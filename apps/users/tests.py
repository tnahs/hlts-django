import pathlib

import pytest
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError


@pytest.mark.django_db
class TestUser:

    model = get_user_model()

    email = "user@email.com"
    first_name = "firstname"
    last_name = "lastname"
    password = "password"
    theme = 1
    fields = {
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "theme": theme,
    }

    def test_create_user(self):
        """ Test full creation of a user. """

        user = self.model.objects.create_user(**self.fields)

        assert user.email == self.email
        assert user.check_password(self.password) is True
        assert user.first_name == self.first_name
        assert user.last_name == self.last_name
        assert user.theme == self.theme
        assert user.is_staff is False
        assert user.is_superuser is False

        # Test __str__, __repr__ and display_name return strings.
        assert isinstance(user.__str__(), str)
        assert isinstance(user.__repr__(), str)
        assert isinstance(user.display_name, str)

        # Test user media directories.
        assert user.dir_media == pathlib.Path(f"user_{user.pk}")
        assert user.dir_images == user.dir_media / "images"
        assert user.dir_audios == user.dir_media / "audios"
        assert user.dir_videos == user.dir_media / "videos"
        assert user.dir_documents == user.dir_media / "documents"
        assert user.dir_misc == user.dir_media / "misc"

    def test_create_user_minimum_requirements(self):
        """ Test create user with e-mail and password only. """

        user = self.model.objects.create_user(email=self.email, password=self.password)

        assert user.email == self.email
        assert user.check_password(self.password) is True

        # Test display_name returns string.
        assert isinstance(user.display_name, str)

    def test_create_superuser(self):
        """ Test full creation of a superuser. """

        user = self.model.objects.create_superuser(**self.fields)

        assert user.email == self.email
        assert user.check_password(self.password) is True
        assert user.first_name == self.first_name
        assert user.last_name == self.last_name
        assert user.is_staff is True
        assert user.is_superuser is True

        # Test __str__, __repr__ and display_name return strings.
        assert isinstance(user.__str__(), str)
        assert isinstance(user.__repr__(), str)
        assert isinstance(user.display_name, str)

    def test_create_superuser_minimum_requirements(self):
        """ Test create user with e-mail and password only. """

        user = self.model.objects.create_superuser(
            email=self.email, password=self.password
        )

        assert user.email == self.email
        assert user.check_password(self.password) is True
        assert user.is_staff is True
        assert user.is_superuser is True

        # Test display_name returns string.
        assert isinstance(user.display_name, str)

    def test_create_superuser_fail(self):
        """ Test superuser always has is_staff=True and is_superuser=True. """

        extra_fields = {"is_staff": False, "is_superuser": True}
        with pytest.raises(ValueError):
            self.model.objects.create_superuser(
                email=self.email, password=self.password, **extra_fields
            )

        extra_fields = {"is_staff": True, "is_superuser": False}
        with pytest.raises(ValueError):
            self.model.objects.create_superuser(
                email=self.email, password=self.password, **extra_fields
            )

    def test_normalize_email(self):
        """ Test e-mails is normalized to maintain unique usernames. """

        non_normalized_email = "user@EMAIL.com"
        user = self.model.objects.create_user(
            email=non_normalized_email, password=self.password
        )

        assert user.email == non_normalized_email.lower()

    def test_user_with_email_exists(self):
        """ Test e-mail is unique. """

        self.model.objects.create_user(email=self.email, password=self.password)
        with pytest.raises(IntegrityError):
            self.model.objects.create_user(email=self.email, password=self.password)

    '''
    TODO: These validations might need to be done at the Serializer level.s

    from django.core import exceptions

    def test_user_missing_email(self):
        """ Test e-mail is required. """

        with pytest.raises(exceptions.ValidationError):
            self.model.objects.create_user(email=None, password=self.password)

    def test_user_invalid_email(self):
        """ Test e-mail is valid format. """

        invalid_email = "useremailcom"

        with pytest.raises(exceptions.ValidationError):
            self.model.objects.create_user(email=invalid_email, password=self.password)
    '''
