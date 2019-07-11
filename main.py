import json

# Для работа с Watson Assistant
import os
from threading import Thread

import ibm_watson

import urllib.request

import speech_recognition as sr

import soundfile as sf

import subprocess

import random

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

r = sr.Recognizer()

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

service = ibm_watson.AssistantV2(
        version='2019-02-28',
        url='https://gateway-lon.watsonplatform.net/assistant/api',
        iam_apikey='NGzCvJ0F7EPmWBLBJbD2pdwA5oqkFWtOur-lNJ-9OxGH')

# Инициализация для выяввления ФИО
extractor = NamesExtractor()

# Массив возможных диагнозов
list_diagnoses = ["Иммунодефицит неуточненный", "Дефект в системе комплемента", "Общий вариабельный иммунодефицит",
                  "Избирательный дефицит иммуноглобулина A [IgA]", "Наследственная гипогаммаглобулинемия", "Синдром Вискотта-Олдрича",
                  "Тяжелый комбинированный иммунодефицит", "Другие комбинированные иммунодефициты", "Общий вариабельный иммунодефицит неуточненный",
                  "Синдром Ниймеген", "Синдром Луи-Бар", "Агаммаглобулинемия неуточненная", "ХГБ, аутосомно-рецессивная",
                  "ТКИН неуточненный, синдром Оменн", "Другой вид ПИД"]

# Возведение первой буквы слова в заглавную
def toUpper(temp): return temp[0].upper() + temp[1:]

# Подготовка к выводу параметра "Причина отказа"
def getRejectionReasons(entities):
    prepare = []
    for i in range(len(entities)):
        pre_temp = entities[i]["entity"].split('_')
        temp = ""
        for i in range(len(pre_temp)):
            temp += (pre_temp[i] + " ")
        res = temp[0].upper() + temp[1:]
        prepare.append(res)
    return prepare

# Подсчёт процента совпадения подстроки в строке
def search_partial_text(src, dst):
    dst_buf = dst
    result = 0
    for char in src:
        if char in dst_buf:
            dst_buf = dst_buf.replace(char, '', 1)
            result += 1
    r1 = int(result / len(src) * 100)
    r2 = int(result / len(dst) * 100)
    return '{}'.format(r1 if r1 < r2 else r2)

# temp_url = "https://psv4.userapi.com/c852420//u135828303/audiomsg/d17/1444b370e9.ogg"
#
# oggfile = urllib.request.urlopen(temp_url).read()
#
# rand_t = random.randint(1, 10000)
#
# filen_in = "message"  + str(rand_t) + ".ogg"
# filen_out = "message"  + str(rand_t) + ".wav"
#
# with open('message.ogg','wb') as output:
#     output.write(oggfile)
#
# command = "ffmpeg -i " + 'message.ogg' + " " + 'message.wav'
# subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#
# hard = sr.AudioFile(os.path.abspath('message.wav'))
# with hard as source:
#     audio = r.record((source))
# res = ""
# try:
#     res = r.recognize_google(audio, language="ru-RU").lower()
# except sr.UnknownValueError:
#     print("Ничего не сказано!")

# if path.isfile(path.abspath(filen_in)):
#     remove(path.abspath(filen_in))
# if path.isfile(path.abspath(filen_out)):
#     remove(path.abspath(filen_out))
# print(res)
# response = res

