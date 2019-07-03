import pytest

# from rest_framework.test import RequestsClient

# client = RequestsClient()
# response = client.get('http://testserver/users/')
# assert response.status_code == 200

# from django.core import management

# @pytest.fixture(scope="session")
# def django_db_setup(django_db_setup, django_db_blocker):
#     with django_db_blocker.unblock():
#         management.call_command("loaddata", "fixtures/dev_data.json")

# TODO:
# 1. Each list view returns a proper response.
# 2. Each detail view returns a proper response.
# 3. Via Client each Serializer creates and updates expectedly.


@pytest.mark.django_db
class TestApi:
    def test_save(self):
        pass
