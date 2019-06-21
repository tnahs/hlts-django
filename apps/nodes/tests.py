import pytest

from django.core.management import call_command

from .models import Node


@pytest.mark.django_db
class TestNodeModel:

    def _load_dev_fixtures(self):
        call_command("loaddata", "fixtures/dev_db.json")

    def test_save(self):
        self._load_dev_fixtures()
        call_command("loaddata", "fixtures/dev_db.json")
        text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        node = Node.objects.create(text=text, user_id=1)
        assert node.text == text
