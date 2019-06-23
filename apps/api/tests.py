import pytest

from django.core.management import call_command


@pytest.mark.django_db
class TestApi:
    def _load_dev_fixtures(self):
        call_command("loaddata", "fixtures/dev_db.json")

    def test_save(self):
        self._load_dev_fixtures()
        pass
