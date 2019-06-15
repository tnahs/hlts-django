import pytest

from django.core.management import call_command

from .models import Text


@pytest.mark.django_db
class TestTextModel:

    def _load_dev_fixtures(self):
        call_command("loaddata", "fixtures/dev_db.json")

    def test_save(self):
        self._load_dev_fixtures()
        call_command("loaddata", "fixtures/dev_db.json")
        body = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        text = Text.objects.create(body=body, user_id=1)
        assert text.body == body
