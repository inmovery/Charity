import base64
import email
import os
import smtplib
import zipfile
from email import encoders
from email.mime.base import MIMEBase
from os.path import basename
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText  # Текст/HTML
from email.mime.application import MIMEApplication

from zipfile import ZipFile

from docx import Document

import Config
from PatternDetect import request_processing

def send_mail(addr_to, doc):
    filename = 'Statement.docx'
    doc.save(filename)
    with ZipFile('Docs.zip', 'w') as zip:
        zip.write(filename)

    msg = MIMEMultipart()  # Создаем сообщение
    msg['From'] = Config.ADDRESS_FROM  # Адресат
    msg['To'] = addr_to  # Получатель
    msg['Subject'] = 'Ответ на обращение'  # Тема сообщения

    html = """\
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <title>Фонд "Подсолнух"</title>
    </head>
    <body>
        <table id="top-message" cellpadding="20" cellspacing="0" width="550" align="center">
        <tr>
            <td align="center">
                <p>Проблемы с отображением письма?<a href="#">Просмотрите его в браузере.</a></p>
            </td>
        </tr>
        <tr bgcolor="white">
            <td align="center">
                <p align="left">
                    Здравствуйте, вы обратились в фонд "Подслонух", ваше заявление было обработано автоматически. Во вложении вы найдете заявление, с которым можете обратиться в государственное учредение по месту жительства
                    <br/><br/>
                    Согласно ст. 2 Федерального закона от 02.05.2006 N 59-ФЗ "О порядке рассмотрения обращений граждан Российской Федерации", граждане имеют право обращаться лично, а также направлять индивидуальные и коллективные обращения, в государственные органы, органы местного самоуправления и их должностным лицам, в государственные и муниципальные учреждения и их должностным лицам.
                    <br/><br/>
                    Срок рассмотрения письменного обращения, поступившего в государственный орган, орган местного самоуправления или должностному лицу в соответствии с их компетенцией, рассматривается в течение 30 дней со дня регистрации письменного обращения.
                    <br/><br/>
                    Нарушение установленного порядка рассмотрения обращений граждан должностными лицами государственных органов, органов местного самоуправления, государственных и муниципальных учреждений и иных организаций, на которые возложено осуществление публично значимых функций, влечет наложение административного штрафа в размере от пяти тысяч до десяти тысяч рублей (ст. 5.59 Кодекса Российской Федерации об административных нарушениях).
                    <br/><br/>
                    Распечатайте заявление в двух экземплярах. Один экземпляр с приложенной к нему выпиской из больницы надо подать в приёмную или регистратуру вашей поликлиники по месту жительства. На втором экземпляре вам должны поставить отметку о принятии - поставить штамп с датой, должностью и подписью принявшего лица. Фотографию этого штампа надо прислать на почту ar@fondpodsonuh.ru или через WhatsApp или Viber 8-910-440-2099.
                </p>
            </td>
        </tr>
    </table><!-- top message -->
    </body>
    </html>
    """

    msg.attach(MIMEText(html, 'html', 'utf-8'))

    fp = open('Docs.zip', 'rb')
    zip2 = MIMEBase('application', 'zip')
    zip2.set_payload(fp.read())
    zip2.add_header('Content-Disposition', "attachment; filename= %s" % 'Docs.zip')
    fp.close()
    encoders.encode_base64(zip2)

    msg.attach(zip2)

    server = smtplib.SMTP_SSL(Config.HOST, 465)  # Создаем объект SMTP
    server.login(Config.ADDRESS_FROM, Config.PASSWORD)  # Получаем доступ
    server.send_message(msg)  # Отправляем сообщение
    server.quit()  # Выходим

document = Document('C:/Users/clay.DESKTOP-JFB7SPD/PycharmProjects/Charity/application/minzdrav/МинЗ доступность и качество.docx')
send_mail("roman_piskunov@bk.ru", document)

# msg.attach(MIMEText(html, 'html', 'utf-8'))
# doc.save(filename)
# part = MIMEApplication(b'hello', Name=basename(filename))#open(filename, 'rb').read()
# part['Content-Disposition'] = 'attachment; filename="%s"' % basename(filename)
# print(part)
# msg.attach(part)