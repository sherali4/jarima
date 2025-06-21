from datetime import datetime
import json
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.urls import reverse_lazy
from django.utils import timezone
import openpyxl
import pandas as pd
from django.views.generic.edit import UpdateView
from ish.models import Dalolatnoma, Topshiriq, Xodim, Excelupload, Hisobot, Hisobotdavri
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from .forms import DalolatnomaForm, ExceluploadForm, ExceluploadUpdateForm, KorxonaForm, TopshiriqForm, CustomUserForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from own.tekshir import tekshirish
import os
from .forms import FoydalanuvchiRoyxatForm

viloyat = ['1703', '1706', '1708', '1710', '1712', '1714', '1718', '1722', '1724', '1726', '1727', '1730', '1733']
tuman = ['1710207', '1710212', '1710220', '1710224', '1710229', '1710232', '1710233', '1710234', '1710235', '1710237', '1710242', '1710245', '1710250', '1710401']

def index(request):
    topshiriqlar = Topshiriq.objects.all()

    for task in topshiriqlar:
        if task.tugash_sanasi:
            total_days = (task.tugash_sanasi - task.yaratilgan_vaqti.date()).days
            passed_days = (timezone.localdate() - task.yaratilgan_vaqti.date()).days
            if total_days > 0:
                progress = int(passed_days / total_days * 100)
                progress = max(0, min(progress, 100))  # 0 dan 100 gacha chegaralash
            else:
                progress = 100 if task.bajarilgan else 0
        else:
            progress = 0
        task.progress = progress
        print(f"Task: {task.nomi}, Progress: {progress}%")

    context = {
        'topshiriqlar': topshiriqlar,
        #'progress': progress,
    }
    return render(request, 'ish/index.html', context)



def signup_view1(request):
    if request.method == 'POST':
        form = FoydalanuvchiRoyxatForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = FoydalanuvchiRoyxatForm()
    return render(request, 'auth/signup.html', {'form': form})


def signup_view(request):
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')  # manzilga moslang
    else:
        form = CustomUserForm()
    return render(request, 'auth/signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')





def topshiriq_create_view(request):
    xodimlar = Xodim.objects.all()
    # Xodimlar ro'yxatini shablonga uzatish
    if request.method == 'POST':
        form = TopshiriqForm(request.POST, request.FILES)
        if form.is_valid():
            topshiriq = form.save(commit=False)
            topshiriq.user = request.user
            topshiriq.save()
            form.save_m2m()
            return redirect('index')
    else:
        form = TopshiriqForm()
    return render(request, 'ish/topshiriq_create.html', {'form': form, 'xodimlar': xodimlar})
def jarima(request):
    return render(request, 'ish/jarima.html')

@login_required
def upload_excel(request):
    if request.method == 'POST':
        form = ExceluploadForm(request.POST, request.FILES)
        # Formani tekshirish
        if form.is_valid():
            hisobot = form.cleaned_data.get('hisobot') # Hisobot turini olish
            hisobotdavri = form.cleaned_data.get('hisobot_davri') # Hisobot davrini olish
            
            excel_file = request.FILES['file']

            # Faylni .xlsx ekanligiga tekshiruv
            if not excel_file.name.endswith('.xlsx'):
                messages.error(request, "Faqat .xlsx formatdagi fayllar qabul qilinadi.")
                return redirect('upload_excel')

            try:
                df = pd.read_excel(excel_file)
            except Exception as e:
                messages.error(request, f"Faylni o'qishda xatolik: {e}")
                return redirect('upload_excel')

            # Har bir qatordagi ma'lumotni saqlash
            for _, row in df.iterrows():
                okpo_val = row.get('okpo', '')
                inn_val = row.get('inn', '')

                # BAZADAN TEKSHIRUV: ushbu okpo va inn mavjudmi?
                #mavjud = Excelupload.objects.filter(okpo=okpo_val, inn=inn_val).exists()
                
                mavjud = Excelupload.objects.filter(okpo=okpo_val, inn=inn_val, hisobot_nomi=hisobot, xat_turi = "ko'rsatma", faoliyatsiz =False, dalolatnomasi_mavjudligi = False).exists()
                sudga_xat = Excelupload.objects.filter(okpo=okpo_val, inn=inn_val, hisobot_nomi=hisobot, xat_turi = "chaqiriq", faoliyatsiz =False, dalolatnomasi_mavjudligi = False).exists()
                if mavjud and not sudga_xat:
                    xat_turi = 'chaqiriq'
                elif sudga_xat:
                    xat_turi = 'sudga xat'
                else:
                    xat_turi = 'ko\'rsatma'
                soato4=str(row.get('soato'))[:4]
                # agar dalolatnoma mavjud bo'lsa, xat turi 'dalolatnoma' bo'ladi
                dalolatnoma_mavjud = Dalolatnoma.objects.filter(okpo=okpo_val, inn=inn_val, soato4=soato4).exists()
                

                Excelupload.objects.create(
                    hisobot_nomi=hisobot,
                    hisobot_davri=hisobotdavri,
                    okpo=row.get('okpo', ''),
                    inn=row.get('inn', ''),
                    soato=row.get('soato', ''),
                    nomi=row.get('nomi', ''),
                    sababi=row.get('sababi', ''),
                    opf=row.get('opf', ''),
                    xat_turi=xat_turi,
                    dalolatnomasi_mavjudligi=True if dalolatnoma_mavjud else False,                                        
                )
                


            messages.success(request, "Fayl muvaffaqiyatli yuklandi va ma'lumotlar saqlandi.")
            return redirect('upload_excel')
        else:
            messages.error(request, "Formada xatolik bor, iltimos tekshirib qayta urinib ko'ring.")
    else:
        form = ExceluploadForm()
    return render(request, 'ish/upload_excel.html', {'form': form})

