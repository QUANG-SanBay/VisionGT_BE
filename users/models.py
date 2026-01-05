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
    GENDER_CHOICES = [
        ('male', 'Nam'),
        ('female', 'Nữ'),
        ('other', 'Khác'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    
    role = models.CharField(max_length=20, choices=ROLES_CHOICES, default='customer')  # nếu is_staff = True thì role = admin
    # Override the save method to set role based on is_staff
    def save(self, *args, **kwargs):
        if self.is_staff:
            self.role = 'admin'
        super().save(*args, **kwargs)
    email = models.EmailField(unique=True)  # Ensure email is unique
    USERNAME_FIELD = 'email'  # Use email as the unique identifier for authentication
    REQUIRED_FIELDS = ['username']  # Username is still required, but not used for authentication
    def __str__(self):
        return str(self.email)
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()