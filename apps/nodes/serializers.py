# import ast

import django
from django.db.models import QuerySet
# from django.contrib.auth import get_user_model
from rest_framework import serializers, exceptions

from . import models


class TagSerializer(serializers.Serializer):

    id = serializers.ReadOnlyField()
    name = serializers.CharField()
    apiurl = serializers.HyperlinkedRelatedField(
        source="id", read_only=True, view_name="tag-detail")

    def validate_name(self, value):

        try:
            models.Tag.objects.get(name=value)
        except models.Tag.DoesNotExist:
            return value
        else:
            raise serializers.ValidationError(f"Tag '{value}' already exists.")

    def create(self, validated_data):
        user = self.context["request"].user
        tag = models.Tag.objects.create(
            user=user,
            **validated_data
        )
        return tag

    def update(self, instance, validated_data):
        print(validated_data)
        instance.name = validated_data.get("name", instance.name)
        return instance
