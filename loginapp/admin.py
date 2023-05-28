from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Visit


class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'first_name', 'last_name', 'last_login']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'groups']


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


class CustomVisitAdmin(admin.ModelAdmin):
    readonly_fields = ['date', 'arrival_time', 'leaving_time']


admin.site.register(Visit, CustomVisitAdmin)
