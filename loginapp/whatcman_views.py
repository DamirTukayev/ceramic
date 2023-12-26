from io import BytesIO

from django.contrib.auth import authenticate, login
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from openpyxl.workbook import Workbook

from .decorators import whatchman_required
from .forms import UserFilterForm
from .models import Visit


@whatchman_required
def whatchman_room(request):
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
        headers = ['Фамилия', 'Имя', 'Дата','Время прибытия', 'Время ухода', 'Время работы', 'Время опоздания', 'Переработки']
        ws.append(headers)
        for obj in visits:
            row = [obj.user.last_name, obj.user.first_name, obj.date, obj.arrival_time, obj.leaving_time, obj.working_time,
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
    return render(request, 'loginapp/admin/index.html', context)


def whatchman_login(request):
    if request.user.is_authenticated == False:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                response = redirect(reverse('room'))
                return response
    else:
        response = redirect(reverse('room'))
        return response
    return render(request, template_name='loginapp/login.html')
