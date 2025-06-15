from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Hisobot, Topshiriq, Excelupload, Hisobotdavri




class FoydalanuvchiRoyxatForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
        labels = {
            'username': 'Foydalanuvchi nomi',
            'password1': 'Parol',
            'password2': 'Parolni tasdiqlang',
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

        self.fields['username'].help_text = "Faqat harflar, raqamlar va @/./+/-/_ belgilariga ruxsat etiladi."
        self.fields['password1'].help_text = (
            "Parol kamida 8 belgidan iborat bo‘lishi, oddiy so‘z bo‘lmasligi va raqamlardan iborat emasligi lozim."
        )
        self.fields['password2'].help_text = "Tekshirish uchun parolni qayta kiriting."




from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'telefon', 'soato', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'



class TopshiriqForm(forms.ModelForm):
    class Meta:
        model = Topshiriq
        fields = ['nomi', 'tavsif', 'tugash_sanasi', 'file', 'masullar']
        widgets = {
            'nomi': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Topshiriq nomini kiriting'}),
            'tavsif': forms.Textarea(attrs={'rows': 4}),
            'tugash_sanasi': forms.DateInput(attrs={'type': 'date'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'masullar': forms.CheckboxSelectMultiple(),
        }
        labels = {
            'nomi': 'Topshiriq nomi',
            'tavsif': 'Tavsif',
            'bajarilgan': 'Bajarilgan',
            'tugash_sanasi': 'Tugatish sanasi',
            'file': 'Fayl',
            'masullar': 'Masullar',
        }
class ExceluploadForm(forms.Form):
    file = forms.FileField(label='Excel faylini yuklash', help_text='Excel faylini tanlang va yuklang.', required=True)
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file.name.endswith('.xlsx'):
            raise forms.ValidationError('Faqat .xlsx formatidagi fayllarni yuklash mumkin.')
        return file

class ExceluploadForm(forms.Form):
    file = forms.FileField(label='Excel fayl (.xlsx)', widget=forms.ClearableFileInput(attrs={'accept': '.xlsx'}))
    hisobot = forms.ModelChoiceField(
        queryset=Hisobot.objects.all(),
        label='Hisobot turini tanlash',

        empty_label='Hisobot turini tanlang',
        help_text='Yuklangan faylga mos hisobotni tanlang.',
        required=False
    )
    hisobot_davri = forms.ModelChoiceField(
        queryset=Hisobotdavri.objects.all(),
        label='Hisobot davrini tanlash',
        empty_label='Hisobot davrini tanlang',
        help_text='Yuklangan faylga mos hisobot davrini tanlang.',
        required=False
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agar form data kelsa, hisobot asosida hisobot_davri querysetini yangilash:
        if 'hisobot' in self.data:
            try:
                hisobot_id = int(self.data.get('hisobot'))
                self.fields['hisobot_davri'].queryset = Hisobotdavri.objects.filter(nomi_id=hisobot_id).order_by('tugash_sanasi')
            except (ValueError, TypeError):
                pass  # noto‘g‘ri id yoki bo‘sh bo‘lsa
        elif self.initial.get('hisobot'):
            hisobot_id = self.initial.get('hisobot').id
            self.fields['hisobot_davri'].queryset = Hisobotdavri.objects.filter(nomi_id=hisobot_id).order_by('tugash_sanasi')


class ExceluploadUpdateForm(forms.ModelForm):
    class Meta:
        model = Excelupload
        fields = [
            'okpo', 'inn', 'soato', 'nomi', 'hisobot_nomi', 'hisobot_davri',
            'xat_turi', 'xat_sanasi', 'pdf_fayli',
        ]
        widgets = {
            'xat_sanasi': forms.DateInput(attrs={'type': 'date'}),
        }
        exclude = ['okpo']

        def __init__(self, *args, **kwargs):
                super(ExceluploadForm, self).__init__(*args, **kwargs)
                self.fields['nomi'].widget.attrs['readonly'] = True

class KorxonaForm(forms.ModelForm):
    class Meta:
        model = Excelupload
        fields = 'xat_sanasi',

        widgets = {
            'xat_sanasi': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder': 'Xat sanasini kiriting'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.template_pack = 'bootstrap5'  # Bu borligi kerak
        self.helper.add_input(Submit('submit', 'Saqlash'))