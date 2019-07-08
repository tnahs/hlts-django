import pathlib
import uuid

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models


from ..helpers import UpdateFieldsMixin


class UserManager(UpdateFieldsMixin, BaseUserManager):

    use_in_migrations = True

    def _create(self, email, password, **extra_fields):

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.clean()
        user.save()

        return user

    def create_user(self, email, password, **extra_fields):

        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_staff", False)

        return self._create(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):

        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create(email, password, **extra_fields)

    def update(self, instance, **data):

        fields = ["email", "first_name", "last_name", "theme"]

        instance = self.update_fields(instance, data, fields)
        instance.clean()
        instance.save()

        return instance


class User(AbstractBaseUser, PermissionsMixin):
    """ References:
    https://docs.djangoproject.com/en/2.2/topics/auth/customizing/
    https://github.com/tmm/django-username-email/blob/master/cuser/models.py
    https://testdriven.io/blog/django-custom-user-model/ """

    THEME_CHOICES = [(0, "Default"), (1, "Dark"), (2, "Warm")]
    THEME_DEFAULT = 0

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField("e-mail", max_length=128, unique=True)
    first_name = models.CharField(max_length=128, blank=True)
    last_name = models.CharField(max_length=128, blank=True)
    theme = models.IntegerField(choices=THEME_CHOICES, default=THEME_DEFAULT)

    # password = models.CharField ... via AbstractBaseUser
    # last_login = models.DateTimeField ... via AbstractBaseUser
    # is_superuser = models.BooleanField ... via PermissionsMixin
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # QUESTION: Add date_created ?
    # QUESTION: When is this timestamped ?

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"

    objects = UserManager()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"<{self.__class__.__name__}:{self.email}>"

    # def set_password(): ... via AbstractBaseUser
    # def check_password(): ... via AbstractBaseUser

    # via AbstractUser
    def clean(self):
        # super().clean() isn't called here because AbstractBaseUser normalizes
        # using the .normalize_username() method instead of .normalize_email().
        self.email = self.__class__.objects.normalize_email(self.email)

    @property
    def display_name(self):
        if self.first_name or self.last_name:
            return " ".join([self.first_name, self.last_name])
        return self.email

    @property
    def dir_media(self):
        # MEDIA_ROOT/user_<pk>/
        return pathlib.Path(f"user_{self.pk}/")

    @property
    def dir_images(self):
        return self.dir_media / "images"

    @property
    def dir_audios(self):
        return self.dir_media / "audios"

    @property
    def dir_videos(self):
        return self.dir_media / "videos"

    @property
    def dir_documents(self):
        return self.dir_media / "documents"

    @property
    def dir_misc(self):
        return self.dir_media / "misc"
