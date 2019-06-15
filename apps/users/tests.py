import pytest

from django.core.management import call_command

from .models import User


@pytest.mark.django_db
class TestUserModel:

    def _load_dev_fixtures(self):
        call_command("loaddata", "fixtures/dev_db.json")

    def test_save(self):
        self._load_dev_fixtures()
        email = "testuser@email.com"
        user = User.objects.create(email=email)
        assert user.email == email
