from django.contrib.auth import authenticate, login

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from datetime import datetime
from .services import generate_qr
from django.urls import reverse
from django.core.cache import cache

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
    return HttpResponseNotFound(f'как вы сюда попали? вот {code}')


def home(request):
    return HttpResponse('успех')

def qr(request):
    date = datetime.now().date()
    image = f'{date}.png'
    return render(request, 'loginapp/qr.html', {'image': image})