def startBot():
    while True:
        # Даныне пациентов
        data_person = {}

        # Для отслеживания потока пользователей
        unique_users = []

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                response = event.text

                messages = vk_session.method("messages.getConversations", {"offset": 0, "count": 200, "filter": "all"})
                print(len(messages["items"][0]["last_message"]["attachments"]))
                #print(json.dumps(messages, indent=2))
                if(len(messages["items"][0]["last_message"]["attachments"]) >= 1):

                    temp_url = messages["items"][0]["last_message"]["attachments"][0]["audio_message"]["link_ogg"]

                    oggfile = urllib.request.urlopen(temp_url).read()

                    rand_t = random.randint(1, 10000)

                    filen_in = "message" + str(rand_t) + ".ogg"
                    filen_out = "message" + str(rand_t) + ".wav"

                    with open(filen_in, 'wb') as output:
                        output.write(oggfile)

                    command = "ffmpeg -i " + filen_in + " " + filen_out
                    subprocess.run(command, shell=True)

                    hard = sr.AudioFile(os.path.abspath(filen_out))
                    with hard as source:
                        audio = r.record(source)
                    res = ""
                    try:
                        res = r.recognize_google(audio, language="ru-RU").lower()
                    except sr.UnknownValueError:
                        print("Ничего не сказано!")

                    if os.path.isfile(os.path.abspath(filen_out)):
                        os.remove(os.path.abspath(filen_out))

                    print(res)
                    response = res

                    # if os.path.isfile(os.path.abspath(filen_in)):
                    #     os.remove(os.path.abspath(filen_in))

                person = DataPerson("", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", 0, 0, 0, 0, 0, 0, 0,
                                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
                try:
                    if (event.user_id in unique_users):  # Пользователь уже записан
                        person = data_person[str(event.user_id)]
                        unique_users = set(unique_users)
                        unique_users = list(unique_users)
                    else:  # Пользователь ещё не обращался к боту
                        unique_users.append(event.user_id)

                    data_person[str(event.user_id)] = person

                    if event.from_user and not event.from_me:

                        # Создание сессии
                        session = service.create_session(Config.ASSISTANT_ID).get_result()

                        # получение резалта
                        resp = service.message(
                            assistant_id=Config.ASSISTANT_ID,
                            session_id=session['session_id'],
                            input={
                                'message_type': 'text',
                                'text': response
                            }
                        ).get_result()

                        # Удаление сессии
                        service.delete_session(Config.ASSISTANT_ID, session['session_id']).get_result()

                        # Вычисление ФИО пациента или законного представителя
                        matches = extractor(response)
                        spans = [_.span for _ in matches]
                        facts = [_.fact.as_json for _ in matches]

                        intents = ""

                        # начало бизнес-логики
                        if (len(resp["output"]["intents"]) < 1 and len(facts) < 1 and response != "Получение заявления" and
                                response != "вывод" and person.stepForDiagnosis != 1 and person.stepForTgsk != 1 and
                                person.stepForDisability != 1 and person.stepForEmail != 1 and person.stepForMobile != 1 and
                                person.stepForCheckNeed != 1 and person.stepForQuestions != 1 and person.stepForRepresentativeName != 1):
                            sendMessageToVK(event.user_id, "Не балуйтесь! Вводите только запрашиваемые данные!")
                        elif (len(resp["output"]["intents"]) == 1):
                            intents = resp["output"]["intents"][0]["intent"]
                        entities = resp["output"]["entities"]

                        # Вступительная часть
                        if (intents == "приветствие" and response != "Получение заявления"):
                            sendMessageToVK(event.user_id, "Добрый день! Выбери услугу:",
                                            default_keyboard(["Получение заявления", "Проверить заявление"]))
                        elif (response == "вывод"):
                            temp = "Причина: " + person.rejection_reason + "\n" + \
                                   "ФИО пациента: " + person.patient_name + "\n" + \
                                   "ФИО законного представителя: " + person.representative_name + "\n" + \
                                   "Регион: " + person.region + "\n" + \
                                   "Возраст: " + person.age + "\n" + \
                                   "Диагноз: " + person.diagnosis + "\n" + \
                                   "ТГСК была проведена: " + person.tgsk + "\n" + \
                                   "Наличие инвалидности: " + person.disability + "\n" + \
                                   "E-mail: " + person.email + "\n" + \
                                   "Телефон: " + person.mobile + "\n" + \
                                   "Помощь с препаратами от фонда: " + person.help_with_drugs + "\n" + \
                                   "Обращение в больницу по месту жительства: " + person.appeal_hospital + "\n" + \
                                   "Была проведена Врачебная комиссия:" + person.hold_medical_commission + "\n" + \
                                   "Обращение в Минздрав: " + person.ministry_health + "\n" + \
                                   "Обращение в Прокуратуру и Росздравнадзор: " + person.prosecutor + "\n" + \
                                   "Обращение в суд: " + person.court_appeal
                            sendMessageToVK(event.user_id, temp)
                        elif (response == "Получение заявления"):
                            sendMessageToVK(event.user_id,
                                            "Продолжая общение с ботом вы соглашаетесь с обработкой ваших персональных данных.")
                            sendMessageToVK(event.user_id, "По какой причине вам отказали :")
                        else:
                            # если нашлась 1 подходящая причина
                            if (len(entities) == 1 or len(facts) > 0 or intents == "регион" or intents == "возраст" or
                                    person.stepForDiagnosis == 1 or person.stepForRepresentativeName == 1 or person.stepForTgsk == 1 or person.stepForDisability == 1 or
                                    person.stepForEmail == 1 or person.stepForMobile == 1 or person.stepForCheckNeed == 1 or person.stepForQuestions == 1):
                                if (person.stepRejectionReason != 1):
                                    print("Причина")
                                    pre_temp = entities[0]["entity"].split('_')
                                    temp = ""
                                    for i in range(len(pre_temp)):
                                        temp += (pre_temp[i] + " ")
                                    res = toUpper(temp)
                                    person.rejection_reason = res.rstrip()
                                    person.stepRejectionReason = 1  # заполнили причину отказа
                                    sendMessageToVK(event.user_id, "Причина записана! [" + person.rejection_reason + "]")
                                    sendMessageToVK(event.user_id, "Введите ФИО пациента :")
                                elif (person.stepPatientName != 1 and person.stepRejectionReason == 1):
                                    print("ФИО пациента")
                                    if (len(facts[0]) < 3):
                                        person.patient_name = toUpper(facts[0]["last"]) + " " + toUpper(
                                            facts[0]["first"])
                                    else:
                                        person.patient_name = toUpper(facts[0]["last"]) + " " + toUpper(
                                            facts[0]["first"]) + " " + toUpper(facts[0]["middle"])
                                    person.stepPatientName = 1
                                    person.stepForRepresentativeName = 1
                                    sendMessageToVK(event.user_id, "ФИО записаны! [" + person.patient_name + "]")
                                    sendMessageToVK(event.user_id, "Пациент является своим законным представителем ?",
                                                    default_keyboard(["Да, является", "Нет, не является"]))
                                elif (person.stepCheckRepresentativeName != 1 and person.stepPatientName == 1):

                                    print("Проверка ФИО законного представителя")
                                    if (response == "Да, является"):
                                        person.representative_name = ""
                                        person.stepCheckRepresentativeName = 1
                                        person.stepRepresentativeName = 1
                                        sendMessageToVK(event.user_id,
                                                        "Введите регион (республика, край, область, округ), в котором вы проживаете :")
                                    elif (response == "Нет, не является"):
                                        person.stepCheckRepresentativeName = 1
                                        sendMessageToVK(event.user_id, "Введите ФИО законного представителя :")
                                elif (person.stepRepresentativeName != 1 and person.stepCheckRepresentativeName == 1):
                                    if (len(facts[0]) < 3):
                                        person.representative_name = toUpper(facts[0]["last"]) + " " + toUpper(
                                            facts[0]["first"])
                                    else:
                                        person.representative_name = toUpper(facts[0]["last"]) + " " + toUpper(
                                            facts[0]["first"]) + " " + toUpper(facts[0]["middle"])
                                    person.stepRepresentativeName = 1
                                    sendMessageToVK(event.user_id, "ФИО записаны! [" + person.representative_name + "]")
                                    sendMessageToVK(event.user_id,
                                                    "Введите регион (республика, край, область, округ), в котором вы проживаете:")
                                elif (person.stepRegion != 1 and person.stepRepresentativeName == 1):
                                    print("Регион")
                                    if (intents == "регион"):
                                        person.stepRegion = 1
                                        person.region = response
                                        sendMessageToVK(event.user_id, "Регион записан! [" + person.region + "]")
                                        sendMessageToVK(event.user_id, "Введите возраст пациента :")
                                elif (person.stepAge != 1 and person.stepRegion == 1):
                                    print("Возраст")
                                    if (intents == "возраст"):
                                        person.stepForDiagnosis = 1
                                        person.stepAge = 1
                                        for_res = ""
                                        for j in range(len(response)):
                                            if (response[j].isdigit()):
                                                for_res += response[j]
                                        person.age = for_res
                                        sendMessageToVK(event.user_id, "Возраст записан! [" + person.age + "]")
                                        sendMessageToVK(event.user_id, "Введите дианоз пациента :")
                                elif (person.stepDiagnosis != 1 and person.stepAge == 1):
                                    print("Диагноз")
                                    one = ""
                                    two = ""
                                    temp_for = {}
                                    ok = False
                                    # если выбран 100% правильный диагноз
                                    for j in range(len(list_diagnoses)):
                                        if (int(search_partial_text(response.lower(),
                                                                    list_diagnoses[j].lower())) == 100):
                                            ok = True
                                            break
                                    if (ok):
                                        person.stepForTgsk = 1
                                        person.stepDiagnosis = 1
                                        person.diagnosis = response
                                        sendMessageToVK(event.user_id, "Диагноз записан! [" + person.diagnosis + "]")
                                        sendMessageToVK(event.user_id,
                                                        "У пациента была проведена ТГСК (Трансплантация гемопоэтических стволовых клеток) :",
                                                        default_keyboard(["Нет, ТГСК не была проведена",
                                                                          "Да, ТГСК была проведена"]))
                                    else:
                                        for j in range(len(list_diagnoses)):
                                            if (int(search_partial_text(response.lower(),
                                                                        list_diagnoses[j].lower())) < 100):
                                                temp_for[str(list_diagnoses[j])] = int(
                                                    search_partial_text(response.lower(), list_diagnoses[j].lower()))
                                        list_temp_for = list(temp_for.items())
                                        list_temp_for.sort(key=lambda i: i[1])
                                        d = 0
                                        for j in list_temp_for:
                                            # print(str(j[0]) + " : " + str(j[1]))
                                            d = d + 1
                                            if (d == 14):
                                                two = j[0]
                                            elif (d == 15):
                                                one = j[0]
                                        prepare = [one, two]
                                        sendMessageToVK(event.user_id, "Возможно вы имели ввиду :",
                                                        default_keyboard(prepare))
                                elif (person.stepTgsk != 1 and person.stepDiagnosis == 1):
                                    print("ТГСК")
                                    if (response == "Нет, ТГСК не была проведена"):
                                        person.stepTgsk = 1
                                        person.tgsk = "Нет"
                                        if (person.rejection_reason == "Отсутствие инвалидности"):
                                            person.stepDisability = 1
                                            person.disability = "Нет"
                                            sendMessageToVK(event.user_id,
                                                            "Перечислите препараты, прописанные пациенту через запятую :")
                                        else:
                                            sendMessageToVK(event.user_id, "У пациента есть инвалидность ?",
                                                            default_keyboard(["Да, инвалидность есть",
                                                                              "Инвалидность отсутствует"]))
                                    elif (response == "Да, ТГСК была проведена"):
                                        person.stepForDisability = 1
                                        person.stepTgsk = 1
                                        person.tgsk = "Да"
                                        if (person.rejection_reason == "Отсутствие инвалидности"):
                                            person.stepDisability = 1
                                            person.disability = "Нет"
                                            sendMessageToVK(event.user_id,
                                                            "Перечислите препараты, прописанные пациенту через запятую :")
                                        else:
                                            sendMessageToVK(event.user_id, "У пациента есть инвалидность ?",
                                                            default_keyboard(["Да, инвалидность есть",
                                                                              "Инвалидность отсутствует"]))
                                elif (person.stepDisability != 1 and person.stepTgsk == 1):
                                    print("Инвалидность")
                                    if (response == "Да, инвалидность есть"):
                                        person.stepDisability = 1
                                        person.disability = "Да"
                                        sendMessageToVK(event.user_id,
                                                        "Перечислите препараты, прописанные пациенту через запятую :")
                                    elif (response == "Инвалидность отсутствует"):
                                        person.stepDisability = 1
                                        person.disability = "Нет"
                                        sendMessageToVK(event.user_id,
                                                        "Перечислите препараты, прописанные пациенту через запятую :")
                                elif (person.stepDrugs != 1 and person.stepDisability == 1):
                                    print("Препараты")
                                    res = response.split(',')
                                    for j in range(len(res)):
                                        person.drugs += res[j].strip()
                                    person.stepDrugs = 1
                                    person.stepForEmail = 1
                                    sendMessageToVK(event.user_id, "Введите контактный E-mail :")
                                elif (person.stepEmail != 1 and person.stepDrugs == 1):
                                    print("Email")
                                    person.email = response
                                    person.stepEmail = 1
                                    person.stepForMobile = 1
                                    sendMessageToVK(event.user_id, "Введите контактный телефон :")
                                elif (person.stepMobile != 1 and person.stepEmail == 1):
                                    print("Телефон")
                                    person.mobile = response
                                    person.stepMobile = 1
                                    person.stepForCheckNeed = 1
                                    sendMessageToVK(event.user_id, "Нужна помощь с препаратами от фонда ?",
                                                    default_keyboard(["Да, помощь с препаратами нужна",
                                                                      "Нет, помощь с препаратами не нужна"]))
                                elif (person.stepHelpWithDrugs != 1 and person.stepMobile == 1):
                                    if (response == "Да, помощь с препаратами нужна"):
                                        person.help_with_drugs = "Да"
                                        person.stepHelpWithDrugs = 1
                                        person.stepForQuestions = 1
                                        sendMessageToVK(event.user_id, "Вы обращались в больницу по месту жительства ?",
                                                        default_keyboard(["Да, в больницу обращался(лась)",
                                                                          "Нет, в больницу не обращался(лась)"]))
                                    elif (response == "Нет, помощь с препаратами не нужна"):
                                        person.help_with_drugs = "Нет"
                                        person.stepHelpWithDrugs = 1
                                        person.stepForQuestions = 1
                                        sendMessageToVK(event.user_id, "Обращались ли вы в больницу по месту жительства ?",
                                                        default_keyboard(["Да, в больницу обращался(лась)",
                                                                          "Нет, в больницу не обращался(лась)"]))
                                elif (person.stepAppealHospital != 1 and person.stepHelpWithDrugs == 1):
                                    if (response == "Да, в больницу обращался(лась)"):
                                        person.appeal_hospital = "Да"
                                        person.stepAppealHospital = 1
                                        sendMessageToVK(event.user_id, "Была проведена врачебная комиссия ?",
                                                        default_keyboard(["Да, была проведена", "Нет, не была проведена"]))
                                    elif (response == "Нет, в больницу не обращался(лась)"):
                                        person.appeal_hospital = "Нет"
                                        person.stepAppealHospital = 1
                                        sendMessageToVK(event.user_id, "Была проведена врачебная комиссия ?",
                                                        default_keyboard(["Да, была проведена", "Нет, не была проведена"]))
                                elif (person.stepHoldMedicalCommission != 1 and person.stepHelpWithDrugs == 1):
                                    if (response == "Да, была проведена"):
                                        person.hold_medical_commission = "Да"
                                        person.stepHoldMedicalCommission = 1
                                        sendMessageToVK(event.user_id,
                                                        "Вы обращались в орган исполнительной власти в сфере здравоохранения (Минздрав) ?",
                                                        default_keyboard(["Да, в Минздрав обращался(лась)",
                                                                          "Нет, в Минздрав не обращался(лась)"]))
                                    elif (response == "Нет, не была проведена"):
                                        person.hold_medical_commission = "Нет"
                                        person.stepHoldMedicalCommission = 1
                                        sendMessageToVK(event.user_id,
                                                        "Вы обращались в орган исполнительной власти в сфере здравоохранения (Минздрав) ?",
                                                        default_keyboard(["Да, в Минздрав обращался(лась)",
                                                                          "Нет, в Минздрав не обращался(лась)"]))
                                elif (person.stepMinistryHealth != 1 and person.stepHoldMedicalCommission == 1):
                                    if (response == "Да, в Минздрав обращался(лась)"):
                                        person.ministry_health = "Да"
                                        person.stepMinistryHealth = 1
                                        sendMessageToVK(event.user_id,
                                                        "Вы обращались в контроллирующие органы государственной власти (Прокуратуру и Росздравнадзор) ?",
                                                        default_keyboard(["Да, в Прокуратуру", "Да, в Росздравнадзор",
                                                                          "Нет, я никуда не обращался"]))
                                    elif (response == "Нет, в Минздрав не обращался(лась)"):
                                        person.ministry_health = "Нет"
                                        person.stepMinistryHealth = 1
                                        sendMessageToVK(event.user_id,
                                                        "Вы обращались в контроллирующие органы государственной власти (Прокуратуру и Росздравнадзор) ?",
                                                        default_keyboard(["Да, в Прокуратуру", "Да, в Росздравнадзор",
                                                                          "Нет, я никуда не обращался"]))
                                elif (person.stepProsecutor != 1 and person.stepMinistryHealth == 1):
                                    if (response == "Да, в Прокуратуру"):
                                        person.prosecutor = "Да"
                                        person.stepProsecutor = 1
                                        sendMessageToVK(event.user_id, "Вы обращались в суд ?",
                                                        default_keyboard(["Да, я обращался(лась) в суд",
                                                                          "Нет, я не обращался(лась) в суд"]))
                                    elif (response == "Да, в Росздравнадзор"):
                                        person.prosecutor = "Да"
                                        person.stepProsecutor = 1
                                        sendMessageToVK(event.user_id, "Вы обращались в суд ?",
                                                        default_keyboard(["Да, я обращался(лась) в суд",
                                                                          "Нет, я не обращался(лась) в суд"]))
                                    elif (response == "Нет, я никуда не обращался"):
                                        person.prosecutor = "Нет"
                                        person.stepProsecutor = 1
                                        sendMessageToVK(event.user_id, "Вы обращались в суд ?",
                                                        default_keyboard(["Да, я обращался(лась) в суд",
                                                                          "Нет, я не обращался(лась) в суд"]))
                                elif (person.stepCourtAppeal != 1 and person.stepProsecutor == 1):
                                    if (response == "Да, я обращался(лась) в суд"):
                                        person.court_appeal = "Да"
                                        person.stepCourtAppeal = 1
                                        # patient_name, representative_name, region, mobile, diagnosis, drugs,
                                        # rejection_reason, age, tgsk, disability, appeal_hospital, hold_medical_commission, ministry_health):

                                        if (person.rejection_reason == "Другое"):
                                            print()
                                            # тут отправка сообщения оператору НКО
                                        else:
                                            temp_for_reason = ["Препарата нет в продаже", "Нет инструкции",
                                                               "Отсутствие инвалидности",
                                                               "Не является необходимым для жизни",
                                                               "Вместо льгот деньги", "Нарушение прав"]
                                            res_reason = ""
                                            for j in range(len(temp_for_reason)):
                                                if (temp_for_reason[j] == person.rejection_reason):
                                                    res_reason = j + 1
                                                    break
                                            data = {}
                                            data['representative_name'] = person.representative_name
                                            data['patient_name'] = person.patient_name
                                            data['address'] = person.region
                                            data['illness'] = person.diagnosis
                                            data['medicine'] = person.drugs
                                            data['telephone'] = person.mobile
                                            data['reason'] = res_reason
                                            data['if_tgsk'] = person.tgsk.lower() == 'да'
                                            data['if_invalid'] = person.disability.lower() == 'да'
                                            data['if_hospital'] = person.appeal_hospital.lower() == 'да'
                                            data['if_comission'] = person.hold_medical_commission.lower() == 'да'
                                            data['if_minzdrav'] = person.ministry_health.lower() == 'да'
                                            data['if_older_3'] = int(person.age) >= 3

                                            doc = request_processing(data)
                                            send_mail(person.email, doc)

                                        sendMessageToVK(event.user_id,
                                                        "Заявка на получение заявления успешно обработана.\nЗаявление с инструкцией отправлены на указанный E-mail: " + person.email + "\nСпасибо за обращение!")
                                    elif (response == "Нет, я не обращался(лась) в суд"):
                                        person.court_appeal = "Нет"
                                        person.stepCourtAppeal = 1

                                        if (person.rejection_reason == "Другое"):
                                            print()
                                            # тут отправка сообщения оператору НКО
                                        else:
                                            temp_for_reason = ["Препарата нет в продаже", "Нет инструкции",
                                                               "Отсутствие инвалидности",
                                                               "Не является необходимым для жизни",
                                                               "Вместо льгот деньги", "Нарушение прав"]
                                            res_reason = ""
                                            for j in range(len(temp_for_reason)):
                                                if (temp_for_reason[j] == person.rejection_reason):
                                                    res_reason = j + 1
                                                    break
                                            data = {}
                                            data['representative_name'] = person.representative_name
                                            data['patient_name'] = person.patient_name
                                            data['address'] = person.region
                                            data['illness'] = person.diagnosis
                                            data['medicine'] = person.drugs
                                            data['telephone'] = person.mobile
                                            data['reason'] = res_reason
                                            data['if_tgsk'] = person.tgsk.lower() == 'да'
                                            data['if_invalid'] = person.disability.lower() == 'да'
                                            data['if_hospital'] = person.appeal_hospital.lower() == 'да'
                                            data['if_comission'] = person.hold_medical_commission.lower() == 'да'
                                            data['if_minzdrav'] = person.ministry_health.lower() == 'да'
                                            data['if_older_3'] = int(person.age) >= 3

                                            doc = request_processing(data)
                                            send_mail(person.email, doc)
                                            sendMessageToVK(event.user_id,
                                                        "Заявка на получение заявления успешно обработана.\nЗаявление с инструкцией отправлены на указанный E-mail: " + person.email + "\nСпасибо за обращение!")
                            elif ((intents == "причина_отказа" and len(entities) < 1) or (intents == "" and person.stepRejectionReason != 1 and person.stepPatientName != 1 and person.stepRepresentativeName != 1 and person.stepRegion != 1 and
                                person.stepAge != 1 and person.stepDiagnosis != 1 and person.stepDisability != 1 and person.stepTgsk != 1 and
                                person.stepDrugs != 1 and person.stepEmail != 1 and person.stepMobile != 1 and person.stepHelpWithDrugs != 1 and
                                person.stepAppealHospital != 1 and person.stepCourtAppeal != 1 and person.stepHoldMedicalCommission != 1 and
                                person.stepMinistryHealth != 1 and person.stepProsecutor != 1)):
                                sendMessageToVK(event.user_id, "Ваша причина относится к категории \"Другое\". После заполнения заявления с вами свяжется специалист.")

                                person.rejection_reason = "Другое"
                                person.stepRejectionReason = 1  # заполнили причину отказа
                                sendMessageToVK(event.user_id, "Причина записана! [" + person.rejection_reason + "]")
                                sendMessageToVK(event.user_id, "Введите ФИО пациента :")
                            # если пользователь ввёл что-то не то, что нужно
                            elif (len(entities) < 1 and person.stepForDiagnosis == 0 and person.stepForTgsk == 0 and person.stepForDisability == 0 and person.stepForEmail == 0 and
                                person.stepForMobile == 0 and person.stepForRepresentativeName == 0 and person.stepForCheckNeed == 0 and person.stepForCheckNeed == 0):
                                sendMessageToVK(event.user_id, "Привет! Выбери услугу :", default_keyboard(["Получение заявления", "Проверить заявление"]))
                            elif (len(entities) > 1):
                                prepare = getRejectionReasons(entities)
                                sendMessageToVK(event.user_id, "Уточните, что вы имели ввиду :", default_keyboard(prepare))
                except ibm_watson.ApiException:
                    print("500 Error IBM Cloud")
                    sendMessageToVK(event.user_id, "Произошла ошибка! Введите то же самое.")

startBot()
