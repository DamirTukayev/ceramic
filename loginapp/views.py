from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from .models import Visit
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from datetime import datetime
from .services import generate_qr
from django.urls import reverse
from django.core.cache import cache
from django.template import loader

def base(request):
    return render(request, "loginapp/base.html")

def index(request, secret_key):
    code = cache.get('code')
    if secret_key == str(code):
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect to a success page.
                return redirect(reverse('home'))
            else:
                # Return an 'invalid login' error message.
                return HttpResponse("Invalid login.")

            # If request method is GET, show the login form
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
    username = 'Юзер'
    user = 0
    try:
        user_id = request.user.id
        username = request.user.username
        user = User.objects.get(id=user_id)
        visit = Visit.objects.create(user=user)
        visit.save()
    finally:
        message = f"Пользователь {username}, сегодня авторизовался"
    
        template = loader.get_template('loginapp/success.html')
        context = {'message': message}
        return HttpResponse(template.render(context, request))

@user_passes_test(lambda u: u.is_superuser)
def qr(request):
    date = datetime.now().date()
    image = f'{date}.png'
    return render(request, 'loginapp/qr.html', {'image': image})