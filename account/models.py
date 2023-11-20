from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    address = models.CharField(max_length=30, blank=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=70, blank=True, null=True)
    postal_code = models.CharField(max_length=15, blank=True, null=True)
    dp = models.FileField(upload_to='uploads/profile/', blank=True, null=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class WerifierApi(models.Model):
    user= models.OneToOneField(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=30, blank=True, null=True)
    webhook = models.CharField(max_length=180, blank=True, null=True)

