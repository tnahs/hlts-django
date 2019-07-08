import pytest
from django.contrib.auth import get_user_model

from ..serializers import TagSerializer


@pytest.fixture
@pytest.mark.django_db
def user():
    email = "user@email.com"
    password = "password"
    return get_user_model().objects.create_user(email=email, password=password)


@pytest.mark.django_db
class TestTagSerializer:
    pass

    # serializer_class = TagSerializer
    #
    # name = "tag"
    # data = {"name": name}
    #
    # def test_create(self, user):
    #
    #     serializer = self.serializer_class(data=self.data)
    #
    #     assert serializer.is_valid()
