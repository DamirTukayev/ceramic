from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from .models import Visit
from django.contrib.auth.apps import AuthConfig

AuthConfig.verbose_name = ''

class CustomUserAdmin(UserAdmin):
    verbose_name_plural = "Мои пользователи и группы"
    list_display = ['username', 'first_name', 'last_name', 'last_login']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'groups']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

class CustomVisitAdmin(admin.ModelAdmin):
    readonly_fields = ['date', 'arrival_time', 'leaving_time', 'working_time', 'lateness', 'recycling']



admin.site.register(Visit, CustomVisitAdmin)


admin.site.unregister(Group)






admin.site.index_title = "Добро пожаловать в интерфейс администратора Ceramic Pro!"

admin.site.site_header = "Административная панель Ceramic Pro"

admin.site.site_title = "Админ панель"
