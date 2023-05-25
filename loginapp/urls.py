from django.urls import path
from . import views
urlpatterns = [
    path("", views.base),
    path('check/', views.home, name='home'),
    path('check/<secret_key>', views.index),
    path('qr/', views.qr),
    path('ceramic/admin', views.admin, name='admin')
]
