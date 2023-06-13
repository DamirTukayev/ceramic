from io import BytesIO

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from .models import Visit, UniqueLink
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from datetime import datetime, timedelta, date
from .services import check_status
from django.urls import reverse
from django.core.cache import cache
from django.template import loader
from django.db.models import Q
from .forms import UserFilterForm
from openpyxl import Workbook



def get_last():
    code = UniqueLink.objects.all().order_by('-id').first()
    return code.code


def superuser_required(view_func):
    def decorator_func(request, *args, **kwargs):
        code = get_last()
        actual_decorator = user_passes_test(
            lambda u: u.is_superuser,
            login_url=f'/check/{code}'
        )
        return actual_decorator(view_func)(request, *args, **kwargs)

    return decorator_func


def base(request):
    return render(request, "loginapp/base.html")


def index(request, secret_key):
    code = get_last()
    if secret_key == code:
        if request.user.is_authenticated == False:
            if request.method == 'POST':
                username = request.POST['username']
                password = request.POST['password']
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    expiration_date = datetime.now() + timedelta(days=7)

                    if check_status(username):
                        response = redirect(reverse('admin'))
                    else:
                        response = redirect(reverse('home'))
                    response.set_cookie('username', username, expires=expiration_date)
                    return response
                else:
                    # Return an 'invalid login' error message.
                    return HttpResponse("Invalid login.")

                # If request method is GET, show the login form

        else:
            if check_status(request.user.username):
                return redirect(reverse('admin'))
            else:
                return redirect(reverse('home'))
        return render(request, 'loginapp/login.html')
    message = "Отсканируйте QR снова"
    template = loader.get_template('loginapp/success.html')
    url = code
    context = {
        'message': message,
        'url': url
    }

    return HttpResponse(template.render(context, request))


def home(request):
    user_id = request.user.id
    username = request.user.username
    user = User.objects.get(id=user_id)
    current_date = date.today()
    todayVisit = Visit.objects.filter(Q(user=user) & Q(date=current_date))
    if todayVisit.exists() == False:
        visit = Visit.objects.create(user=user)
        visit.save()
        message = f"Пользователь {username}, сегодня авторизовался"
    else:
        visit = todayVisit[0]
        visit.leaving_time = datetime.now().time()
        visit.save()
        message = f"Пользователь {username}, успешно вышел"
    template = loader.get_template('loginapp/success.html')
    context = {'message': message}
    return HttpResponse(template.render(context, request))


@user_passes_test(lambda u: u.is_superuser)
def qr(request):
    date = datetime.now().date()
    image = f'{date}.png'
    return render(request, 'loginapp/qr.html', {'image': image})


@superuser_required
def ceramic_admin_view(request):
    form = UserFilterForm(request.GET or None)
    search_query = request.GET.get('search', '')

    # Retrieve the date filter from the request GET parameters
    since_date_filter = request.GET.get('date1', '')
    before_date_filter = request.GET.get('date2', '')
    sort_by = request.GET.get('sort_by', '')

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

    if since_date_filter != '':
        visits = visits.filter(date__gte=since_date_filter)
        if before_date_filter != '':
            visits = visits.filter(date__gte=since_date_filter, date__lte=before_date_filter)
        else:
            visits = visits.filter(date=since_date_filter)
    else:
        if before_date_filter != '':
            visits = visits.filter(date__lte=before_date_filter)
    if form.is_valid():
        selected_user = form.cleaned_data['users']
        if selected_user:
            visits = visits.filter(user=selected_user)

    if request.GET.get('download'):
        if search_query:  # Применяем фильтрацию поиска только если есть параметр поиска
            visits = visits.filter(
                Q(user__first_name__icontains=search_query) |
                Q(date__icontains=search_query)
            )

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

    context = {
        'visits': visits,
        'form': form,
        'search_query': search_query,
        'since_date_filter': since_date_filter,
        'before_date_filter': before_date_filter,
        'sort_by': sort_by
    }
    return render(request, 'loginapp/admin.html', context)
