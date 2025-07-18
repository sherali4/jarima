# Generated by Django 5.2.3 on 2025-06-14 19:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ish', '0004_excelupload_tasdiqlangan_vaqt_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='excelupload',
            name='dalolatnomasi_mavjudligi',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='Dalolatnoma',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('okpo', models.CharField(max_length=8)),
                ('inn', models.CharField(max_length=9)),
                ('soato4', models.CharField(max_length=20)),
                ('yaratilgan_vaqti', models.DateTimeField(auto_now_add=True)),
                ('yangilangan_vaqti', models.DateTimeField(auto_now=True)),
                ('izoh', models.TextField()),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dalolatnomalar', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Dalolatnoma',
                'verbose_name_plural': 'Dalolatnomalar',
                'ordering': ['-yaratilgan_vaqti'],
            },
        ),
    ]
