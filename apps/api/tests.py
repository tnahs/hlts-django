import pytest

# from django.core import management

# @pytest.fixture(scope="session")
# def django_db_setup(django_db_setup, django_db_blocker):
#     with django_db_blocker.unblock():
#         management.call_command("loaddata", "fixtures/dev_data.json")


@pytest.mark.django_db
class TestApi:
    def test_save(self):
        pass
