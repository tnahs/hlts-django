import pytest
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError


@pytest.mark.django_db
class TestUser:

    user_model = get_user_model()
    email = "user@email.com"
    password = "password"

    def test_user_create(self):

        user = self.user_model.objects.create_user(
            email=self.email, password=self.password
        )

        assert user.email == self.email
        assert user.check_password(self.password) is True
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_superuser_create(self):

        user = self.user_model.objects.create_superuser(
            email=self.email, password=self.password
        )

        assert user.email == self.email
        assert user.check_password(self.password) is True
        assert user.is_staff is True
        assert user.is_superuser is True

    def test_superuser_fail(self):

        extra_fields = {"is_staff": False, "is_superuser": True}

        with pytest.raises(ValueError):
            self.user_model.objects.create_superuser(
                email=self.email, password=self.password, **extra_fields
            )

        extra_fields = {"is_staff": True, "is_superuser": False}

        with pytest.raises(ValueError):
            self.user_model.objects.create_superuser(
                email=self.email, password=self.password, **extra_fields
            )

    def test_user_with_email_exists(self):

        self.user_model.objects.create_user(email=self.email, password=self.password)

        with pytest.raises(IntegrityError):
            self.user_model.objects.create_user(
                email=self.email, password=self.password
            )

    def test_user_missing_email(self):

        with pytest.raises(ValueError):
            self.user_model.objects.create_user(email=None, password=self.password)

    def test_normalize_email(self):

        email = "user@EMAIL.com"

        user = self.user_model.objects.create_user(email=email, password=self.password)

        assert user.email == email.lower()

    """
    def test_user_invalid_password(self):

        # FIXME Does not raise ValidationError...

        with pytest.raises(exceptions.ValidationError):
            self.user_model.objects.create_user(email=self.email, password="123")

    def test_user_invalid_email(self):

        # FIXME Does not raise ValidationError...

        with pytest.raises(exceptions.ValidationError):
            self.user_model.objects.create_user(
                email=self.email, password=self.password
            )
    """
