from rest_framework import serializers

from .models import AppUser
from ..nodes.serializers import TextSerializer, ImageSerializer


class UserNodesSerializer(serializers.ModelSerializer):

    texts = TextSerializer(many=True)
    images = ImageSerializer(many=True)

    class Meta:
        model = AppUser
        fields = ["texts", "images", ]