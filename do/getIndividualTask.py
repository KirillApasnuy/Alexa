import json
import tts
import requests
import random

def getIndividualTask():
    url = 'http://localhost:5000/alex/individualTask'
    response = requests.get(url)
    data = json.loads(response.text)
    try:
        i = random.randrange(0, len(data))
        data = data[i]
        subject = data['subject']
        topic = data['topic']
        value = data['value']
        if subject != None:
            tts.va_speak(f"Предмет {subject}")
        if topic != None:
            tts.va_speak(f"Тема {topic}")
        if value != None:
            tts.va_speak(f"Вопрос... {value}")
    except:
        tts.va_speak('К сожалению на сегодня заданий нет. не грусти, зайди завтра!')
