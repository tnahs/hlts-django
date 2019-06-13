from rest_framework import serializers

from .models import (Origin, Individual, Source, Tag, Collection, Topic, Node,
    Text, Image)


# class OriginSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Origin
#         fields = ["name", ]


# class TagSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Tag
#         fields = ["name", ]


# class CollectionSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Collection
#         fields = ["name", "color", "description", ]


# class IndividualSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Individual
#         fields = ["name", "first_name", "last_name", ]  # "aka", ]


# class SourceSerializer(serializers.ModelSerializer):

#     individuals = IndividualSerializer()

#     class Meta:
#         model = Source
#         fields = ["name", "url", "date", "notes", "individuals", ]


class TagRelatedField(serializers.RelatedField):

    @property
    def _owner_id(self):
        return self.context['request'].user.pk

    def get_queryset(self):
        return Tag.objects.filter(owner_id=self._owner_id)

    def to_representation(self, value):
        return value.name

    def to_internal_value(self, data):
        # FIXME this returns a more than one result error.
        # `get() returned more than one Tag -- it returned 3!`
        # TODO: Need to append user before save method.
        try:
            obj, created = self.get_queryset().get_or_create(data)
            return obj
        except (TypeError, ValueError):
            self.fail("invalid")


class NodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Node
        fields = ["notes", "in_trash", "is_starred", "related", "source",
                  "tags", "collections", "origin", ]

    tags = TagRelatedField(many=True)


class TextSerializer(NodeSerializer):

    class Meta:
        model = Text
        fields = ["uuid", "body", ] + NodeSerializer.Meta.fields

    # def create(self, validated_data):
    #     # TODO: Need to append user before save method.
    #     data_origin = validated_data.pop("collections")
    #     data_source = validated_data.pop("source")
    #     data_tags = validated_data.pop("tags")
    #     data_collections = validated_data.pop("collections")
    #
    #     text = Text.objects.create(**validated_data)
    #
    #     return text


class ImageSerializer(NodeSerializer):

    class Meta:
        model = Image
        fields = ["file", "name", "description", ] + NodeSerializer.Meta.fields

    # def create(self, validated_data):
    #     # TODO: Need to append user before save method.
    #     pass