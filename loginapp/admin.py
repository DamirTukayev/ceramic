from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import Visit, CustomUser
from django.contrib.auth.apps import AuthConfig

AuthConfig.verbose_name = 'Сотрудники'


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    verbose_name_plural = "Мои пользователи и группы"
    list_display = ['username', 'first_name', 'last_name', 'last_login', 'is_whatchman']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'groups']
    fieldsets = (
        (None, {'fields': ('username', 'password', 'is_whatchman')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )


admin.site.register(CustomUser, CustomUserAdmin)


class CustomVisitAdmin(admin.ModelAdmin):
    readonly_fields = ['date', 'arrival_time', 'leaving_time', 'working_time', 'lateness', 'recycling']


# list_filter = ['date', 'arrival_time', 'leaving_time']
admin.site.register(Visit, CustomVisitAdmin)
admin.site.unregister(Group)
admin.site.index_title = "Добро пожаловать в интерфейс администратора Ceramic Pro!"
admin.site.site_header = "Административная панель Ceramic Pro"
admin.site.site_title = "Админ панель"
