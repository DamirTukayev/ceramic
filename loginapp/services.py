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
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
import logging
from django.http import HttpResponse, HttpResponseNotFound
from django.template import loader
from .models import Visit
from openpyxl import Workbook
from django.db.models import Q
from io import BytesIO

LOGIN_TEMPLATE = 'loginapp/login.html'

logger = logging.getLogger(__name__)


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
    url = f'{HOSTNAME}/{code}/'
    img = qrcode.make(url)
    filename = f'{datetime.now().date()}.png'
    img.save(os.path.join(settings.MEDIA_ROOT, 'qr', filename))
    return cache.set('code', code)


def clearMedia():
    for image in os.listdir(MEDIA_ROOT):
        os.remove(os.path.join(MEDIA_ROOT + '/qr/', image))

def superuser_required(view_func):
    code = cache.get('code')

    actual_decorator = user_passes_test(
        lambda u: u.is_superuser,
        login_url=f'/check/{code}'
    )
    return actual_decorator(view_func)    

def check_authentication(request):
    if request.user.is_authenticated:
        if check_status(request.user.username):
            return redirect(reverse('admin'))
        else:
            return redirect(reverse('home'))
    return render(request, LOGIN_TEMPLATE)   

def handle_login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)

        if check_status(username):
            return redirect(reverse('admin'))
        else:
            return redirect(reverse('home'))
    else:
        logger.error(f"Invalid login attempt for username: {username}")
        return HttpResponse("Invalid login.") 

def show_login_form(request):
    return check_authentication(request)

def show_qr_scan_again(request, code):
    message = f"Отсканируйте QR снова"
    template = loader.get_template('loginapp/success.html')
    url = code
    context = {
        'message': message,
        'url': url
    }
    return HttpResponse(template.render(context, request))

def handle_user_login(user, username, current_date):
    visit = Visit.objects.create(user=user)
    visit.save()
    message = f"Пользователь {username}, сегодня авторизовался"
    template = loader.get_template('loginapp/success.html')
    context = {'message': message}
    return HttpResponse(template.render(context, request))

def handle_user_logout(visit, username):
    visit.leaving_time = datetime.now().time()
    visit.save()
    message = f"Пользователь {username}, успешно вышел"
    template = loader.get_template('loginapp/success.html')
    context = {'message': message}
    return HttpResponse(template.render(context, request))

def get_filtered_visits(request, search_query, since_date_filter, before_date_filter, sort_by):
    visits = Visit.objects.all()
    visits = visits.order_by('-date')

    if sort_by == 'first_name':
        visits = visits.order_by('user__first_name')
    elif sort_by == 'last_name':
        visits = visits.order_by('user__last_name')
    elif sort_by == 'date':
        visits = visits.order_by('date')
    elif sort_by == 'arrival_time':
        visits = visits.order_by('arrival_time')
    elif sort_by == 'living_time':
        visits = visits.order_by('leaving_time')
    elif sort_by == 'working_time':
        visits = visits.order_by('working_time')

    if search_query:
        visits = visits.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(date__icontains=search_query)
        )

    if since_date_filter:
        visits = visits.filter(date__gte=since_date_filter)
        if before_date_filter:
            visits = visits.filter(date__gte=since_date_filter, date__lte=before_date_filter)
        else:
            visits = visits.filter(date=since_date_filter)
    else:
        if before_date_filter:
            visits = visits.filter(date__lte=before_date_filter)

    return visits

def download_visits_report(visits, search_query):
    # Создаем новый файл Excel и добавляем данные
    wb = Workbook()
    ws = wb.active
    headers = ['Фамилия', 'Имя', 'Время прибытия', 'Время ухода', 'Время работы', 'Время опоздания', 'Переработки']
    ws.append(headers)
    for obj in visits:
        row = [obj.user.last_name, obj.user.first_name, obj.arrival_time, obj.leaving_time, obj.working_time,
               obj.lateness, obj.recycling]
        ws.append(row)

    # Генерируем файл Excel в памяти и создаем HTTP-ответ для скачивания файла
    file_stream = BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=report.xlsx'
    response.write(file_stream.read())
    return response


scheduler = BackgroundScheduler()
scheduler.add_job(generate_qr, 'interval', seconds=60)
scheduler.add_job(clearMedia, 'cron', hour=0)
scheduler.start()
