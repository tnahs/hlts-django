from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser


class AppUser(AbstractUser):
    pass


class Notification(models.Model):
    owner = models.ForeignKey(get_user_model(),
                              related_name="notifications",
                              on_delete=models.CASCADE)


class Task(models.Model):
    owner = models.ForeignKey(get_user_model(),
                              related_name="tasks",
                              on_delete=models.CASCADE)
