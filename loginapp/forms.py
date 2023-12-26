from django import forms
from .models import CustomUser



class UserFilterForm(forms.Form):
    users = forms.ModelChoiceField(queryset=CustomUser.objects.all(), required=False)

