from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=User) #once a new user has been created, a corresponding profile will also be created

def create_profile(sender, instance, created, **kwargs):
    if created: #if user has been created
        Profile.objects.create(user=instance) #create profile





@receiver(post_save, sender=User)

def save_profile(sender, instance, **kwargs): #method for saving profile
    instance.profile.save()

