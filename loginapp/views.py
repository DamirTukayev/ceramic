from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from .models import Visit
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from datetime import datetime, timedelta, date
from .services import generate_qr, get_cookie, check_status
from django.urls import reverse
from django.core.cache import cache
from django.template import loader
from django.db.models import Q
from .forms import UserFilterForm


def base(request):
    return render(request, "loginapp/base.html")


def index(request, secret_key):
    code = cache.get('code')
    if secret_key == str(code):
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
            if check_status:
                return redirect(reverse('admin'))
            else:
                return redirect(reverse('home'))
        return render(request, 'loginapp/login.html')
    message = f"Отсканируйте QR снова"
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

@user_passes_test(lambda u: u.is_superuser)
def admin(request):
    form = UserFilterForm(request.GET or None)
    search_query = request.GET.get('search', '')


    # Retrieve the date filter from the request GET parameters

    date_filter = request.GET.get('date', '')
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
            Q(user__first_name__icontains=search_query) |  # Filter by name containing the search query
            Q(date__icontains=search_query)  # Filter by date containing the search query
        )

    if date_filter:
        visits = visits.filter(date=date_filter)


    if form.is_valid():
        selected_user = form.cleaned_data['users']
        if selected_user:
            visits = visits.filter(user=selected_user)

    context = {'visits': visits, 'form': form}
    return render(request, 'loginapp/admin.html', context)
