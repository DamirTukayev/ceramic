from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from .models import Visit
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from datetime import datetime, timedelta, date
from .services import generate_qr, get_cookie
from django.urls import reverse
from django.core.cache import cache
from django.template import loader


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
                    response = redirect(reverse('home'))
                    response.set_cookie('username', username, expires=expiration_date)
                    return response
                else:
                    # Return an 'invalid login' error message.
                    return HttpResponse("Invalid login.")

                # If request method is GET, show the login form

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
from django.db.models import Q



def home(request):

    user_id = request.user.id
    username = request.user.username
    user = User.objects.get(id=user_id)
    current_date = date.today()
    todayVisit = Visit.objects.filter(Q(user=user) & Q(date=current_date))
    if todayVisit.exists()==False:
        visit = Visit.objects.create(user=user)
        visit.save()
    message = f"Пользователь {username}, сегодня авторизовался"

    template = loader.get_template('loginapp/success.html')
    context = {'message': message}
    return HttpResponse(template.render(context, request))


@user_passes_test(lambda u: u.is_superuser)
def qr(request):
    date = datetime.now().date()
    image = f'{date}.png'
    return render(request, 'loginapp/qr.html', {'image': image})
