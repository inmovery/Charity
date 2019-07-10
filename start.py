import requests
import json
import smtplib
import datetime
from os.path import basename
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText  # Текст/HTML
from email.mime.application import MIMEApplication

downloader_url = 'https://script.google.com/macros/s/AKfycbx2jWe4Rc3BG1BHTBdKuM7rhDaG2MB6ygWJnTA96o-6gk_JvJb6/exec'
docid = open('answers-table-id').read()
HOST = 'smtp.yandex.ru'
addr_from = 'ortemmmm@yandex.ru'
password = 'ortemx4ik'

def send_mail(addr_to, doc):
    password = "ortemx4ik"  # Пароль
    filename = 'заявление.docx'
    msg = MIMEMultipart()  # Создаем сообщение
    msg['From'] = addr_from  # Адресат
    msg['To'] = addr_to  # Получатель
    msg['Subject'] = 'Ответ на обращение'  # Тема сообщения

    body = 'Здравствуйте, вы обратились в фонд "Подслонух", ваше заявление было обработано автоматически. ' \
           'Во вложении вы найдете заявление, с которым можете обратиться в государственное учредение по месту жительства'

    msg.attach(MIMEText(body, 'plain'))  # Добавляем в сообщение текст
    doc.save(filename)
    with open(filename, "rb") as fil:
        part = MIMEApplication(
            fil.read(),
            Name=basename(filename)
        )
    # After the file is closed
    part['Content-Disposition'] = 'attachment; filename="%s"' % basename(filename)
    msg.attach(part)
    server = smtplib.SMTP_SSL(HOST, 465)  # Создаем объект SMTP
    server.login(addr_from, password)  # Получаем доступ
    server.send_message(msg)  # Отправляем сообщение
    server.quit()  # Выходим