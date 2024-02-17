import anyio
import webbrowser
import asyncer
import time
from num2words import num2words

import ya_musik
from weather import weather
from stark.voice_assistant import VoiceAssistant, Mode
from stark.interfaces.protocols import SpeechRecognizer, SpeechSynthesizer
from stark import CommandsManager, Response, CommandsContext
from stark.interfaces.vosk import VoskSpeechRecognizer
from stark.interfaces.silero import SileroSpeechSynthesizer
from stark.core.types import String, Word
from stark.general.blockage_detector import BlockageDetector
from stark.core import ResponseHandler
from stark_place.triggers import porcupine
from stark_place.notifications import sound

VOSK_MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-ru-0.42.zip"
SILERO_MODEL_URL = "https://models.silero.ai/models/tts/ru/v4_ru.pt"

ACCSESS_KEY = 'ntJQ97QXMbrY+r50ZOd8zxxZdDRhRE5/v5hkCaPO60fAn9I9V8xXBw=='
KEYWORD_PATCH = ['downloads/эй-инга_ru_windows_v3_0_0.ppn']
MODEL_PATCH = 'downloads/porcupine_params_ru.pv'

recognizer = VoskSpeechRecognizer(model_url=VOSK_MODEL_URL)
synthesizer = SileroSpeechSynthesizer(model_url=SILERO_MODEL_URL, torch_backends_quantized_engine="onednn")

manager = CommandsManager()


@manager.new(r'(включай любимые песни|включай музыку|дискотека)')
async def play_music() -> Response:
    voice = text = 'Хорошо включаю ваши любимые песни'
    recognizer.stop_listening()
    ya_musik.play()
    return Response(text=text, voice=voice)


@manager.new(r'(пропусти|следующую|дальше)')
async def skipping() -> Response:
    voice = text = 'включаю следующий трек'
    recognizer.stop_listening()
    ya_musik.skip()
    return Response(text=text, voice=voice)


@manager.new(r'(стоп|молчи|хватит)')
async def music_stop() -> Response:
    voice = text = 'Хорошо, послушаем в другой раз'
    ya_musik.stop()
    return Response(text=text, voice=voice)


@manager.new(r'(погода|какая погода|температура) $weathers:String')
async def weather_now(weathers: String) -> Response:
    now = weather(weathers.value)
    realy_temp = now.get('1')
    feel_temp = now.get('2')
    voice = text = f'сейчас в {weathers} температура {realy_temp} градусов. по ощущению {feel_temp} '
    return Response(text=text, voice=voice)


@manager.new(r'(сколько времени|который час|сколько сейчас времени)')
def time_now() -> Response:
    hour = time.strftime('%H')
    hour = Word(num2words(hour, lang='ru'))
    minutes = time.strftime('%M')
    minutes = Word(num2words(minutes, lang='ru'))
    voice = text = f'сейчас {hour} часов и {minutes} минут    '
    return Response(text=text, voice=voice)


@manager.new('привет')
def hello_context(**params):
    text = voice = f'прив+ет {params["name"]}'
    return Response(text=text, voice=voice)


@manager.new('пока', hidden=True)
def bye_context(name: Word, handler: ResponseHandler):
    handler.pop_context()
    return Response(text=f'пока {name}')


@manager.new(r'(привет|как дела) name:Word')
def hello(name: Word):
    text = voice = f'привет {name}'
    return Response(
        text=text,
        voice=voice,
        commands=[hello_context, bye_context],
        parameters={'name': name}
    )


@manager.new(r'(найди|что такое|как называется) $queue:String')
def search_in_google(queue: String) -> Response:
    voice = text = f'по запросу {queue} найдены следущие реультаты/!'
    url = f"https://www.google.com/search?q={queue}"
    webbrowser.open(url)
    return Response(text=text, voice=voice)


@manager.new(r'(включи|открой|видео) $queuer:String')
def search_in_youtube(queuer: String) -> Response:
    voice = text = f'вот что есть на ютубе по запросу {queuer}'
    url = f"https://www.youtube.com/results?search_query={queuer}"
    webbrowser.open(url)
    return Response(text=text, voice=voice)


async def run(
        managers: CommandsManager,
        speech_recognizer: SpeechRecognizer,
        speech_synthesizer: SpeechSynthesizer
):
    async with asyncer.create_task_group() as main_task_group:
        context = CommandsContext(
            task_group=main_task_group,
            commands_manager=managers
        )
        voice_assistant = VoiceAssistant(
            speech_recognizer=speech_recognizer,
            speech_synthesizer=speech_synthesizer,
            commands_context=context
        )
        speech_recognizer.delegate = voice_assistant
        context.delegate = voice_assistant

        voice_assistant.mode = Mode.external()

        def add_porcupine_listener():
            def on_wake_word():
                sound.play()
                main_task_group.soonify(start_speech_recognizer)()

            main_task_group.soonify(porcupine.start)(
                access_key=ACCSESS_KEY,
                keyword_paths=KEYWORD_PATCH,
                model_path=MODEL_PATCH,
                callback=on_wake_word
            )

        async def start_speech_recognizer():
            await speech_recognizer.start_listening()
            add_porcupine_listener()

        add_porcupine_listener()

        main_task_group.soonify(context.handle_responses)()

        detector = BlockageDetector()
        main_task_group.soonify(detector.monitor)()


async def main():
    await run(manager, recognizer, synthesizer)


if __name__ == '__main__':
    anyio.run(main)
