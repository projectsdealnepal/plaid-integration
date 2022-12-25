from django.db import models
from datetime import datetime


# Create your models here.

class User(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    username = models.CharField(max_length=30, primary_key=True)
    password = models.CharField(max_length=100)
    email = models.EmailField()
    creation_date = models.DateTimeField(blank=True, default=datetime.now())
    last_login = models.DateTimeField(blank=True, default=datetime.now())

    def __str__(self):
        return self.username


class Accounts(models.Model):
    acc_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # acc_key = models.CharField(max_length=50, primary_key=True, null=False)
    bank_name = models.CharField(max_length=50, null=True, blank=True)
    # account_id = models.CharField(max_length=50, primary_key=True)
    # account = models.CharField(max_length=30, null=True, blank=True)
    user_name = models.CharField(max_length=30, null=True, blank=True)
    user_pass = models.CharField(max_length=30, null=True, blank=True)
    institution_id = models.CharField(max_length=30, null=True)
    verified = models.BooleanField(default=0, blank=True)
    user_id = models.CharField(max_length=100, null=True)
    auth_token = models.CharField(max_length=255, null=True)


