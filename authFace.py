import cv2
import face_recognition
import subprocess
import tts
import pickle
from pathlib import Path
import numpy as np
import os
CDIR = os.getcwd()
tts.va_speak('Начинаю просыпаться')

app = Path('../alexDesktop/app.exe')
path = Path('../alexDesktop/dataset_from_cam')
imges = []
classname = []
myList = os.listdir(path)

for cls in myList:
    curimg = cv2.imread(f'{path}/{cls}')
    imges.append(curimg)
    classname.append(os.path.splitext(cls)[0])

print(classname)

def findEncodings(images):
    tts.va_speak('Вспоминаю лица')
    encodeList = []


    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

encodeListKnow = findEncodings(imges)
tts.va_speak('Вспомнила!')
def authFace():
    tts.va_speak('Посмотри в камеру и улыбнись')
    cam = cv2.VideoCapture(0)

    while True:
        success, img = cam.read()
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
        facesCurFrame = face_recognition.face_locations(imgS)
        encodeCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

        for encodeFace, faceLoc in zip(encodeCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(encodeListKnow, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnow, encodeFace)
            print(faceDis)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:

                name = classname[matchIndex]
                print(name)
                tts.va_speak(f'оу, прекрасно выглядишь, запускаю приложение!')


                with open('../name.pickle', 'wb') as file:
                    pickle.dump(name, file)
                    subprocess.Popen([f'{CDIR}\\custom-commands\\runAlexDesktop.exe'])
                    return