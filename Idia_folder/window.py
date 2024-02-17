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
################################################################################
manager = CommandsManager


@manager.new(['(открыть|открой) (окно|окна)', ' подними|поднять) (шторы|роллеты)'])
def windowOpen(params):
    stark.send({
        'target': 'window',
        'cmd':  'window_open',
    })
    voice = text = ''
    return Response(text = text, voice = voice)

################################################################################

@manager.new(['(закрыть|закрой) (окно|окна)', '(опусти|опустить) (шторы|роллеты)'])
def windowClose(params):
    stark.send({
        'target': 'window',
        'cmd':  'window_close',
    })
    voice = text = ''
    return Response(text = text, voice = voice)