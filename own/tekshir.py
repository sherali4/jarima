import re
from PyPDF2 import PdfReader
from django.shortcuts import get_object_or_404
from pdf2image import convert_from_path
from pyzbar.pyzbar import decode
from PIL import Image
import warnings
from datetime import datetime

from ish.models import Excelupload

def tekshirish(soato4, inn, xat_turi, hisobot_turi, yil, aniqlangan_sana, xat_sanasi, fayl_nomi):

    '''
       "soato4": "1710",
       "inn": "311858341",
       "xat_turi": "chaqiriq",
       "hisobot_turi": "12-korxona",
       "yil": "2024",
       'aniqlangan_sana': "10.06.2025",
       'xat_sanasi': "09.06.2025",
       fayl nomi = xat.pdf
    '''
    #kelayotgan ma'lumotlar
    mavjud = {
        "soato4": soato4,
        "inn": inn,
        "xat_turi": xat_turi,
        "hisobot_turi": hisobot_turi,
        "yil": yil,
        'aniqlangan_sana': aniqlangan_sana,
        'xat_sanasi': xat_sanasi,
    }


    oylar = {
        'yanvar': '01',
        'fevral': '02',
        'mart': '03',
        'aprel': '04',
        'may': '05',
        'iyun': '06',
        'iyul': '07',
        'avgust': '08',
        'sentyabr': '09',
        'oktyabr': '10',
        'noyabr': '11',
        'dekabr': '12'
    }

    if mavjud['xat_turi'] == "chaqiriq":
        xat_turi = r"chaqiriq.*?xat"
    else:
        xat_turi = r"ko.*?rsatma.*?xat"

    if mavjud['hisobot_turi'] == "1-korxona":
        hisobot_turi = r'1\s*-\s*?korxona|1\s*korxona'
    elif mavjud['hisobot_turi'] == "12-korxona":
        hisobot_turi = r'12\s*-\s*?korxona|12\s*korxona'
    elif mavjud['hisobot_turi'] == "1-moliya":
        hisobot_turi = r'1\s*-\s*?moliya|1\s*moliya'
    elif mavjud['hisobot_turi'] == "12-moliya":
        hisobot_turi = r'12\s*-\s*?moliya|12\s*moliya'
    else:
        hisobot_turi = r'fermer'

    hududlar_nomi = {
        '1703': 'Andijon',
        '1706': 'Buxoro',
        '1730': 'Farg‘ona',
        '1708': 'Jizzax',
        '1710': 'Qashqadaryo',
        '1712': 'Navoiy',
        '1714': 'Namangan',
        '1718': 'Samarqand',
        '1724': 'Sirdaryo',
        '1722': 'Surxondaryo',
        '1727': 'Toshkent',
        '1733': 'Xorazm',
        '1735': 'Qoraqalpog‘iston Respublikasi',
        '1726': 'Toshkent shahar',
    }
    hududlar_nomi = {k: v.lower() for k, v in hududlar_nomi.items()}

    baza = {
        'soato4': False,
        'inn': False,
        'xat_turi': False,
        'hisobot_turi': False,
        'yil': False,
        'aniqlangan_sana': False,
        'xat_sanasi': False,
        "boshqarma_boshligi": False,
        
    }

    hudud_nomi = hududlar_nomi[mavjud['soato4']]

    warnings.filterwarnings("ignore")
    reader = PdfReader(fayl_nomi)
    first_page = reader.pages[0]
    text = first_page.extract_text()

    if text and hudud_nomi in text.lower():
        baza['soato4'] = True
        
    if text and str(mavjud['inn']) in text:
        baza['inn'] = True

    if text:
        matches = re.findall(xat_turi, text, re.IGNORECASE)
        for match in matches:
            baza['xat_turi'] = True

    if text:
        matches = re.findall(hisobot_turi, text, re.IGNORECASE)
        for match in matches:
            baza['hisobot_turi'] = True


    if text and str(mavjud['yil']) in text:
        baza['yil'] = True

    xat_sanasi = '01.01.2000'

    pattern = r'.*?(\d{2}).*?\s+(yanvar|fevral|mart|aprel|may|iyun|iyul|avgust|sentyabr|oktyabr|noyabr|dekabr)\s+(\d{4})-y\.'
    if text:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            match = re.search(pattern, text)
            if match:
                kun, oy_nomi, yil = match.groups()
                oy = oylar[oy_nomi.lower()]
                xat_sanasi = f"{int(kun):02d}.{oy}.{yil}"
                if xat_sanasi == str(mavjud['xat_sanasi']):
                    baza['xat_sanasi'] = True
            else:
                print("Sana topilmadi.")

    #######################################

    aniqlangan_sana = mavjud['aniqlangan_sana']
    aniqlangan_sana_dt = datetime.strptime(aniqlangan_sana, "%d.%m.%Y")
    xat_sanasi_dt = datetime.strptime(xat_sanasi, "%d.%m.%Y")

    # Taqqoslash
    if xat_sanasi_dt >= aniqlangan_sana_dt:
        baza['aniqlangan_sana'] = True
    #######################################################
    boshliq_shablon = r"boshqarma.*?boshlig.*?i"
    if text:
        matches = re.findall(boshliq_shablon, text, re.IGNORECASE)
        for match in matches:
            baza['boshqarma_boshligi']=True
    ########################QRCODE##############################################
    
        #print("QR-kod hujjatda topilmadi.")
    ########################################################

    print(f'inn= {inn}')
    for kalit, qiymat in baza.items():
        #post = get_object_or_404(Excelupload, pk=request.POST['id'])

        if not qiymat:
            print(f"❌ {kalit} topilmadi.")
    return baza


#tekshirish('1710', '311858341', 'chaqiriq', '12-korxona', '2024', '10.06.2025', '09.06.2025', 'xat.pdf')
#tekshirish('1703', '301158341', 'chaqiriq', '12-korxona', '2024', '10.06.2025', '09.06.2025', 'xat.pdf')
#tekshirish('1710', '999999999', 'chaqiriq', '12-korxona', '2024', '10.06.2025', '09.06.2025', 'xat.pdf')
#tekshirish('1710', '888888888', 'chaqiriq', '12-korxona', '2024', '10.06.2025', '09.06.2025', 'xat.pdf')
