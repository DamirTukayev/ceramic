import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'djangFEESESFESFEFSEfseesfoBigDick-inseqz-vusb9u'

DEBUG = False

ALLOWED_HOST = ['http://185.111.106.153/']
STATIC_DIR = os.path.join(BASE_DIR, 'static')
STATICFILES_DIR = [STATIC_DIR]
STATIC_ROOT = os.path.join(BASE_DIR, 'static')