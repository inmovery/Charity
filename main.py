import json
import os

import ibm_watson

from natasha import NamesExtractor

from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import vk_api

import clf
import start


#инициализация для выяввления ФИО
extractor = NamesExtractor()

class DataPerson:

    def __init__(self, mRejectionReason, mPatientName, mRegion, mAge, mDiagnosis, mTgsk, mDisability, mDrugs, mEmail, mMobile, mHelpWithDrugs, mAppealHospital, mHoldMedicalCommission, mMinistryHealth, mProsecutor, mCourtAppeal, mRepresentativeName,
                 mStepRejectionReason, mStepPatientName, mStepRepresentativeName, mStepRegion, mStepAge, mStepDiagnosis, mStepTgsk, mStepDisability, mStepDrugs, mStepEmail, mStepMobile, mStepHelpWithDrugs, mStepAppealHospital, mStepHoldMedicalCommission,
                 mStepMinistryHealth, mStepProsecutor, mStepCourtAppeal, mStepForCheckNeed, mStepForQuestions, mStepForMobile, mStepForEmail, mStepForDisability, mStepForTgsk, mStepForDiagnosis, mStepCheckRepresentativeName, mStepForRepresentativeName):

        # основные поля пользователя
        self.rejection_reason = mRejectionReason
        self.patient_name = mPatientName
        self.representative_name = mRepresentativeName
        self.region = mRegion
        self.age = mAge
        self.diagnosis = mDiagnosis
        self.tgsk = mTgsk
        self.disability = mDisability
        self.drugs = mDrugs
        self.email = mEmail
        self.mobile = mMobile
        self.help_with_drugs = mHelpWithDrugs

        # проверка законного представителя
        self.stepCheckRepresentativeName = mStepCheckRepresentativeName

        # отслежвание передвижений пользователей по дефолтным вопросам
        self.stepRejectionReason = mStepRejectionReason
        self.stepPatientName = mStepPatientName
        self.stepRepresentativeName = mStepRepresentativeName
        self.stepRegion = mStepRegion
        self.stepAge = mStepAge
        self.stepDiagnosis = mStepDiagnosis
        self.stepTgsk = mStepTgsk
        self.stepDisability = mStepDisability
        self.stepDrugs = mStepDrugs
        self.stepEmail = mStepEmail
        self.stepMobile = mStepMobile
        self.stepHelpWithDrugs = mStepHelpWithDrugs

        # вопросы по обращениям
        self.appeal_hospital = mAppealHospital
        self.hold_medical_commission = mHoldMedicalCommission
        self.ministry_health = mMinistryHealth
        self.prosecutor = mProsecutor
        self.court_appeal = mCourtAppeal

        self.stepAppealHospital = mStepAppealHospital
        self.stepHoldMedicalCommission = mStepHoldMedicalCommission
        self.stepMinistryHealth = mStepMinistryHealth
        self.stepProsecutor = mStepProsecutor
        self.stepCourtAppeal = mStepCourtAppeal

        self.stepForCheckNeed = mStepForCheckNeed
        self.stepForQuestions = mStepForQuestions
        self.stepForMobile = mStepForMobile
        self.stepForEmail = mStepForEmail
        self.stepForDisability = mStepForDisability
        self.stepForTgsk = mStepForTgsk
        self.stepForDiagnosis = mStepForDiagnosis

        self.stepForRepresentativeName = mStepForRepresentativeName

# авторизация ВК
token = "445fb94adce5f5d33d8b4adf1bdcd3000b322e8d830404f58b361c183e1012badb3738d9386852d88468d"
vk_session = vk_api.VkApi(token=token)
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

print("Бот запустился")

# инициализация Watson Assistant
service = ibm_watson.AssistantV2(
        version='2019-02-28',
        url='https://gateway-lon.watsonplatform.net/assistant/api',
        iam_apikey='NGzCvJ0F7EPmWBLBJbD2pdwA5oqkFWtOur-lNJ-9OxGH')

def start_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Получение заявления", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Проверить заявление", color=VkKeyboardColor.PRIMARY) # пока что не реализовано
    keyboard = keyboard.get_keyboard()
    return keyboard

def hold_TGSK():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Нет, ТГСК не была проведена", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Да, ТГСК была проведена", color=VkKeyboardColor.PRIMARY)
    keyboard = keyboard.get_keyboard()
    return keyboard

