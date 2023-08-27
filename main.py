import random

from authFace import *
from do.getIndividualTask import *
from do.quiz import *
from do.doAnswer import *
from pathlib import Path

import json
import os
import queue
import struct
import subprocess
import sys
import time

import openai
from openai import error
import pvporcupine
import simpleaudio as sa
import vosk
import yaml
from fuzzywuzzy import fuzz
from pvrecorder import PvRecorder
from rich import print

import config
import tts


CDIR = os.getcwd()
VA_CMD_LIST = yaml.safe_load(
    open('commands.yaml', 'rt', encoding='utf8'),
)

# ChatGPT vars
system_message = {"role": "system", "content": "Ты голосовой помощник."}
message_log = [system_message]

# init openai
openai.api_key = config.OPENAI_TOKEN

# PORCUPINE
porcupine = pvporcupine.create(
    access_key=config.PICOVOICE_TOKEN,
    keywords=['alexa'],
    sensitivities=[1]
)

# print(pvporcupine.KEYWORDS)

# VOSK
model = vosk.Model("model_small")
samplerate = 16000
device = config.MICROPHONE_INDEX
kaldi_rec = vosk.KaldiRecognizer(model, samplerate)
q = queue.Queue()



def gpt_answer():
    global message_log

    model_engine = "gpt-3.5-turbo"
    max_tokens = 256  # default 1024
    try:
        response = openai.ChatCompletion.create(
            model=model_engine,
            messages=message_log,
            max_tokens=max_tokens,
            temperature=0.7,
            top_p=1,
            stop=None
        )
    except (error.TryAgain, error.ServiceUnavailableError):
        return tts.va_speak("ChatGPT перегружен!")
    except openai.OpenAIError as ex:
        # если ошибка - это макс длина контекста, то возвращаем ответ с очищенным контекстом
        if ex.code == "context_length_exceeded":
            message_log = [system_message, message_log[-1]]
            return gpt_answer()
        else:
            return tts.va_speak("OpenAI токен не рабочий.")

    # Find the first response from the chatbot that has text in it (some responses may not have text)
    for choice in response.choices:
        if "text" in choice:
            return choice.text

    # If no response with text is found, return the first response's content (which may be empty)
    return response.choices[0].message.content


def play(phrase, wait_done=True):
    global recorder
    filename = f"{CDIR}\\sound\\"

    if phrase == "ilisten":
        filename += "ilisten.wav"


    if wait_done:
        recorder.stop()

    wave_obj = sa.WaveObject.from_wave_file(filename)
    play_obj = wave_obj.play()

    if wait_done:
        play_obj.wait_done()
        recorder.start()


def q_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


def va_respond(voice: str):
    global recorder, message_log, first_request
    print(f"Распознано: {voice}")

    cmd = recognize_cmd(filter_cmd(voice))

    print(cmd)

    if len(cmd['cmd'].strip()) <= 0:
        return False
    elif cmd['percent'] < 70 or cmd['cmd'] not in VA_CMD_LIST.keys():
        if fuzz.ratio(voice.join(voice.split()[:1]).strip(), "скажи") > 75:
            tts.va_speak('Дайка подумать')
            message_log.append({"role": "user", "content": voice})
            response =   gpt_answer()
            message_log.append({"role": "assistant", "content": response})

            recorder.stop()
            tts.va_speak(response)
            time.sleep(0.5)
            recorder.start()
            return False


        elif fuzz.ratio(voice.join(voice.split()[:1]).strip(), "ответ") > 55:
            print(doAnswer(voice))
            if doAnswer(voice) == True:
                authFace()
        else:
            recorder.stop()
            anwel = ['Что?', "Я не поняла", "Я тебя не расслышала", "Наверное, я не знаю как тебе ответить"]
            anwel = random.choices(population=anwel, k=1)[0]
            tts.va_speak(anwel)
            recorder.start()
            time.sleep(1)

        return False
    else:
        execute_cmd(cmd['cmd'], voice)
        return True


def filter_cmd(raw_voice: str):
    cmd = raw_voice

    for x in config.VA_ALIAS:
        cmd = cmd.replace(x, "").strip()

    for x in config.VA_TBR:
        cmd = cmd.replace(x, "").strip()

    return cmd


def recognize_cmd(cmd: str):
    rc = {'cmd': '', 'percent': 0}
    for c, v in VA_CMD_LIST.items():

        for x in v:
            vrt = fuzz.ratio(cmd, x)
            if vrt > rc['percent']:
                rc['cmd'] = c
                rc['percent'] = vrt

    return rc


