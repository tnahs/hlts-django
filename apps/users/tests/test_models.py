import pathlib

import pytest
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError


@pytest.mark.django_db
class TestUser:

    model = get_user_model()

    email = "user@email.com"
    password = "password"
    first_name = "firstname"
    last_name = "lastname"
    theme = 1

    def test_create_user(self):
        """ Test full creation of a user. """

        fields = {
            "email": self.email,
            "password": self.password,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "theme": self.theme,
        }

        user = self.model.objects.create_user(**fields)

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

    def test_create_user_minimum(self):
        """ Test create user with e-mail and password only. """

        fields = {"email": self.email, "password": self.password}

        user = self.model.objects.create_user(**fields)

        assert user.email == self.email
        assert user.check_password(self.password) is True

        # Test display_name returns string.
        assert isinstance(user.display_name, str)

    def test_create_superuser(self):
        """ Test full creation of a superuser. """

        fields = {
            "email": self.email,
            "password": self.password,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "theme": self.theme,
        }

        user = self.model.objects.create_superuser(**fields)

        assert user.email == self.email
        assert user.check_password(self.password) is True
        assert user.first_name == self.first_name
        assert user.last_name == self.last_name
        assert user.theme == self.theme
        assert user.is_staff is True
        assert user.is_superuser is True

        # Test __str__, __repr__ and display_name return strings.
        assert isinstance(user.__str__(), str)
        assert isinstance(user.__repr__(), str)
        assert isinstance(user.display_name, str)

    def test_create_superuser_minimum(self):
        """ Test create user with e-mail and password only. """

        fields = {"email": self.email, "password": self.password}

        user = self.model.objects.create_superuser(**fields)

        assert user.email == self.email
        assert user.check_password(self.password) is True
        assert user.is_staff is True
        assert user.is_superuser is True

        # Test display_name returns string.
        assert isinstance(user.display_name, str)

    def test_create_superuser_fail(self):
        """ Test superuser always has is_staff=True and is_superuser=True. """

        fields = {
            "email": self.email,
            "password": self.password,
            "is_staff": False,
            "is_superuser": True,
        }
        with pytest.raises(ValueError):
            self.model.objects.create_superuser(**fields)

        fields = {
            "email": self.email,
            "password": self.password,
            "is_staff": True,
            "is_superuser": False,
        }
        with pytest.raises(ValueError):
            self.model.objects.create_superuser(**fields)

    def test_create_unique_email(self):
        """ Test e-mail is unique. """

        fields = {"email": self.email, "password": self.password}

        self.model.objects.create_user(**fields)
        with pytest.raises(IntegrityError):
            self.model.objects.create_user(**fields)

    def test_update(self):

        fields = {"email": self.email, "password": self.password}
        user = self.model.objects.create_user(**fields)

        email = "user@email.com"
        password = "password"
        first_name = "firstname"
        last_name = "lastname"
        theme = 1

        updated_fields = {
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
            "theme": theme,
        }

        updated = self.model.objects.update(user, **updated_fields)

        assert updated.pk == user.pk
        assert updated.email == email
        assert updated.check_password(password) is True
        assert updated.first_name == first_name
        assert updated.last_name == last_name
        assert updated.theme == theme

    def test_update_unique_email(self):

        existing_email = "user-existing@email.com"

        fields = {"email": existing_email, "password": self.password}
        self.model.objects.create_user(**fields)

        fields = {"email": self.email, "password": self.password}
        user = self.model.objects.create_user(**fields)

        with pytest.raises(IntegrityError):
            self.model.objects.update(user, email=existing_email)

    def test_normalize_email(self):
        """ Test e-mails is normalized to maintain unique usernames. """

        non_normalized_email = "user@EMAIL.com"
        user = self.model.objects.create_user(
            email=non_normalized_email, password=self.password
        )

        assert user.email == non_normalized_email.lower()
