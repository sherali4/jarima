from django.contrib import admin
from django.forms import ModelForm, ValidationError
from .models import Dalolatnoma, Xodim, Topshiriq, Hisobot, Hisobotdavri, Excelupload

class HisobotForm(ModelForm):
    class Meta:
        model = Hisobot
        fields = '__all__'

class HisobotdavriForm(ModelForm):
    class Meta:
        model = Hisobotdavri
        fields = '__all__'
class TopshiriqForm(ModelForm):
    class Meta:
        model = Topshiriq
        fields = '__all__'

    def clean_tugash_sanasi(self):
        tugash_sanasi = self.cleaned_data.get('tugash_sanasi')
        from django.utils import timezone
        if tugash_sanasi and tugash_sanasi < timezone.localdate():
            raise ValidationError("Tugatish sanasi bugungi kundan oldin bo'lishi mumkin emas.")
        return tugash_sanasi


class XodimAdmin(admin.ModelAdmin):
    list_display = ('ism', 'familiya', 'ishlayapti')
    search_fields = ('ism', 'familiya')
    list_filter = ('ishlayapti',)
    class Meta:
        db_table = ''
        managed = True
        verbose_name = 'Xodim'
        verbose_name_plural = 'Xodimlar'
class TopshiriqAdmin(admin.ModelAdmin):
    form = TopshiriqForm
    list_display = ('nomi', 'bajarilgan', 'tugash_sanasi', 'yaratilgan_vaqti', 'yangilangan_vaqti')
    search_fields = ('nomi', 'tavsif')
    list_filter = ('bajarilgan', 'tugash_sanasi')
    filter_horizontal = ('masullar',)
    class Meta:
        
        db_table = ''
        managed = True
        verbose_name = 'Topshiriq'
        verbose_name_plural = 'Topshiriqlar'
class DalolatnomaAdmin(admin.ModelAdmin):
    list_display = ('okpo', 'inn', 'soato4', 'yaratilgan_vaqti', 'yangilangan_vaqti')
    search_fields = ('okpo', 'inn', 'soato4')
    list_filter = ('yaratilgan_vaqti', 'yangilangan_vaqti')

    def __str__(self):
        return super().__str__()

class HisobotAdmin(admin.ModelAdmin):
    list_display = ('nomi',)

    def __str__(self):
        return super().__str__()

class HisobotdavriAdmin(admin.ModelAdmin):
    list_display = ('nomi', 'name', 'tugash_sanasi',)

    def __str__(self):
        return super().__str__()
    
class ExceluploadAdmin(admin.ModelAdmin):
    list_display = ('okpo', 'inn', 'xat_sanasi',)

    def __str__(self):
        return super().__str__()
admin.site.register(Xodim, XodimAdmin)
admin.site.register(Topshiriq, TopshiriqAdmin)
admin.site.register(Hisobot, HisobotAdmin)
admin.site.register(Hisobotdavri, HisobotdavriAdmin)
admin.site.register(Excelupload, ExceluploadAdmin)
admin.site.register(Dalolatnoma, DalolatnomaAdmin)