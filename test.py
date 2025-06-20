from pdf2image import convert_from_path
from pytesseract import image_to_string
import os
# Agar poppler o'rnatilgan bo'lsa, yo'lini ko'rsating
poppler_path = r"D:\project\jarima\poppler\Library\bin" 
def ocrdan_1111_qidir(pdf_path):
    sahifalar = convert_from_path(pdf_path, poppler_path=poppler_path)
    for sahifa in sahifalar:
        matn = image_to_string(sahifa)
        if "1111" in matn:
            return True
    return False
# Foydalanish
pdf_fayl = "xat.pdf"
if ocrdan_1111_qidir(pdf_fayl):
    print("✅ OCR orqali '1111' topildi.")
else:
    print("❌ OCR orqali ham '1111' topilmadi.")