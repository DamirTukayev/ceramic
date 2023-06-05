# Generated by Django 4.2.1 on 2023-06-04 17:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('loginapp', 'initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='visit',
            options={'verbose_name': 'Таблица посещений', 'verbose_name_plural': 'Таблица посещений'},
        ),
        migrations.AlterField(
            model_name='visit',
            name='arrival_time',
            field=models.TimeField(auto_now_add=True, verbose_name='Дата прихода'),
        ),
        migrations.AlterField(
            model_name='visit',
            name='date',
            field=models.DateField(auto_now_add=True, verbose_name='дата'),
        ),
        migrations.AlterField(
            model_name='visit',
            name='leaving_time',
            field=models.TimeField(blank=True, null=True, verbose_name=' Дата ухода'),
        ),
        migrations.AlterField(
            model_name='visit',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Юзер'),
        ),
    ]
