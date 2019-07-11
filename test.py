import json

# Для работа с Watson Assistant
import time
import urllib
from threading import Thread

import ibm_watson

from DataPerson import DataPerson
from Keyboards import default_keyboard
import Config

# Для определения ФИО
from natasha import NamesExtractor

# Для взаимодействия с ВК
from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api

# Классификация шаблонов и отправка
from SMTP import send_mail
from PatternDetect import processing, request_processing

import requests


# Отправка сообщений в ВК
def sendMessageToVK(user_id, message, keyboard = ""):
    vk_session.method("messages.send",
                      {"user_id": user_id,
                       "message": message,
                       "random_id": 0,
                       "keyboard": keyboard})

token = Config.TOKEN_VK
vk_session = vk_api.VkApi(token=token)
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)
print("Бот запустился")


api_endpoint = 'https://api.wit.ai/speech'
wit_access_token = ''

def ReadAudio(AUDIO_FILE):
    with open(AUDIO_FILE, 'rb') as f:
        audio = f.read()
        return audio

def RecognizeSpeech(AUDIO_FILE, num_seconds=5):
    audio = ReadAudio(AUDIO_FILE)
    headers = {
        'Accept': 'audio/x-mpeg-3',
        'authorization': 'Bearer ' + wit_access_token,
        'Content-Type': 'audio/mpeg3'}
    resp = requests.post(api_endpoint, headers=headers, data=audio)
    data = json.loads(resp.content)
    text = data['_text']
    return text


while True:
        try:
            messages = vk_session.method("messages.getConversations", {"offset": 0, "count": 200, "filter": "all"})
            print(json.dumps(messages, indent=2))
            break
            if messages['count'] >= 1:
                id = messages['items'][0]['last_message']['from_id']
                try:
                    try:
                        audio_msg = messages["items"][0]["last_message"]["attachments"][0]["audio_message"]["link_mp3"]
                    except:
                        audio_msg = messages["items"][0]["last_message"]["fwd_messages"][0]["attachments"][0]["audio_message"]["link_mp3"]
                    vk_session.method('messages.setActivity', {"user_id": id, 'type': 'typing'})
                    audio = urllib.request.urlretrieve(audio_msg, 'mp.mp3')
                    text = RecognizeSpeech('mp.mp3', 4)
                    if text != '':
                        vk_session.method("messages.send", {"peer_id": id, "message": str(text)})
                    else:
                        vk_session.method("messages.send", {"peer_id": id, "message": "Я не понял тебя!"})
                        continue
                except Exception as Error:
                    vk_session.method("messages.send", {"peer_id": id, "message": "Отправь голосовое сообщение!"})
        except Exception as error:
            time.sleep(1)