def check_disability():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Да, инвалидность есть", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Инвалидность отсутствует", color=VkKeyboardColor.PRIMARY)
    keyboard = keyboard.get_keyboard()
    return keyboard

# def check_help_with_drugs():
#     keyboard = VkKeyboard(one_time=True)
#     keyboard.add_button("Да, помощь с препаратами нужна", color=VkKeyboardColor.PRIMARY)
#     keyboard.add_button("Нет, помощь с препаратами не нужна", color=VkKeyboardColor.PRIMARY)
#     keyboard = keyboard.get_keyboard()
#     return keyboard

def check_help_with_drugs():
    keyboard = VkKeyboard(one_time=True)
    prepare = ["Да, помощь с препаратами нужна", "Нет, помощь с препаратами не нужна"]
    temp_for_long = []
    for i in range(len(prepare)):
        temp_for_long.append([{
            "action": {
                "type": "text",
                "payload": json.dumps(""),
                "label": prepare[i]
            },
            "color": "primary"
        }])

    keyboard = {
        "one_time": True,
        "buttons": temp_for_long
    }
    print(json.dumps(keyboard, indent=2))

    keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
    keyboard = str(keyboard.decode('utf-8'))
    return keyboard

def check_request_hospital():
    keyboard = VkKeyboard(one_time=True)
    prepare = ["Да, в больницу обращался(лась)", "Нет, в больницу не обращался(лась)"]
    temp_for_long = []
    for i in range(len(prepare)):
        temp_for_long.append([{
            "action": {
                "type": "text",
                "payload": json.dumps(""),
                "label": prepare[i]
            },
            "color": "primary"
        }])

    keyboard = {
        "one_time": True,
        "buttons": temp_for_long
    }
    print(json.dumps(keyboard, indent=2))

    keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
    keyboard = str(keyboard.decode('utf-8'))
    return keyboard

def check_medical_commission():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Да, была проведена", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Нет, не была проведена", color=VkKeyboardColor.PRIMARY)
    keyboard = keyboard.get_keyboard()
    return keyboard

def check_representative_name():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Да, является", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Нет, не является", color=VkKeyboardColor.PRIMARY)
    keyboard = keyboard.get_keyboard()
    return keyboard

def check_ministry_health():
    keyboard = VkKeyboard(one_time=True)
    prepare = ["Да, в Минздрав обращался(лась)", "Нет, в Минздрав не обращался(лась)"]
    temp_for_long = []
    for i in range(len(prepare)):
        temp_for_long.append([{
            "action": {
                "type": "text",
                "payload": json.dumps(""),
                "label": prepare[i]
            },
            "color": "primary"
        }])

    keyboard = {
        "one_time": True,
        "buttons": temp_for_long
    }
    print(json.dumps(keyboard, indent=2))

    keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
    keyboard = str(keyboard.decode('utf-8'))
    return keyboard

def check_prosecutor():
    keyboard = VkKeyboard(one_time=True)
    prepare = ["Да, в Прокуратуру", "Да, в Росздравнадзор", "Нет, я никуда не обращался"]
    temp_for_long = []
    temp_for_little = []
    for i in range(len(prepare)):

        # если содержимое кнопки выходит за рамки
        if (len(prepare[i]) > 25):
            temp_for_long.append([{
                "action": {
                    "type": "text",
                    "payload": json.dumps(""),
                    "label": prepare[i]
                },
                "color": "primary"
            }])
        else:
            temp_for_little.append({
                "action": {
                    "type": "text",
                    "payload": json.dumps(""),
                    "label": prepare[i]
                },
                "color": "primary"
            })

    keyboard = {
        "one_time": True,
        "buttons": temp_for_long + [temp_for_little]
    }

    keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
    keyboard = str(keyboard.decode('utf-8'))
    return keyboard

def check_court():
    keyboard = VkKeyboard(one_time=True)
    prepare = ["Да, я обращался(лась) в суд", "Нет, я не обращался(лась) в суд"]
    temp_for_long = []
    for i in range(len(prepare)):
        temp_for_long.append([{
            "action": {
                "type": "text",
                "payload": json.dumps(""),
                "label": prepare[i]
            },
            "color": "primary"
        }])

    keyboard = {
        "one_time": True,
        "buttons": temp_for_long
    }

    keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
    keyboard = str(keyboard.decode('utf-8'))
    return keyboard

