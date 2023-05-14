from configs.settings import MEDIA_ROOT
import qrcode
import os
from datetime import datetime
from django.conf import settings
from random import randint
from apscheduler.schedulers.background import BackgroundScheduler
from django.core.cache import cache

def set_url():
    code = randint(1, 40000)
    return code




def generate_qr():
    code = set_url()
    url = f'http://127.0.0.1:8000/check/{code}/'
    img = qrcode.make(url)
    filename = f'{datetime.now().date()}.png'
    img.save(os.path.join(settings.MEDIA_ROOT, filename))
    return cache.set('code', code)


def clearMedia():
    for image in os.listdir(MEDIA_ROOT):
        os.remove(os.path.join(MEDIA_ROOT, image))


scheduler = BackgroundScheduler()
scheduler.add_job(generate_qr, 'interval', seconds=10)
scheduler.add_job(clearMedia, 'cron', hour=0)
scheduler.start()
