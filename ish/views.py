from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils import timezone
import pandas as pd
from django.views.generic.edit import UpdateView
from ish.models import Topshiriq, Xodim, Excelupload, Hisobot, Hisobotdavri
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from .forms import ExceluploadForm, ExceluploadUpdateForm, TopshiriqForm, ExceluploadForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required




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

from .forms import FoydalanuvchiRoyxatForm

def signup_view1(request):
    if request.method == 'POST':
        form = FoydalanuvchiRoyxatForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = FoydalanuvchiRoyxatForm()
    return render(request, 'auth/signup.html', {'form': form})

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import CustomUserForm

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
    # Jarima sahifasini ko'rsatish
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
                
                mavjud = Excelupload.objects.filter(okpo=okpo_val, inn=inn_val, hisobot_nomi=hisobot, xat_turi = "ko'rsatma", faoliyatsiz =False).exists()
                sudga_xat = Excelupload.objects.filter(okpo=okpo_val, inn=inn_val, hisobot_nomi=hisobot, xat_turi = "chaqiriq", faoliyatsiz =False).exists()
                if mavjud and not sudga_xat:
                    xat_turi = 'chaqiriq'
                elif sudga_xat:
                    xat_turi = 'sudga xat'
                else:
                    xat_turi = 'ko\'rsatma'


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

def excelupload_list(request):
    tabl = Excelupload.objects.filter(tasdiqlangan=False, faoliyatsiz=False).filter(xat_sanasi__isnull=True).filter(pdf_fayli='').exclude(xat_turi="sudga xat").order_by('-aniqlangan_sanasi')  # tasdiqlanmagan va faoliyatsiz bo'lmaganlar
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

    records = Excelupload.objects.all().order_by('-aniqlangan_sanasi')  # so‘nggi yuklanganlar birinchi

    record_forms = []
    for rec in records:
        record_forms.append({
            'record': rec,
            'form': ExceluploadUpdateForm(instance=rec)
        })
    

    return render(request, 'ish/excelupload_list.html', {'record_forms': record_forms, 'ruyxat': tabl})

def item_detail(request, id):
    korxona = get_object_or_404(Excelupload, id=id)
    context = {
        'korxona': korxona,
        'nomer': id,
    }
    return render(request, 'ish/item_detail.html', context=context)





class KorxonaUpdateView(UpdateView):
    model = Excelupload    
    fields = ['xat_sanasi', 'pdf_fayli']  # Қайси майдонлар таҳрирланади
    template_name = 'ish/item_detail.html'  # Формани кўрсатувчи шаблон
    success_url = reverse_lazy('index')  # Янгиланганидан кейин қайта йўналиш

