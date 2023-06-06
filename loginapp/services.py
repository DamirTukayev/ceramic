from django.urls import reverse
from configs.settings import MEDIA_ROOT
import qrcode
import os
from datetime import datetime
from django.conf import settings
from random import randint
from apscheduler.schedulers.background import BackgroundScheduler
from django.core.cache import cache
from .models import User
from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test
from .models import UniqueLink

def generate_unique_link():
    unique_link = UniqueLink.objects.create()
    return unique_link.code




def check_status(username):
    user = User.objects.get(username=username)
    if user.is_superuser==True:
        return True


def generate_qr():
    uuid = generate_unique_link()
    img = qrcode.make(f'http://185.111.106.153/check/{uuid}')
    filename = f'{datetime.now().date()}.png'
    img.save(os.path.join(settings.MEDIA_ROOT, 'qr', filename))



def clearMedia():
    for image in os.listdir(MEDIA_ROOT):
        os.remove(os.path.join(MEDIA_ROOT + '/qr/', image))


scheduler = BackgroundScheduler()
scheduler.add_job(generate_qr, 'interval', seconds=60)
scheduler.add_job(clearMedia, 'cron', hour=0)
scheduler.start()
