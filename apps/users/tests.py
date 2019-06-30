import pytest

from django.core.management import call_command

from .models import User


@pytest.mark.django_db
class TestUserModel:
    def _load_dev_fixtures(self):
        call_command("loaddata", "fixtures/dev_db.json")

    def test_save(self):
        self._load_dev_fixtures()
        name = "testuser"
        user = User.objects.create(name=name)
        assert user.name == name
