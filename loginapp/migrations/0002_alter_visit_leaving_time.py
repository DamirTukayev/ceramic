# Generated by Django 4.2 on 2023-05-25 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loginapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='visit',
            name='leaving_time',
            field=models.TimeField(blank=True),
        ),
    ]