from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User, AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.
class Xodim(models.Model):
    ism = models.CharField(max_length=100)
    familiya = models.CharField(max_length=100)
    ishlayapti = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.ism} {self.familiya}"

class Topshiriq(models.Model):
    nomi = models.CharField(max_length=200)
    tavsif = models.TextField()
    bajarilgan = models.BooleanField(default=False)
    tugash_sanasi = models.DateField(null=True, blank=True)
    yaratilgan_vaqti = models.DateTimeField(auto_now_add=True)
    yangilangan_vaqti = models.DateTimeField(auto_now=True)
    file = models.FileField(upload_to='topshiriqlar/', null=True, blank=True)
    user = models.ForeignKey('ish.CustomUser', on_delete=models.CASCADE, related_name='topshiriqlar', null=True, blank=True)
    masullar = models.ManyToManyField(Xodim, related_name='topshiriqlar', blank=True)
    class Meta:
        verbose_name = 'Topshiriq'
        verbose_name_plural = 'Topshiriqlar'
        ordering = ['-yaratilgan_vaqti']

    def clean(self):
        super().clean()
        if self.tugash_sanasi and self.tugash_sanasi < timezone.localdate():
            raise ValidationError({'tugash_sanasi': "Tugatish sanasi bugungi kundan oldin bo'lishi mumkin emas."})


    def __str__(self):
        return self.nomi

class Excelupload(models.Model):
    okpo = models.CharField(max_length=8)
    inn = models.CharField(max_length=9)
    soato = models.CharField(max_length=20)
    nomi = models.CharField(max_length=400)
    sababi = models.CharField(max_length=200)
    opf = models.CharField(max_length=10)
    hisobot_nomi = models.CharField(max_length=200)
    hisobot_davri = models.CharField(max_length=50)
    faoliyatsiz = models.BooleanField(default=False)
    xat_turi = models.CharField(max_length=50)
    xat_sanasi = models.DateField(null=True, blank=True)
    kiritgan = models.ForeignKey('ish.CustomUser', on_delete=models.CASCADE, related_name='excel_uploads', null=True, blank=True)
    aniqlangan_sanasi = models.DateField(auto_now_add=True)
    pdf_fayli = models.FileField(upload_to='jarima_xatlari', null=True, blank=True)
    tasdiqlangan = models.BooleanField(default=False)
    tasdiqlangan_vaqt = models.DateTimeField(null=True, blank=True)  # remove auto_now_add
    dalolatnomasi_mavjudligi = models.BooleanField(default=False)
    nazoratdan_chiqarilgan = models.BooleanField(default=False)
    izoh = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.tasdiqlangan and not self.tasdiqlangan_vaqt:
            self.tasdiqlangan_vaqt = timezone.now()
        elif not self.tasdiqlangan:
            self.tasdiqlangan_vaqt = None
        super().save(*args, **kwargs)

    def __str__(self):
        return super().__str__()
    
    # def __str__(self):
        # return f"Excel fayli: {self.file.name} (Yuklangan: {self.uploaded_at})"
    

class Hisobot(models.Model):
    nomi = models.CharField(max_length=255)

    def __str__(self):
        return self.nomi
class Hisobotdavri(models.Model):
    name = models.CharField(max_length=100)
    tugash_sanasi = models.DateField(null=True, blank=True)
    nomi = models.ForeignKey(Hisobot, on_delete=models.CASCADE, related_name='hisobot_davri')
    def __str__(self):
        return f"{self.name} ({self.nomi})"


class CustomUser(AbstractUser):
    telefon = models.CharField(max_length=20, blank=True, null=True)
    yosh = models.PositiveIntegerField(blank=True, null=True)
    soato = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.username

class Dalolatnoma(models.Model):
    okpo = models.CharField(max_length=8)
    inn = models.CharField(max_length=9)
    soato4 = models.CharField(max_length=20)
    yaratilgan_vaqti = models.DateTimeField(auto_now_add=True)
    yangilangan_vaqti = models.DateTimeField(auto_now=True)
    izoh = models.TextField(blank=True, null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='dalolatnomalar', null=True, blank=True)
    dalolatnoma_fayli = models.FileField(upload_to='dalolatnomalar/', null=True, blank=True)
    class Meta:
        verbose_name = 'Dalolatnoma'
        verbose_name_plural = 'Dalolatnomalar'
        ordering = ['-yaratilgan_vaqti']
    

    def __str__(self):
        return f"{self.okpo}-{self.inn} ({self.soato4})"