#!/usr/bin/env python
# coding: utf-8
import os

from docx import Document
from docx.shared import Pt

def processing(document, patient_name, representative_name, address, telephone,
               illness, medicine):
    style = document.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)

    for paragraph in document.paragraphs:

        if 'PATIENT_NAME' in paragraph.text:
            paragraph.text = paragraph.text.replace('PATIENT_NAME', patient_name)
        if 'REPRESENTATIVE_NAME' in paragraph.text:
            paragraph.text = paragraph.text.replace('REPRESENTATIVE_NAME', representative_name)
        if 'ADDRESS' in paragraph.text:
            paragraph.text = paragraph.text.replace('ADDRESS', address)
        if 'TELEPHONE' in paragraph.text:
            paragraph.text = paragraph.text.replace('TELEPHONE', telephone)
        if 'ILLNESS' in paragraph.text:
            paragraph.text = paragraph.text.replace('ILLNESS', illness)
        if 'MEDICINE' in paragraph.text:
            paragraph.text = paragraph.text.replace('MEDICINE', medicine)

        paragraph.style = document.styles['Normal']

    return document

def request_processing(data):
    # patient_name, representative_name, address, telephone, illness, medicine,
    # reason, if_older_3, if_tgsk, if_invalid, if_hospital, if_comission, if_minzdrav

    doc_path = ''

    patient_name = data['patient_name']
    representative_name = data['representative_name']
    address = data['address']
    telephone = data['telephone']
    illness = data['illness']
    medicine = data['medicine']
    reason = data['reason']
    if_older_3 = data['if_older_3']
    if_tgsk = data['if_tgsk']
    if_invalid = data['if_invalid']
    if_hospital = data['if_hospital']
    if_comission = data['if_comission']
    if_minzdrav = data['if_minzdrav']

    if (not if_hospital) or (not if_comission):
        if representative_name != '':
            if if_tgsk:
                doc_path = os.path.abspath('applications/hospital/больница ТГСК.docx')
            elif if_invalid:
                doc_path = os.path.abspath('applications/hospital/больница по ТН 1.docx')
            elif not if_older_3:
                doc_path = os.path.abspath('applications/hospital/больница по ТН 2.docx')
            else:
                doc_path = os.path.abspath('applications/hospital/больница по ТН 3.docx')
        else:
            doc_path = os.path.abspath('applications/hospital/больница 5 взр.docx')

    elif not if_minzdrav:
        if representative_name != '':
            if reason == 4:
                doc_path = os.path.abspath('applications/minzdrav/МЗ ребенок не входит в перечень.docx')
            elif reason == 6:
                doc_path = os.path.abspath('applications/minzdrav/МинЗ доступность и качество.docx')
            else:
                if if_invalid:
                    doc_path = os.path.abspath('applications/minzdrav/МЗ ребенок 1.docx')
                elif not if_older_3:
                    doc_path = os.path.abspath('applications/minzdrav/МЗ ребенок 2.docx')
                else:
                    doc_path = os.path.abspath('applications/minzdrav/МЗ ребенок 3.docx')
        else:
            if reason == 4:
                doc_path = os.path.abspath('applications/minzdrav/МЗ - взр общ не входит в перечень.docx')
            elif reason == 6:
                doc_path = os.path.abspath('applications/minzdrav/МинЗ доступность и качество.docx')

    else:
        if representative_name != '':
            if reason == 4:
                doc_path = os.path.abspath('applications/procecutor_roszdrav/прокуратура ребенок не входит в перечень.docx')
            elif reason == 6:
                doc_path = os.path.abspath('applications/procecutor_roszdrav/прокуратура доступность и качество.docx')
            else:
                if if_invalid:
                    doc_path = os.path.abspath('applications/procecutor_roszdrav/прокуратура и росздрав ребенок инв.docx')
                elif not if_older_3:
                    doc_path = os.path.abspath('applications/procecutor_roszdrav/прокуратура и росздрав ребенок 3х.docx')
                else:
                    doc_path = os.path.abspath('applications/procecutor_roszdrav/прокуратура ребенок 3.docx')
        else:
            if reason == 4:
                doc_path = os.path.abspath('applications/procecutor_roszdrav/прокуратура - взр общ не входит в перечень.docx')
            elif reason == 6:
                doc_path = os.path.abspath('applications/procecutor_roszdrav/прокуратура доступность и качество.docx')
            else:
                doc_path = os.path.abspath('applications/procecutor_roszdrav/прокуратура и росздрав - взр общ.docx')

    document = Document(doc_path)
    new_document = processing(document, patient_name, representative_name, address,
                              telephone, illness, medicine)

    return new_document