def load_hisobot_davri(request):
    hisobot_id = request.GET.get('hisobot')
    davrlar = Hisobotdavri.objects.filter(nomi_id=hisobot_id).order_by('tugash_sanasi')
    data = [{'id': d.id, 'name': d.name} for d in davrlar]
    return JsonResponse(data, safe=False)


def excelupload_listp(request):
    uploads = Excelupload.objects.all().order_by('-aniqlangan_sanasi')  # so‘nggi yuklanganlar birinchi
    return render(request, 'ish/excelupload_list.html', {'uploads': uploads})
@login_required
def excelupload_list(request):
    if len(request.user.soato) == 4 and request.user.soato in viloyat:
        tabl = Excelupload.objects.filter(faoliyatsiz=False).filter(tasdiqlangan=False).exclude(xat_turi="sudga xat").filter(soato__startswith = request.user.soato).order_by('-aniqlangan_sanasi')  
    else:
        tabl = Excelupload.objects.filter(faoliyatsiz=False).filter(tasdiqlangan=False).exclude(xat_turi="sudga xat").order_by('-aniqlangan_sanasi')  
    if request.method == 'POST':
        record_id = request.POST.get('record_id')
        pdf_file = request.FILES
        record = get_object_or_404(Excelupload, id=record_id)
        
        form = ExceluploadUpdateForm(request.POST, request.FILES, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, "Ma'lumot yangilandi.")
            return redirect('excelupload_list')
        else:
            messages.error(request, "Formada xatolik bor, iltimos tekshiring.")
    else:
        form = None

    records = Excelupload.objects.all().order_by('-aniqlangan_sanasi') 

    record_forms = []
    for rec in records:
        record_forms.append({
            'record': rec,
            'form': ExceluploadUpdateForm(instance=rec)
        })
    return render(request, 'ish/excelupload_list.html', {'record_forms': record_forms, 'ruyxat': tabl})

def item_detail1(request, id):
    korxona = get_object_or_404(Excelupload, id=id)
    context = {
        'korxona': korxona,
        'nomer': id,
    }
    return render(request, 'ish/item_detail.html', context=context)


class KorxonaUpdateView(UpdateView):
    model = Excelupload
    fields = ['xat_sanasi', 'pdf_fayli']  
    template_name = 'ish/item_detail.html'  
    success_url = reverse_lazy('excelupload_list')  # Forma muvaffaqiyatli topshirilganda qayerga yo‘naltirish
    def form_valid(self, form):
        instance = form.save(commit=False)
        soato4 = instance.soato[:4]
        inn = instance.inn
        xat_turi = instance.xat_turi
        hisobot_turi = instance.hisobot_nomi
        yil = str(instance.xat_sanasi)[:4]
        aniqlangan_sana = datetime.strptime(str(instance.aniqlangan_sanasi), "%Y-%m-%d").strftime("%d.%m.%Y")
        xat_sanasi = form.cleaned_data['xat_sanasi']
        xat_sanasi = datetime.strptime(str(form.cleaned_data['xat_sanasi']), "%Y-%m-%d").strftime("%d.%m.%Y")
        fayl_nomi = form.cleaned_data['pdf_fayli']
        tekshirish_natijasi = ''
        if fayl_nomi:
            kengaytma = os.path.splitext(fayl_nomi.name)[1]  
            if kengaytma.lower() == '.pdf':
                tekshirish_natijasi = tekshirish(soato4, inn, xat_turi, hisobot_turi, yil, aniqlangan_sana, xat_sanasi, fayl_nomi)
                #print(tekshirish_natijasi)
                json_str = json.dumps(tekshirish_natijasi, indent=4)
                #print(json_str)
                #original_dict = json.loads(json_str) ortga qaytarish
        instance.tekshirish_natijasi = json_str
        messages.info(self.request, '11111 korxonasi bo\'yicha pdf fayl yangilandi')
        messages.success(self.request, "pdf fayl muvaffaqiyatli yangilandi.")
        messages.warning(self.request, "pdf fayl muvaffaqiyatli yangilandi.")
        return super().form_valid(form)

