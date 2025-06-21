import re
from PyPDF2 import PdfReader

reader = PdfReader("xat.pdf")
matn_topildi = False
pattern_12korxona = r"12.*?korxona"
pattern_1korxona = r"12[^0-9].*?korxona"
pattern_rahbar = r"boshqarma.*?boshli"





for page in reader.pages:
    text = page.extract_text()
    
    
    if text and "113313" in text:
        inn = True
    
    
    if text:
        matches = re.findall(pattern_12korxona, text, re.IGNORECASE)
        for match in matches:
            print("12 korxona hisoboti:", match)
    

    if text:
        matches = re.findall(pattern_1korxona, text, re.IGNORECASE)
        for match in matches:
            print("1 korxona hisoboti:", match)
    

    if text:
        matches = re.findall(pattern_rahbar, text, re.IGNORECASE)
        for match in matches:
            print("rahbar:", match)

# PDF faylidan QR-kodlarni o'qish va matnni tekshirish
from pdf2image import convert_from_path
from pyzbar.pyzbar import decode
from PIL import Image

# PDF ni sahifalarga aylantirish
pages = convert_from_path("xat.pdf")

qrcode_found = False

for page_number, page in enumerate(pages, start=1):
    decoded_objects = decode(page)
    if decoded_objects:
        print(f"✅ QR-kod topildi, sahifa: {page_number}")
        for obj in decoded_objects:
            print("QR-kod mazmuni:", obj.data.decode("utf-8"))
        qrcode_found = True
        break  # Birinchi QR-kod topilgach, to‘xtatamiz

if not qrcode_found:
    print("❌ QR-kod topilmadi")

#Rasmdan qr-kodlarni o'qish
from pyzbar.pyzbar import decode
from PIL import Image

# Rasmni ochish
image = Image.open("qrcode_rasm.png")

# QR kodni o‘qish
decoded_objects = decode(image)

# Natijani chiqarish
for obj in decoded_objects:
    print("QR matni:", obj.data.decode('utf-8'))



if matn_topildi:
    print("✅ '11' raqami matnda mavjud.")
else:
    print("❌ '11' raqami topilmadi.")
pattern = r"12[^0-9].*?korxona"