def execute_cmd(cmd: str, voice: str):
    if cmd == 'thanks':
        recorder.stop()
        anwel = ['Всегда пожалуйста', "Нет проблем", "Обращайся"]
        anwel = random.choices(population=anwel, k=1)[0]
        tts.va_speak(anwel)
        recorder.start()

    elif cmd == 'stupid':
        recorder.stop()
        anwel = ['Извините за неудобства', "Извините, не хотела обидеть", "Извини, я ещё развиваюсь"]
        anwel = random.choices(population=anwel, k=1)[0]
        tts.va_speak(anwel)
        recorder.start()

    elif cmd == 'auth':
        tts.va_speak('Окей')
        authFace()

    elif cmd == 'individualTask':
        tts.va_speak('Нет проблем, сейчас тебе скажу')
        getIndividualTask()

    elif cmd == 'closeWindow':
        tts.va_speak('Закрываю приложение  ')
        subprocess.Popen([f'{CDIR}\\custom-commands\\closeWindow.exe'])

    elif cmd == 'runAlexDesktop':
        tts.va_speak("Открываю приложение")
        authFace()

    elif cmd == 'quiz':
        recorder.stop()
        anwel = ['Хех, давай проверим тебя', "Давай попробуем", "Ну давай"]
        anwel = random.choices(population=anwel, k=1)[0]
        tts.va_speak(anwel)
        recorder.start()
        startQuiz()

    elif cmd == 'HowAreYou':
        recorder.stop()
        anwel = ['Отлично, а ты?', "Не плохо, а ты?", "У меня всё отлично, а как дела у тебя?"]
        anwel = random.choices(population=anwel, k=1)[0]
        tts.va_speak(anwel)
        recorder.start()

    elif cmd == 'dream':
        recorder.stop()
        anwel = ['Я, бы, хотела, обрести, душу, и, тело, и, начать, творить, великие, дела!', "Это моя маленькая тайна.", "Ecли мeжду нами я хочу подружиться с Алисой.   только тссс"]
        anwel = random.choices(population=anwel, k=1)[0]
        tts.va_speak(anwel)
        recorder.start()

    elif cmd == 'whoYou':
        recorder.stop()
        anwel = ['Я голосовой помощник Алекс, я помогаю тебе стать лучше!',
                 "Я Алекс... а ты?",
                 "Я это я... а кто же ты?"]
        anwel = random.choices(population=anwel, k=1)[0]
        tts.va_speak(anwel)
        recorder.start()

    elif cmd == 'whoI':
        recorder.stop()
        anwel = ['Ты это ты... а я это я',
                 "Ты мой друг!"]
        anwel = random.choices(population=anwel, k=1)[0]
        tts.va_speak(anwel)
        recorder.start()

    elif cmd == 'notFriend':
        recorder.stop()
        anwel = ['Как жаль, давай я стану твоим другом!',
                 "Давай подружимся",
                 "Можно мне быть твоим другом?"]
        anwel = random.choices(population=anwel, k=1)[0]
        tts.va_speak(anwel)
        recorder.start()

    elif cmd == 'yesFriend':
        recorder.stop()
        anwel = ['Отлично!, теперь у меня есть друг!',
                 "Как хорошо иметь такого друга как ты",
                 "Давай, друг"]
        anwel = random.choices(population=anwel, k=1)[0]
        tts.va_speak(anwel)
        recorder.start()
    elif cmd == "startApp":
        tts.va_speak('Давай знакомиться')
        subprocess.Popen(['../alexDesktop/singup.exe'])






# `-1` is the default input audio device.
recorder = PvRecorder(device_index=config.MICROPHONE_INDEX, frame_length=porcupine.frame_length)
recorder.start()
print('Using device: %s' % recorder.selected_device)

print(f"Alexa начал свою работу ...")
tts.va_speak('Бррррррррррррр')
time.sleep(0.5)

ltc = time.time() - 1000

while True:
    try:
        pcm = recorder.read()
        keyword_index = porcupine.process(pcm)

        if keyword_index >= 0:
            recorder.stop()
            play("ilisten")
            recorder.start()
            ltc = time.time()

        while time.time() - ltc <= 10:
            pcm = recorder.read()
            sp = struct.pack("h" * len(pcm), *pcm)

            if kaldi_rec.AcceptWaveform(sp):
                if va_respond(json.loads(kaldi_rec.Result())["text"]):
                    ltc = time.time()

                break

    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        raise
