from django.urls import path
from . import views
urlpatterns = [
    path('check/', views.home, name='home'),
    path('check/<secret_key>', views.index),
    path('qr/', views.qr)
]
