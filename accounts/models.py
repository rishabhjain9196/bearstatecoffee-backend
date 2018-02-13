from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import MyUserManager

# Create your models here.


class BaseModel(models.Model):
    """
        This is for storing commonly used fields.
    """
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now_add=True)


class MyUser(AbstractBaseUser, PermissionsMixin, BaseModel):
    """
        This is a User model to create some extra fields.
    """
    email = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'

    objects = MyUserManager()
