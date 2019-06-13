import pytest

from django.core.management import call_command

from .models import AppUser


@pytest.mark.django_db
class TestAppUserModel:

    def _load_dev_fixtures(self):
        call_command("loaddata", "fixtures/dev_db.json")

    def test_save(self):
        self._load_dev_fixtures()
        username = "testuser"
        email = "testuser@email.com"
        user = AppUser.objects.create(username=username, email=email)
        assert user.username == username
        assert user.email == email
