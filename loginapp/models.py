from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Visit(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