def JarimaQilinmagan(request):
    jarima_qilinmagan = Excelupload.objects.filter(faoliyatsiz=False, xat_turi='chaqiriq').order_by('-aniqlangan_sanasi')
    return render(request, 'ish/jarima_qilinmagan.html', {'ruyxat': jarima_qilinmagan})

def Exceluploadtoexcel(request):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Jarima baza'
    sheet.append(['OKPO', 'INN', 'SOATO', 'Nomi', 'Sababi', 'OPF', 'Hisobot Nomi', 'Hisobot Davri', 'Faoliyatsiz', 'Xat Turi', 'Xat Sanasi', 'Aniqlangan Sanasi'])
    uploads = Excelupload.objects.all()
    if not uploads:
        messages.error(request, "Hozirda yuklangan ma'lumotlar mavjud emas.")
        return redirect('excelupload_list')

    for upload in uploads:
        sheet.append([
            upload.okpo,
            upload.inn,
            upload.soato,
            upload.nomi,
            upload.sababi,
            upload.opf,
            upload.hisobot_nomi,
            upload.hisobot_davri,
            'Ha' if upload.faoliyatsiz else 'Yo‘q',
            upload.xat_turi,
            upload.xat_sanasi.strftime('%Y-%m-%d') if upload.xat_sanasi else '',
            upload.aniqlangan_sanasi.strftime('%Y-%m-%d') if upload.aniqlangan_sanasi else '',
        ])

    # Excel faylni HTTP javobga yozish
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename=jarima_baza.xlsx'
    workbook.save(response)
    return response

class DalolatnomaUpdateView(UpdateView):
    model = Dalolatnoma
    fields = ['pdf_fayli', 'soato4']  # Qaysi maydonlar tahrirlanadi
    template_name = 'ish/dalolatnoma_update.html'  # BU YER MUHIM
    success_url = reverse_lazy('index')  # Forma muvaffaqiyatli topshirilganda qayerga yo‘naltirish

    def get_object(self, queryset=None):
        return get_object_or_404(Dalolatnoma, id=self.kwargs['pk'])
    def form_valid(self, form):
        dalolatnoma = form.save(commit=False)
        dalolatnoma.user = self.request.user
        dalolatnoma.save()
        messages.success(self.request, "Dalolatnoma muvaffaqiyatli yangilandi.")
        return super().form_valid(form)



def dalolatnoma_from_excelupload1(request, excel_id):
    excelupload = get_object_or_404(Excelupload, id=excel_id)
    initial_data = {
        'okpo': excelupload.okpo,
        'inn': excelupload.inn,
        'soato4': excelupload.soato,
        'nomi': excelupload.nomi,
    }

    if request.method == 'POST':
        form = DalolatnomaForm(request.POST, request.FILES)
        if form.is_valid():
            dalolatnoma = form.save(commit=False)
            dalolatnoma.user = request.user
            dalolatnoma.save()
            excelupload.dalolatnomasi_mavjudligi = True
            excelupload.save()
            return redirect('dalolatnoma_list')
    else:
        form = DalolatnomaForm(initial=initial_data)

    return render(request, 'ish/from_excel.html', {'form': form, 'excel': excelupload})


def dalolatnoma_from_excelupload(request, excel_id):
    excelupload = get_object_or_404(Excelupload, id=excel_id)

    initial_data = {
        'okpo': excelupload.okpo,
        'inn': excelupload.inn,
        'soato4': excelupload.soato,
        'nomi': excelupload.nomi,
    }

    if request.method == 'POST':
        form = DalolatnomaForm(request.POST, request.FILES)
        if form.is_valid():
            dalolatnoma = form.save(commit=False)
            dalolatnoma.user = request.user
            dalolatnoma.save()
            excelupload.dalolatnomasi_mavjudligi = True
            excelupload.save()
            return redirect('excelupload_list')
    else:
        form = DalolatnomaForm(initial=initial_data)

    return render(request, 'ish/from_excel.html', {'form': form, 'excel': excelupload})


def dalolatnoma_list(request):
    tabl = Dalolatnoma.objects.all().order_by('-id')  
    if request.method == 'POST':
        record_id = request.POST.get('record_id')
        pdf_file = request.FILES
        record = get_object_or_404(Dalolatnoma, id=record_id)
        form = DalolatnomaForm(request.POST, request.FILES, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, "Ma'lumot yangilandi.")
            return redirect('dalolatnoma_list')
        else:
            messages.error(request, "Formada xatolik bor, iltimos tekshiring.")
    else:
        form = None

    records = Dalolatnoma.objects.all().order_by('-id')  # so‘nggi yuklanganlar birinchi

    record_forms = []
    for rec in records:
        record_forms.append({
            'record': rec,
            'form': DalolatnomaForm(instance=rec)
        })
    return render(request, 'ish/dalolatnoma_list.html', {'record_forms': record_forms, 'ruyxat': tabl})
