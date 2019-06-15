import pathlib

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """ via.https://testdriven.io/blog/django-custom-user-model/ """

    THEME_CHOICES = [
        (0, "Default"),
        (1, "Dark"),
    ]

    theme = models. IntegerField(
        choices=THEME_CHOICES,
        default=0
    )

    @property
    def dir_media(self):
        # MEDIA_ROOT/user_<pk>/
        return pathlib.Path(f"user_{self.pk}/")

    @property
    def dir_images(self):
        # MEDIA_ROOT/user_<pk>/images/
        return self.dir_media / "images"


class Notification(models.Model):

    user = models.ForeignKey(get_user_model(),
                            related_name="notifications",
                            on_delete=models.CASCADE)


class Task(models.Model):

    user = models.ForeignKey(get_user_model(),
                            related_name="tasks",
                            on_delete=models.CASCADE)
