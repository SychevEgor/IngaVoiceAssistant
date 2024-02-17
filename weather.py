import json

from stark.core.types import String
from num2words import num2words




import requests
def weather(city:str):
    url = 'https://api.openweathermap.org/data/2.5/weather?q=' + city + '&units=metric&lang=ru&appid=79d1ca96933b0328e1c7e3e7a26cb347'
    weather_data = requests.get(url).json()
    weather_data_structure = json.dumps(weather_data, indent=2)
    temperature = round(weather_data['main']['temp'])
    temperature_feels = round(weather_data['main']['feels_like'])
    sr = num2words(temperature,lang='ru')
    other = num2words(temperature_feels,lang='ru')
    return {'1': String(sr), '2': String(other)}
