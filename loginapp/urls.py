from django.urls import path
from .views import base, home, index, qr, ceramic_admin_view
from .whatcman_views import whatchman_room, whatchman_login
urlpatterns = [
    path("", base, name='base'),
    path('login/', whatchman_login, name='whatchman_login'),
    path('lk/', whatchman_room, name='room'),
    path('check/', home, name='home'),
    path('check/<secret_key>', index),
    path('qr/', qr, name='qr'),
    path('ceramic/admin', ceramic_admin_view, name='admin'),

]
