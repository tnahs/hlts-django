from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import (Tag, Collection, Node, Text, Image)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ("id", "name")
        read_only_fields = ("id", )


class CollectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Collection
        fields = ("id", "name")
        read_only_fields = ("id", )


#


class NodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Node
        fields = ("notes", "in_trash", "is_starred", "source",
                  "tags", "collections", "origin")


class TextSerializer(NodeSerializer):

    class Meta:
        model = Text
        fields = ("uuid", "body") + NodeSerializer.Meta.fields


class ImageSerializer(NodeSerializer):

    class Meta:
        model = Image
        fields = ("file", "name", "description") + NodeSerializer.Meta.fields


#


class NodesSerializer(serializers.ModelSerializer):

    texts = TextSerializer(many=True)
    images = ImageSerializer(many=True)
    tags = TagSerializer(many=True)
    collections = TagSerializer(many=True)

    class Meta:
        model = get_user_model()
        fields = ("texts", "images", "tags", "collections")
