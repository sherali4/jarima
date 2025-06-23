import re
from PyPDF2 import PdfReader
from datetime import datetime
import warnings

from ish.models import Excelupload

def tekshirish(soato4, inn, xat_turi, hisobot_turi, yil, aniqlangan_sana, xat_sanasi, fayl_nomi):
    mavjud = {
        "soato4": soato4,
        "inn": inn,
        "xat_turi": xat_turi,
        "hisobot_turi": hisobot_turi,
        "yil": yil,
        'aniqlangan_sana': aniqlangan_sana,
        'xat_sanasi': xat_sanasi,
    }

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

    oylar_uz = {
        'yanvar': '01', 'fevral': '02', 'mart': '03', 'aprel': '04', 'may': '05',
        'iyun': '06', 'iyul': '07', 'avgust': '08', 'sentabr': '09',
        'oktabr': '10', 'noyabr': '11', 'dekabr': '12'
    }

    hududlar_nomi = {
        '1703': 'andijon', '1706': 'buxoro', '1730': 'farg‘ona', '1708': 'jizzax',
        '1710': 'qashqadaryo', '1712': 'navoiy', '1714': 'namangan', '1718': 'samarqand',
        '1724': 'sirdaryo', '1722': 'surxondaryo', '1727': 'toshkent',
        '1733': 'xorazm', '1735': 'qoraqalpog‘iston respublikasi', '1726': 'toshkent shahar',
    }

    warnings.filterwarnings("ignore")
    reader = PdfReader(fayl_nomi)
    text = reader.pages[0].extract_text() or ""
    text_clean = text.replace('“', '').replace('”', '').replace('–', '-').lower()

    # === Tekshiruvlar ===
    if hududlar_nomi.get(mavjud['soato4'], '') in text_clean:
        baza['soato4'] = True

    if str(mavjud['inn']) in text_clean:
        baza['inn'] = True

    # xat_turi regex
    xat_turi_pattern = r"chaqiriq.*?xat" if mavjud['xat_turi'] == "chaqiriq" else r"ko‘?rsatma.*?xat"
    if re.search(xat_turi_pattern, text_clean, re.IGNORECASE):
        baza['xat_turi'] = True

    # hisobot_turi regex
    hisobot_patterns = {
        "1-korxona": r'1\s*[-]?\s*korxona',
        "12-korxona": r'12\s*[-]?\s*korxona',
        "1-moliya": r'1\s*[-]?\s*moliya',
        "12-moliya": r'12\s*[-]?\s*moliya',
        "fermer": r'fermer',
    }
    hisobot_regex = hisobot_patterns.get(mavjud['hisobot_turi'].lower())
    if hisobot_regex and re.search(hisobot_regex, text_clean, re.IGNORECASE):
        baza['hisobot_turi'] = True

    if str(mavjud['yil']) in text_clean:
        baza['yil'] = True

    # === Sana topish va taqqoslash ===
    sana_match = re.search(
        r'\b(\d{1,2})\s+(yanvar|fevral|mart|aprel|may|iyun|iyul|avgust|sentabr|oktabr|noyabr|dekabr)[^\d]+(\d{4})',
        text_clean
    )

    topilgan_sana = None
    if sana_match:
        kun, oy_uz, yil = sana_match.groups()
        oy = oylar_uz.get(oy_uz)
        if oy:
            topilgan_sana = f"{int(kun):02d}.{oy}.{yil}"
            if topilgan_sana == mavjud['xat_sanasi']:
                baza['xat_sanasi'] = True

    # aniqlangan_sana <= xat_sanasi bo‘lsa True
    try:
        aniqlangan_sana_dt = datetime.strptime(mavjud['aniqlangan_sana'], "%d.%m.%Y")
        if topilgan_sana:
            xat_sanasi_dt = datetime.strptime(topilgan_sana, "%d.%m.%Y")
            if xat_sanasi_dt >= aniqlangan_sana_dt:
                baza['aniqlangan_sana'] = True
    except Exception as e:
        print("Sana taqqoslashda xatolik:", e)

    # boshqarma boshlig‘i
    if re.search(r"boshqarma.*?boshlig.*?i", text_clean):
        baza['boshqarma_boshligi'] = True

    # === Natija chiqarish ===
    for kalit, qiymat in baza.items():
        if not qiymat:
            print(f"❌ {kalit} topilmadi.")

    return baza
