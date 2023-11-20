from django.db import models
from django.contrib.auth.models import User


class Api(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=150)
    sid = models.CharField(max_length=150)
    number = models.CharField(max_length=25)

    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class List(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    
    status = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Lead(models.Model):
    list = models.ForeignKey(List, on_delete=models.CASCADE)
    number = models.CharField(max_length=25)
    name = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=100)
    status = models.CharField(max_length=20)

    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (self.number + ' | ' + self.status)