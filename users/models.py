from django.db import models
from django.contrib.auth.models import AbstractUser # Import AbstractUser to extend the default user model
from django.db.models.signals import post_save # Import post_save signal để 
# Create your models here.

class CustomUser(AbstractUser):
    # Add any additional fields you want for your custom user model here
    ROLES_CHOICES = [
        ('admin', 'Admin'),
        ('customer', 'Customer'),
    ]
    role = models.CharField(max_length=20, choices=ROLES_CHOICES, default='customer')
    def __str__(self):
        return str(self.username)