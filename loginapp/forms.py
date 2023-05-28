from django import forms
from .models import User

class UserFilterForm(forms.Form):
    users = forms.ModelChoiceField(queryset=User.objects.all(), empty_label='Выберите пользователя')
