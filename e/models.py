from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class EList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ELead(models.Model):
    elist = models.ForeignKey(EList, on_delete=models.CASCADE)
    email = models.CharField(max_length=25)
    status = models.IntegerField(default=0)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (self.email)

class EApi(models.Model):
    key = models.CharField(max_length=200)

class RequestID(models.Model):
    eapi = models.ForeignKey(EApi, on_delete=models.CASCADE)
    elist = models.ForeignKey(EList, on_delete=models.CASCADE, blank=True, null=True)
    requestid = models.IntegerField()
    processed = models.BooleanField(default=False)

class Result(models.Model):
    elist= models.ForeignKey(EList, on_delete=models.CASCADE, blank=True, null=True)
    email = models.CharField(max_length=200)
    format_check = models.BooleanField(default=False)
    smtp_check = models.BooleanField(default=False)
    dns_check = models.BooleanField(default=False)
    free_check = models.BooleanField(default=False)
    disposable_check = models.BooleanField(default=False)
    catch_all_check = models.BooleanField(default=False)
    result = models.CharField(max_length=100)
    error = models.CharField(max_length=100)