def check_diagnoses(prepare):
    keyboard = VkKeyboard(one_time=True)
    temp_for_long = []
    temp_for_little = []
    for i in range(len(prepare)):

        # если содержимое кнопки выходит за рамки
        if (len(prepare[i]) > 25):
            temp_for_long.append([{
                "action": {
                    "type": "text",
                    "payload": json.dumps(""),
                    "label": prepare[i]
                },
                "color": "primary"
            }])
        else:
            temp_for_little.append({
                "action": {
                    "type": "text",
                    "payload": json.dumps(""),
                    "label": prepare[i]
                },
                "color": "primary"
            })
    if(len(temp_for_long) > 0 and len(temp_for_little) > 0):
        keyboard = {
            "one_time": True,
            "buttons": temp_for_long + [temp_for_little]
        }
    elif(len(temp_for_long) > 0 and len(temp_for_little) < 1):
        keyboard = {
            "one_time": True,
            "buttons": temp_for_long
        }
    elif(len(temp_for_long) < 1 and len(temp_for_little) > 0):
        keyboard = {
            "one_time": True,
            "buttons": [temp_for_little]
        }

    print(json.dumps(keyboard, indent=2))

    keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
    keyboard = str(keyboard.decode('utf-8'))
    return keyboard

def accuracy_keyboard(entities):
    keyboard = VkKeyboard(one_time=True)
    prepare = []
    for i in range(len(entities)):
        pre_temp = entities[i]["entity"].split('_')
        temp = ""
        for i in range(len(pre_temp)):
            temp += (pre_temp[i] + " ")
        res = temp[0].upper() + temp[1:]
        prepare.append(res)
    temp_for_long = []
    temp_for_little = []
    for i in range(len(prepare)):

        #если содержимое кнопки выходит за рамки
        if (len(prepare[i]) > 25):
            temp_for_long.append([{
                "action": {
                    "type": "text",
                    "payload": json.dumps(""),
                    "label": prepare[i]
                },
                "color": "primary"
            }])
        else:
            temp_for_little.append({
                "action": {
                    "type": "text",
                    "payload": json.dumps(""),
                    "label": prepare[i]
                },
                "color": "primary"
            })

    keyboard = {
        "one_time": True,
        "buttons": temp_for_long + [temp_for_little]
    }

    keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
    keyboard = str(keyboard.decode('utf-8'))
    return keyboard

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

def toUpper(temp):
    return temp[0].upper() + temp[1:]

list_diagnoses = ["Иммунодефицит неуточненный", "Дефект в системе комплемента", "Общий вариабельный иммунодефицит",
                  "Избирательный дефицит иммуноглобулина A [IgA]", "Наследственная гипогаммаглобулинемия", "Синдром Вискотта-Олдрича",
                  "Тяжелый комбинированный иммунодефицит", "Другие комбинированные иммунодефициты", "Общий вариабельный иммунодефицит неуточненный",
                  "Синдром Ниймеген", "Синдром Луи-Бар", "Агаммаглобулинемия неуточненная", "ХГБ, аутосомно-рецессивная",
                  "ТКИН неуточненный, синдром Оменн", "Другой вид ПИД"]
