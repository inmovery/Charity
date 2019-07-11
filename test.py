import os
import shlex
import urllib

import speech_recognition as sr

import subprocess

# Распознование речи
def RecognizeFile(filename):
    r = sr.Recognizer()
    hard = sr.AudioFile(filename)
    with hard as source:
        audio = r.record((source))
    res = ""
    try:
        res = r.recognize_google(audio, language="ru-RU").lower()
    except sr.UnknownValueError:
        print("Ничего не сказано!")
    return res

oggfile = urllib.request.urlopen("https://psv4.userapi.com/c852420//u135828303/audiomsg/d17/1444b370e9.ogg").read()

with open('message.ogg','wb') as output:
  output.write(oggfile)

command = 'ffmpeg -i message.ogg message.wav'
subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

res = RecognizeFile(os.path.abspath('message.wav'))
print(res)