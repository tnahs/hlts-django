# import ast

from rest_framework import serializers

from . import models


def update_instance(instance, data: dict, attrs: list):
    """
    Performs...
        instance.attr = data.get("attr", instance.attr)
    for every item in attrs.
    """

    for attr in attrs:
        value_original = getattr(instance, attr)
        value_new = data.get(attr, value_original)
        setattr(instance, attr, value_new)

    return instance


class TagSerializer(serializers.Serializer):

    id = serializers.ReadOnlyField()

    name = serializers.CharField(max_length=64)

    apiurl = serializers.HyperlinkedRelatedField(
        source="id", read_only=True, view_name="tags-detail")

    def validate_name(self, value):

        # PUT and PATCH
        if self.instance:
            if self.instance.name == value:
                return value

        # POST, PUT and PATCH
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

        updated_instance = update_instance(
            instance, validated_data, ["name"])

        updated_instance.save()
        return updated_instance


class CollectionSerializer(serializers.Serializer):

    id = serializers.ReadOnlyField()

    name = serializers.CharField(max_length=64)
    color = serializers.CharField(allow_blank=True, max_length=32)
    description = serializers.CharField(allow_blank=True)

    apiurl = serializers.HyperlinkedRelatedField(
        source="id", read_only=True, view_name="collections-detail")

    def validate_name(self, value):

        # PUT and PATCH
        if self.instance:
            if self.instance.name == value:
                return value

        # POST, PUT and PATCH
        try:
            models.Collection.objects.get(name=value)
        except models.Collection.DoesNotExist:
            return value
        else:
            raise serializers.ValidationError(
                f"Collection '{value}' already exists."
            )

    def create(self, validated_data):
        user = self.context["request"].user
        tag = models.Collection.objects.create(
            user=user,
            **validated_data
        )
        return tag

    def update(self, instance, validated_data):

        updated_instance = update_instance(
            instance, validated_data, ["name", "color", "description"])

        updated_instance.save()
        return updated_instance


class NestedSlugRelatedField(serializers.SlugRelatedField):

    def get_queryset(self):
        user = self.context["request"].user
        return self.queryset.filter(user=user)


class NodeSerializer(serializers.Serializer):

    id = serializers.ReadOnlyField()

    uuid = serializers.ReadOnlyField()
    text = serializers.CharField(allow_blank=True)
    file = serializers.FileField()

    source = serializers.StringRelatedField()
    notes = serializers.CharField(allow_blank=True)
    tags = NestedSlugRelatedField(
        slug_field="name", many=True, queryset=models.Tag.objects.all()
    )
    collections = NestedSlugRelatedField(
        slug_field="name", many=True, queryset=models.Collection.objects.all()
    )

    origin = NestedSlugRelatedField(
        slug_field="name", queryset=models.Origin.objects.all()
    )
    in_trash = serializers.BooleanField()
    is_starred = serializers.BooleanField()

    related = serializers.HyperlinkedRelatedField(
            many=True, read_only=True, view_name="nodes-detail")

    # # topics
    # # count_seen
    # # count_query
    # # date_created
    # # date_modified

    # apiurl = serializers.HyperlinkedRelatedField(
    #     source="id", read_only=True, view_name="nodes-detail")
