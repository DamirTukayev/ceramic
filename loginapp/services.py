from django.urls import reverse
from configs.settings import MEDIA_ROOT, HOSTNAME
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


def set_url():
    code = randint(1, 40000)
    return code

def get_cookie(request):
    try:
        username = request.COOKIES["username"]
        return username
    finally:
        return None


def check_status(username):
    user = User.objects.get(username=username)
    if user.is_superuser==True:
        return True


def generate_qr():
    code = set_url()
<<<<<<< HEAD
    url = f'{HOSTNAME}/check/{code}/'
=======
    url = f'185.111.106.153/check/{code}'
>>>>>>> origin/deploy
    img = qrcode.make(url)
    filename = f'{datetime.now().date()}.png'
    img.save(os.path.join(settings.MEDIA_ROOT, 'qr', filename))
    return cache.set('code', code)


def clearMedia():
    for image in os.listdir(MEDIA_ROOT):
        os.remove(os.path.join(MEDIA_ROOT + '/qr/', image))


scheduler = BackgroundScheduler()
<<<<<<< HEAD
scheduler.add_job(generate_qr, 'interval', seconds=27)
=======
scheduler.add_job(generate_qr, 'interval', seconds=60)
>>>>>>> origin/deploy
scheduler.add_job(clearMedia, 'cron', hour=0)
scheduler.start()