def start():
    while True:
            # даныне пациентов или законных представителей
            data_person = {}

            # для отслеживания потока пользователей
            unique_users = []

            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW:
                    response = event.text

                    person = DataPerson("", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
                    try:
                        if(event.user_id in unique_users): # пользователь уже записан
                            person = data_person[str(event.user_id)]
                            unique_users =  set(unique_users)
                            unique_users = list(unique_users)
                        else: #пользователь ещё не обращался к боту
                            unique_users.append(event.user_id)

                        data_person[str(event.user_id)] = person

                        if event.from_user and not event.from_me:

                            #создание сессии
                            session = service.create_session("55340594-28fd-4e4a-879a-69b0c6f2fa04").get_result()

                            #получение резалта
                            resp = service.message(
                                assistant_id='55340594-28fd-4e4a-879a-69b0c6f2fa04',
                                session_id=session['session_id'],
                                input={
                                    'message_type': 'text',
                                    'text': response
                                }
                            ).get_result()

                            # удаление сессии
                            service.delete_session("55340594-28fd-4e4a-879a-69b0c6f2fa04",
                                                    session['session_id']).get_result()

                            #вычисление ФИО пациента или законного представителя
                            matches = extractor(response)
                            spans = [_.span for _ in matches]
                            facts = [_.fact.as_json for _ in matches]

                            intents = ""
                            if(len(resp["output"]["intents"]) < 1 and len(facts) < 1 and response != "Получение заявления" and
                                    response != "вывод" and person.stepForDiagnosis != 1 and person.stepForTgsk != 1 and person.stepForDisability != 1 and
                                    person.stepForEmail != 1 and person.stepForMobile != 1 and person.stepForCheckNeed != 1 and person.stepForQuestions != 1 and
                                    person.stepForRepresentativeName != 1):
                                vk_session.method("messages.send",
                                                {"user_id": event.user_id, "message": "Не балуйтесь! Вводите только запрашиваемые данные!", "random_id": 0})
                            elif(len(resp["output"]["intents"]) == 1):
                                intents = resp["output"]["intents"][0]["intent"]
                            entities = resp["output"]["entities"]

                            # Вступительная часть
                            if(intents == "приветствие" and response != "Получение заявления"):
                                vk_session.method("messages.send",
                                                  {"user_id": event.user_id, "message": "Добрый день! Выбери услугу:", "random_id": 0,
                                                   'keyboard': start_keyboard()})
                            elif(response == "вывод"):
                                temp = "Причина: " + person.rejection_reason + "\n" +\
                                       "ФИО пациента: " + person.patient_name + "\n" + \
                                       "ФИО законного представителя: " + person.representative_name + "\n" + \
                                       "Регион: " + person.region + "\n" +\
                                       "Возраст: " + person.age + "\n" +\
                                       "Диагноз: " + person.diagnosis + "\n" +\
                                       "ТГСК была проведена: " + person.tgsk + "\n" +\
                                       "Наличие инвалидности: " + person.disability + "\n" +\
                                       "E-mail: " + person.email + "\n" +\
                                       "Телефон: " + person.mobile + "\n" +\
                                       "Помощь с препаратами от фонда: " + person.help_with_drugs + "\n" +\
                                       "Обращение в больницу по месту жительства: " + person.appeal_hospital + "\n" +\
                                       "Была проведена Врачебная комиссия:" + person.hold_medical_commission + "\n" +\
                                       "Обращение в Минздрав: " + person.ministry_health + "\n" +\
                                       "Обращение в Прокуратуру и Росздравнадзор: " + person.prosecutor + "\n" +\
                                       "Обращение в суд: " + person.court_appeal
                                vk_session.method("messages.send",
                                                  {"user_id": event.user_id,
                                                   "message": temp,
                                                   "random_id": 0})
                            elif(response == "Получение заявления"):
                                vk_session.method("messages.send",
                                                  {"user_id": event.user_id, "message": "Продолжая общение с ботом вы соглашаетесь с обработкой ваших персональных данных.",
                                                   "random_id": 0})
                                vk_session.method("messages.send",
                                                  {"user_id": event.user_id, "message": "По какой причине вам отказали:", "random_id": 0})
                            else:
                                #если нашлась 1 подходящая причина
                                if(len(entities) == 1 or len(facts) > 0 or intents == "регион" or intents == "возраст" or
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
                                        vk_session.method("messages.send",
                                                          {"user_id": event.user_id,
                                                           "message": "Причина записана! [" + person.rejection_reason + "]",
                                                           "random_id": 0})
                                        vk_session.method("messages.send",
                                                          {"user_id": event.user_id,
                                                           "message": "Введите ФИО пациента :",
                                                           "random_id": 0})
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
                                        vk_session.method("messages.send",
                                                          {"user_id": event.user_id,
                                                           "message": "ФИО записаны! [" + person.patient_name + "]",
                                                           "random_id": 0})

                                        vk_session.method("messages.send",
                                                          {"user_id": event.user_id,
                                                           "message": "Пациент является своим законным представителем ?",
                                                           "random_id": 0,
                                                           'keyboard': check_representative_name()})
                                    elif (person.stepCheckRepresentativeName != 1 and person.stepPatientName == 1):

                                        print("Проверка ФИО законного представителя")
                                        if(response == "Да, является"):
                                            person.representative_name = ""
                                            person.stepCheckRepresentativeName = 1
                                            person.stepRepresentativeName = 1
                                            vk_session.method("messages.send",
                                                              {"user_id": event.user_id,
                                                               "message": "Введите регион (республика, край, область, округ), в котором вы проживаете:",
                                                               "random_id": 0})
                                        elif(response == "Нет, не является"):
                                            person.stepCheckRepresentativeName = 1
                                            vk_session.method("messages.send",
                                                              {"user_id": event.user_id,
                                                               "message": "Введите ФИО законного представителя :",
                                                               "random_id": 0})
                                    elif(person.stepRepresentativeName != 1 and person.stepCheckRepresentativeName == 1):
                                        if(len(facts[0]) < 3):
                                            person.representative_name = toUpper(facts[0]["last"]) + " " + toUpper(
                                                facts[0]["first"])
                                        else:
                                            person.representative_name = toUpper(facts[0]["last"]) + " " + toUpper(
                                                facts[0]["first"]) + " " + toUpper(facts[0]["middle"])
                                        person.stepRepresentativeName = 1
                                        vk_session.method("messages.send",
                                                          {"user_id": event.user_id,
                                                           "message": "ФИО записаны! [" + person.representative_name + "]",
                                                           "random_id": 0})
                                        vk_session.method("messages.send",
                                                          {"user_id": event.user_id,
                                                           "message": "Введите регион (республика, край, область, округ), в котором вы проживаете:",
                                                           "random_id": 0})
                                    elif (person.stepRegion != 1 and person.stepRepresentativeName == 1):
                                        print("Регион")
                                        if(intents == "регион"):
                                            person.stepRegion = 1
                                            person.region = response
                                            vk_session.method("messages.send",
                                                              {"user_id": event.user_id,
                                                               "message": "Регион записан! [" + person.region + "]",
                                                               "random_id": 0})
                                            vk_session.method("messages.send",
                                                              {"user_id": event.user_id,
                                                               "message": "Введите возраст пациента:",
                                                               "random_id": 0})
                                    elif (person.stepAge != 1 and person.stepRegion == 1):
                                        print("Возраст")
                                        if (intents == "возраст"):
                                            person.stepForDiagnosis = 1
                                            person.stepAge = 1
                                            for_res = ""
                                            for j in range(len(response)):
                                                if(response[j].isdigit()):
                                                    for_res += response[j]
                                            person.age = for_res
                                            vk_session.method("messages.send",
                                                              {"user_id": event.user_id,
                                                               "message": "Возраст записан! [" + person.age + "]",
                                                               "random_id": 0})
                                            vk_session.method("messages.send",
                                                              {"user_id": event.user_id,
                                                               "message": "Введите дианоз пациента :",
                                                               "random_id": 0})
                                    elif (person.stepDiagnosis != 1 and person.stepAge == 1):
                                        print("Диагноз")
                                        one = ""
                                        two = ""
                                        temp_for = {}
                                        ok = False
                                        # если выбран 100% правильный диагноз
                                        for j in range(len(list_diagnoses)):
                                            if (int(search_partial_text(response.lower(), list_diagnoses[j].lower())) == 100):
                                                ok = True
                                                break
                                        if (ok):
                                            person.stepForTgsk = 1
                                            person.stepDiagnosis = 1
                                            person.diagnosis = response
                                            vk_session.method("messages.send",
                                                              {"user_id": event.user_id,
                                                               "message": "Диагноз записан! [" + person.diagnosis + "]",
                                                               "random_id": 0})
                                            vk_session.method("messages.send",
                                                              {"user_id": event.user_id,
                                                               "message": "У пациента была проведена ТГСК (Трансплантация гемопоэтических стволовых клеток) :",
                                                               "random_id": 0,
                                                               'keyboard': hold_TGSK()})
                                        else:
                                            for j in range(len(list_diagnoses)):
                                                if(int(search_partial_text(response.lower(), list_diagnoses[j].lower())) < 100):
                                                    temp_for[str(list_diagnoses[j])] = int(search_partial_text(response.lower(), list_diagnoses[j].lower()))
                                            list_temp_for = list(temp_for.items())
                                            list_temp_for.sort(key=lambda i: i[1])
                                            d = 0
                                            for j in list_temp_for:
                                                print(str(j[0]) + " : " + str(j[1]))
                                                d = d + 1
                                                if(d == 14):
                                                    two = j[0]
                                                elif(d == 15):
                                                    one = j[0]
                                            print("one: " + one + "\ntwo: " + two)
                                            prepare = [one, two]
                                            vk_session.method("messages.send",
                                                              {"user_id": event.user_id,
                                                               "message": "Возможно вы имели ввиду:",
                                                               "random_id": 0,
                                                               'keyboard': check_diagnoses(prepare)})
                                    elif (person.stepTgsk != 1 and person.stepDiagnosis == 1):
                                        print("ТГСК")
                                        if(response == "Нет, ТГСК не была проведена"):
                                            person.stepTgsk = 1
                                            person.tgsk = "Нет"
                                            if(person.rejection_reason == "Отсутствие инвалидности"):
                                                person.stepDisability = 1
                                                person.disability = "Нет"
                                                vk_session.method("messages.send",
                                                                  {"user_id": event.user_id,
                                                                   "message": "Перечислите препараты, прописанные пациенту через запятую :",
                                                                   "random_id": 0})
                                            else:
                                                vk_session.method("messages.send",
                                                                  {"user_id": event.user_id,
                                                                   "message": "У пациента есть инвалидность ?",
                                                                   "random_id": 0,
                                                                   'keyboard':check_disability()})
                                        elif(response == "Да, ТГСК была проведена"):
                                            person.stepForDisability = 1
                                            person.stepTgsk = 1
                                            person.tgsk = "Да"
                                            if (person.rejection_reason == "Отсутствие инвалидности"):
                                                person.stepDisability = 1
                                                person.disability = "Нет"
                                                vk_session.method("messages.send",
                                                                  {"user_id": event.user_id,
                                                                   "message": "Перечислите препараты, прописанные пациенту через запятую :",
                                                                   "random_id": 0})
                                            else:
                                                vk_session.method("messages.send",
                                                                  {"user_id": event.user_id,
                                                                   "message": "У пациента есть инвалидность ?",
                                                                   "random_id": 0,
                                                                   'keyboard': check_disability()})
                                    elif (person.stepDisability != 1 and person.stepTgsk == 1):
                                        print("Инвалидность")
                                        if(response == "Да, инвалидность есть"):
                                            person.stepDisability = 1
                                            person.disability = "Да"
                                            vk_session.method("messages.send",
                                                              {"user_id": event.user_id,
                                                               "message": "Перечислите препараты, прописанные пациенту через запятую :",
                                                               "random_id": 0})
                                        elif(response == "Инвалидность отсутствует"):
                                            person.stepDisability = 1
                                            person.disability = "Нет"
                                            vk_session.method("messages.send",
                                                              {"user_id": event.user_id,
                                                               "message": "Перечислите препараты, прописанные пациенту через запятую :",
                                                               "random_id": 0})
                                    elif (person.stepDrugs != 1 and person.stepDisability == 1):
                                        print("Препараты")
                                        res = response.split(',')
                                        for j in range(len(res)):
                                            person.drugs += res[j].strip()
                                        person.stepDrugs = 1
                                        person.stepForEmail = 1
                                        vk_session.method("messages.send",
                                                          {"user_id": event.user_id,
                                                           "message": "Введите контактный E-mail :",
                                                           "random_id": 0})
                                    elif (person.stepEmail != 1 and person.stepDrugs == 1):
                                        print("Email")
                                        person.email = response
                                        person.stepEmail = 1
                                        person.stepForMobile = 1
                                        vk_session.method("messages.send",
                                                          {"user_id": event.user_id,
                                                           "message": "Введите контактный телефон :",
                                                           "random_id": 0})
                                    elif (person.stepMobile != 1 and person.stepEmail == 1):
                                        print("Телефон")
                                        person.mobile = response
                                        person.stepMobile = 1
                                        person.stepForCheckNeed = 1
                                        vk_session.method("messages.send",
                                                          {"user_id": event.user_id,
                                                           "message": "Нужна помощь с препаратами от фонда ?",
                                                           "random_id": 0,
                                                           "keyboard": check_help_with_drugs()})
                                    elif (person.stepHelpWithDrugs != 1 and person.stepMobile == 1):
                                        if(response == "Да, помощь с препаратами нужна"):
                                            person.help_with_drugs = "Да"
                                            person.stepHelpWithDrugs = 1
                                            person.stepForQuestions = 1
                                            vk_session.method("messages.send",
                                                              {"user_id": event.user_id,
                                                               "message": "Вы обращались в больницу по месту жительства ?",
                                                               "random_id": 0,
                                                               "keyboard": check_request_hospital()})
                                        elif(response == "Нет, помощь с препаратами не нужна"):
                                            person.help_with_drugs = "Нет"
                                            person.stepHelpWithDrugs = 1
                                            person.stepForQuestions = 1
                                            vk_session.method("messages.send",
                                                              {"user_id": event.user_id,
                                                               "message": "Обращались ли вы в больницу по месту жительства ?",
                                                               "random_id": 0,
                                                               "keyboard": check_request_hospital()})
                                    elif (person.stepAppealHospital != 1 and person.stepHelpWithDrugs == 1):
                                        if(response == "Да, в больницу обращался(лась)"):
                                            person.appeal_hospital = "Да"
                                            person.stepAppealHospital = 1
                                            vk_session.method("messages.send",
                                                              {"user_id": event.user_id,
                                                               "message": "Была проведена врачебная комиссия ?",
                                                               "random_id": 0,
                                                               "keyboard": check_medical_commission()})
                                        elif(response == "Нет, в больницу не обращался(лась)"):
                                            person.appeal_hospital = "Нет"
                                            person.stepAppealHospital = 1
                                            vk_session.method("messages.send",
                                                              {"user_id": event.user_id,
                                                               "message": "Была проведена врачебная комиссия ?",
                                                               "random_id": 0,
                                                               "keyboard": check_medical_commission()})
                                    elif (person.stepHoldMedicalCommission != 1 and person.stepHelpWithDrugs == 1):
                                        if(response == "Да, была проведена"):
                                            person.hold_medical_commission = "Да"
                                            person.stepHoldMedicalCommission = 1
                                            vk_session.method("messages.send",
                                                              {"user_id": event.user_id,
                                                               "message": "Вы обращались в орган исполнительной власти в сфере здравоохранения (Минздрав) ?",
                                                               "random_id": 0,
                                                               "keyboard": check_ministry_health()})
                                        elif(response == "Нет, не была проведена"):
                                            person.hold_medical_commission = "Нет"
                                            person.stepHoldMedicalCommission = 1
                                            vk_session.method("messages.send",
                                                              {"user_id": event.user_id,
                                                               "message": "Вы обращались в орган исполнительной власти в сфере здравоохранения (Минздрав) ?",
                                                               "random_id": 0,
                                                               "keyboard": check_ministry_health()})
                                    elif (person.stepMinistryHealth != 1 and person.stepHoldMedicalCommission == 1):
                                        if (response == "Да, в Минздрав обращался(лась)"):
                                            person.ministry_health = "Да"
                                            person.stepMinistryHealth = 1
                                            vk_session.method("messages.send",
                                                              {"user_id": event.user_id,
                                                               "message": "Вы обращались в контроллирующие органы государственной власти (Прокуратуру и Росздравнадзор) ?",
                                                               "random_id": 0,
                                                               "keyboard": check_prosecutor()})
                                        elif (response == "Нет, в Минздрав не обращался(лась)"):
                                            person.ministry_health = "Нет"
                                            person.stepMinistryHealth = 1
                                            vk_session.method("messages.send",
                                                              {"user_id": event.user_id,
                                                               "message": "Вы обращались в контроллирующие органы государственной власти (Прокуратуру и Росздравнадзор) ?",
                                                               "random_id": 0,
                                                               "keyboard": check_prosecutor()})
                                    elif (person.stepProsecutor != 1 and person.stepMinistryHealth == 1):
                                        if (response == "Да, в Прокуратуру"):
                                            person.prosecutor = "Да"
                                            person.stepProsecutor = 1
                                            vk_session.method("messages.send",
                                                              {"user_id": event.user_id,
                                                               "message": "Вы обращались в суд ?",
                                                               "random_id": 0,
                                                               "keyboard": check_court()})
                                        elif (response == "Да, в Росздравнадзор"):
                                            person.prosecutor = "Да"
                                            person.stepProsecutor = 1
                                            vk_session.method("messages.send",
                                                              {"user_id": event.user_id,
                                                               "message": "Вы обращались в суд ?",
                                                               "random_id": 0,
                                                               "keyboard": check_court()})
                                        elif (response == "Нет, я никуда не обращался"):
                                            person.prosecutor = "Нет"
                                            person.stepProsecutor = 1
                                            vk_session.method("messages.send",
                                                              {"user_id": event.user_id,
                                                               "message": "Вы обращались в суд ?",
                                                               "random_id": 0,
                                                               "keyboard": check_court()})
                                    elif (person.stepCourtAppeal != 1 and person.stepProsecutor == 1):
                                        if (response == "Да, я обращался(лась) в суд"):
                                            person.court_appeal = "Да"
                                            person.stepCourtAppeal = 1
                                            # patient_name, representative_name, region, mobile, diagnosis, drugs,
                                            # rejection_reason, age, tgsk, disability, appeal_hospital, hold_medical_commission, ministry_health):

                                            if(person.rejection_reason == "Другое"):
                                                print()
                                                # тут отправка сообщения оператору НКО
                                            else:
                                                data = start.renew_table()
                                                temp_for_reason = ["Препарата нет в продаже", "Нет инструкции", "Отсутствие инвалидности", "Не является необходимым для жизни", "Вместо льгот деньги", "Нарушение прав"]
                                                res_reason = ""
                                                for j in range(len(temp_for_reason)):
                                                    if(temp_for_reason[j] == person.rejection_reason):
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

                                                doc = clf.request_processing(data)
                                                start.send_mail(person.email, doc)

                                            vk_session.method("messages.send",
                                                              {"user_id": event.user_id,
                                                               "message": "Заявка на получение заявления успешно обработана.\nЗаявление с инструкцией отправлены на указанный E-mail: " + person.email + "\nСпасибо за обращение!",
                                                               "random_id": 0})
                                        elif (response == "Нет, я не обращался(лась) в суд"):
                                            person.court_appeal = "Нет"
                                            person.stepCourtAppeal = 1

                                            if (person.rejection_reason == "Другое"):
                                                print()
                                                # тут отправка сообщения оператору НКО
                                            else:
                                                data = start.renew_table()
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

                                                doc = clf.request_processing(data)
                                                start.send_mail(person.email, doc)

                                            vk_session.method("messages.send",
                                                              {"user_id": event.user_id,
                                                               "message": "Заявка на получение заявления успешно обработана.\nЗаявление с инструкцией отправлены на указанный E-mail: " + person.email + "\nСпасибо за обращение!",
                                                               "random_id": 0})
                                elif((intents == "причина_отказа" and len(entities) < 1) or (intents == "" and person.stepRejectionReason != 1 and person.stepPatientName != 1 and person.stepRepresentativeName != 1 and person.stepRegion != 1 and
                                                                                             person.stepAge != 1 and person.stepDiagnosis != 1 and person.stepDisability != 1 and person.stepTgsk != 1 and
                                                                                             person.stepDrugs != 1 and person.stepEmail != 1 and person.stepMobile != 1 and person.stepHelpWithDrugs != 1 and
                                                                                             person.stepAppealHospital != 1 and person.stepCourtAppeal != 1 and person.stepHoldMedicalCommission != 1 and
                                                                                             person.stepMinistryHealth != 1 and person.stepProsecutor != 1)):
                                    vk_session.method("messages.send",
                                                      {"user_id": event.user_id, "message": "Ваша причина относится к категории \"Другое\". После заполнения заявления с вами свяжется специалист.",
                                                       "random_id": 0})
                                    person.rejection_reason = "Другое"
                                    person.stepRejectionReason = 1  # заполнили причину отказа
                                    vk_session.method("messages.send",
                                                      {"user_id": event.user_id,
                                                       "message": "Причина записана! [" + person.rejection_reason + "]",
                                                       "random_id": 0})
                                    vk_session.method("messages.send",
                                                      {"user_id": event.user_id,
                                                       "message": "Введите ФИО пациента :",
                                                       "random_id": 0})
                                # если пользователь ввёл что-то не то, что нужно
                                elif(len(entities) < 1 and person.stepForDiagnosis == 0 and person.stepForTgsk == 0 and person.stepForDisability == 0 and person.stepForEmail == 0 and
                                     person.stepForMobile == 0 and person.stepForRepresentativeName == 0 and person.stepForCheckNeed == 0 and person.stepForCheckNeed == 0):
                                    vk_session.method("messages.send",
                                                      {"user_id": event.user_id, "message": "Привет! Выбери услугу:",
                                                       "random_id": 0,
                                                       "keyboard": start_keyboard()})
                                elif(len(entities) > 1):
                                    vk_session.method("messages.send",
                                                  {"user_id": event.user_id, "message": "Уточните, что вы имели ввиду:", "random_id": 0,
                                                   'keyboard': accuracy_keyboard(entities)})
                            #print(intents)
                            #print("————————————————")
                    except ibm_watson.ApiException:
                        print("505 ошибка IBM Cloud")

start()