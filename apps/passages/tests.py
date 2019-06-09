import pytest

from django.core.management import call_command

from .models import Passage


@pytest.mark.django_db
class TestPassageModel:

    def _load_dev_fixtures(self):
        call_command("loaddata", "fixtures/dev_defaults.json")

    def test_save(self):
        self._load_dev_fixtures()
        call_command("loaddata", "fixtures/dev_defaults.json")
        body = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        passage = Passage.objects.create(body=body, owner_id=1)
        assert passage.body == body
