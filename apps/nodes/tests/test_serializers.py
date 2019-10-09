import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate

from ..models import Tag
from ..serializers import TagSerializer
from ..views import TagsViewSet

"""
@pytest.fixture
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():

        email = "user@email.com"
        password = "password"
        user = get_user_model().objects.create_user(email=email, password=password)

        Tag.objects.create(user=user, name="tag")
"""

client = APIClient()


@pytest.fixture
def user():
    email = "user@email.com"
    password = "password"

    user = get_user_model().objects.create_user(email=email, password=password)

    client.login(username=email, password=password)

    return user


@pytest.fixture
def init_db_tags(user):

    tags = ["tag1", "tag2", "tag3"]

    for tag in tags:
        Tag.objects.create(user=user, name=tag)


@pytest.mark.django_db
class TestTagSerializer:
    def test_get_all(self, init_db_tags):

        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)

        url = reverse("tag-list")
        response = client.get(url)

        assert response.data == serializer.data
        assert response.status_code == status.HTTP_200_OK

    def test_get_obj(self, init_db_tags):

        tag = Tag.objects.first()
        serializer = TagSerializer(tag)

        url = reverse("tag-detail", args=[tag.pk])
        response = client.get(url)

        assert response.data == serializer.data
        assert response.status_code == status.HTTP_200_OK
