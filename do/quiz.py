import json
import random
import tts
import requests
url = 'http://localhost:5000/alex/quiz'
response = requests.get(url)
data = json.loads(response.text)
print(data)

def startQuiz():
    try:
        global data
        i = random.randrange(0, len(data))
        data = data[i]
        if data['subject'] != None:
            tts.va_speak(f'На повестке дня {data["subject"]}')
        if data['topic'] != None:
            tts.va_speak(f'Тема на сегодня {data["topic"]}')
        if data['value'] != None:
            tts.va_speak(f'Внимание вопрос... {data["value"]}')
            tts.va_speak('Если хочешь проверить свой ответ, сделай это в моём приложении')
    except:
        tts.va_speak('Как жаль... на сегодня викторины нет, приходи завтра!')
# print(startQuiz())
