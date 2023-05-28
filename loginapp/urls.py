from django.urls import path
from .views import base, home, index, qr, ceramic_admin_view
urlpatterns = [
    path("", base),
    path('check/', home, name='home'),
    path('check/<secret_key>', index),
    path('qr/', qr, name='qr'),
    path('ceramic/admin', ceramic_admin_view, name='admin'),
]
