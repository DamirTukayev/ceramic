from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'first_name', 'last_name', 'last_login']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'groups']

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)