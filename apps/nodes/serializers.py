from django.core.exceptions import ValidationError

from rest_framework import serializers, exceptions

from . import models


def update_instance(instance, data: dict, attrs: list):
    """ instance.attr = data.get("attr", instance.attr) """

    for attr in attrs:
        value_original = getattr(instance, attr)
        value_new = data.get(attr, value_original)
        setattr(instance, attr, value_new)

    return instance


class UniqueToUserField(serializers.RelatedField):
    """
    via https://github.com/encode/django-rest-framework/blob/master/rest_framework/relations.py
    """

    def __init__(self, unique_sibling=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.model = self.queryset.model

        if unique_sibling is None:
            raise ValueError("UniqueToUserField 'unique_sibling' must be defined.")

        if unique_sibling not in [f.name for f in self.model._meta.get_fields()]:
            raise AttributeError(
                "Field {unique_sibling} does not exist in {self.model}."
            )

        self.unique_sibling = unique_sibling

    def get_queryset(self):
        request = self.context.get("request")
        return self.queryset.filter(user=request.user)

    def to_internal_value(self, data):

        request = self.context.get("request")

        try:
            return self.get_queryset().get(**{self.unique_sibling: data})
        except self.model.DoesNotExist:
            return self.model(user=request.user, **{self.unique_sibling: data})

    def to_representation(self, obj):
        return getattr(obj, self.unique_sibling)


#


class SourceSerializer(serializers.Serializer):

    name = serializers.CharField(max_length=256, allow_blank=True)
    individuals = UniqueToUserField(
        unique_sibling="name",
        many=True,
        allow_null=True,
        queryset=models.Individual.objects.all(),
    )
    url = serializers.URLField(max_length=256, allow_blank=True)
    date = serializers.DateField(allow_null=True)
    notes = serializers.CharField(allow_blank=True)

    _url = serializers.HyperlinkedRelatedField(
        source="id", read_only=True, view_name="sources-detail"
    )

    def validate(self, data):
        """ See Source model in nodes.models for notes. """

        request = self.context.get("request")

        name = data.get("name")
        individuals = data.get("individuals")

        if not name and not individuals:
            raise exceptions.ValidationError(
                exceptions._get_error_details(
                    {
                        "name": "Either 'name' or 'individuals' must be defined.",
                        "individuals": "Either 'name' or 'individuals' must be defined.",
                    }
                )
            )

        try:
            models.Source.validate_unique_together(request.user, name, individuals)
        except ValidationError as error:
            raise serializers.ValidationError(error.message)

        return data

    def create(self, validated_data):

        request = self.context.get("request")

        name = validated_data.get("name", None)
        individuals = validated_data.get("individuals", None)

        source = models.Source.objects.get_or_create(request.user, name, individuals)

        source.url = validated_data.get("url", None)
        source.date = validated_data.get("date", None)
        source.notes = validated_data.get("notes", None)

        source.save()

        return source

    def update(self, instance, validated_data):

        updated_instance = update_instance(
            instance, validated_data, ["name", "url", "date", "notes"]
        )

        individuals = validated_data.get("individuals", instance.individuals)
        updated_instance.individuals.set(individuals)

        updated_instance.save()

        return updated_instance


class IndividualSerializer(serializers.Serializer):

    name = serializers.CharField(max_length=256)
    first_name = serializers.CharField(max_length=256, allow_blank=True)
    last_name = serializers.CharField(max_length=256, allow_blank=True)
    # TODO: Implement a recursive editable field for aka.
    aka = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name="individuals-detail"
    )

    _url = serializers.HyperlinkedRelatedField(
        source="id", read_only=True, view_name="individuals-detail"
    )

    def validate_name(self, name):

        # PUT and PATCH
        if self.instance:
            if self.instance.name == name:
                return name

        # POST, PUT and PATCH
        request = self.context.get("request")

        try:
            models.Individual.objects.get(user=request.user, name=name)
        except models.Individual.DoesNotExist:
            return name
        else:
            raise serializers.ValidationError(f"Individual '{name}' already exists.")

    def create(self, validated_data):

        request = self.context.get("request")

        individual = models.Individual.objects.create(
            user=request.user, **validated_data
        )

        return individual

    def update(self, instance, validated_data):

        updated_instance = update_instance(
            instance, validated_data, ["name", "first_name", "last_name"]
        )

        updated_instance.save()

        return updated_instance


class TagSerializer(serializers.Serializer):

    id = serializers.ReadOnlyField()

    name = serializers.CharField(max_length=64)

    _url = serializers.HyperlinkedRelatedField(
        source="id", read_only=True, view_name="tags-detail"
    )

    def validate_name(self, name):

        # PUT and PATCH
        if self.instance:
            if self.instance.name == name:
                return name

        # POST, PUT and PATCH
        request = self.context.get("request")

        try:
            models.Tag.objects.get(user=request.user, name=name)
        except models.Tag.DoesNotExist:
            return name
        else:
            raise serializers.ValidationError(f"Tag '{name}' already exists.")

    def create(self, validated_data):

        request = self.context.get("request")

        tag = models.Tag.objects.create(user=request.user, **validated_data)

        return tag

    def update(self, instance, validated_data):

        updated_instance = update_instance(instance, validated_data, ["name"])

        updated_instance.save()

        return updated_instance


class CollectionSerializer(serializers.Serializer):

    id = serializers.ReadOnlyField()

    name = serializers.CharField(max_length=64)
    color = serializers.CharField(allow_blank=True, max_length=32)
    description = serializers.CharField(allow_blank=True)

    _url = serializers.HyperlinkedRelatedField(
        source="id", read_only=True, view_name="collections-detail"
    )

    def validate_name(self, name):

        # PUT and PATCH
        if self.instance:
            if self.instance.name == name:
                return name

        # POST, PUT and PATCH
        request = self.context.get("request")

        try:
            models.Collection.objects.get(user=request.user, name=name)
        except models.Collection.DoesNotExist:
            return name
        else:
            raise serializers.ValidationError(f"Collection '{name}' already exists.")

    def create(self, validated_data):

        request = self.context.get("request")

        collection = models.Collection.objects.create(
            user=request.user, **validated_data
        )

        return collection

    def update(self, instance, validated_data):

        updated_instance = update_instance(
            instance, validated_data, ["name", "color", "description"]
        )

        updated_instance.save()

        return updated_instance


class OriginSerializer(serializers.Serializer):

    id = serializers.ReadOnlyField()

    name = serializers.CharField(max_length=64)

    _url = serializers.HyperlinkedRelatedField(
        source="id", read_only=True, view_name="origins-detail"
    )

    def validate_name(self, name):

        # PUT and PATCH
        if self.instance:
            if self.instance.name == name:
                return name

        # POST, PUT and PATCH
        request = self.context.get("request")

        try:
            models.Origin.objects.get(user=request.user, name=name)
        except models.Origin.DoesNotExist:
            return name
        else:
            raise serializers.ValidationError(f"Origin '{name}' already exists.")

    def create(self, validated_data):

        request = self.context.get("request")

        tag = models.Origin.objects.create(user=request.user, **validated_data)

        return tag

    def update(self, instance, validated_data):

        updated_instance = update_instance(instance, validated_data, ["name"])

        updated_instance.save()

        return updated_instance


#


class NestedSourceSerializer(serializers.Serializer):

    name = serializers.CharField(max_length=256, allow_blank=True)
    individuals = UniqueToUserField(
        unique_sibling="name",
        many=True,
        allow_null=True,
        queryset=models.Individual.objects.all(),
    )


class NodeSerializer(serializers.Serializer):

    id = serializers.ReadOnlyField()

    uuid = serializers.UUIDField(allow_null=True)

    text = serializers.CharField(allow_blank=True)
    file = serializers.FileField(allow_null=True)

    source = NestedSourceSerializer(allow_null=True)
    notes = serializers.CharField(allow_blank=True)
    tags = UniqueToUserField(
        unique_sibling="name",
        many=True,
        allow_null=True,
        queryset=models.Tag.objects.all(),
    )
    collections = UniqueToUserField(
        unique_sibling="name",
        many=True,
        allow_null=True,
        queryset=models.Collection.objects.all(),
    )

    origin = UniqueToUserField(
        unique_sibling="name", allow_null=True, queryset=models.Origin.objects.all()
    )
    in_trash = serializers.BooleanField()
    is_starred = serializers.BooleanField()

    # TODO: Implement a recursive editable field for related.
    related = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name="nodes-detail"
    )

    topics = serializers.StringRelatedField(many=True, read_only=True)
    related_auto = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name="nodes-detail"
    )
    count_seen = serializers.ReadOnlyField()
    count_query = serializers.ReadOnlyField()
    date_created = serializers.DateTimeField(allow_null=True)
    date_modified = serializers.DateTimeField(allow_null=True)

    _url = serializers.HyperlinkedRelatedField(
        source="id", read_only=True, view_name="nodes-detail"
    )

    def validate(self, data):

        text = data.get("text", None)
        file = data.get("file", None)

        if not text and not file:
            raise exceptions.ValidationError(
                exceptions._get_error_details(
                    {
                        "text": "Either 'text' or 'file' must be defined.",
                        "file": "Either 'text' or 'file' must be defined.",
                    }
                )
            )

        return data

    def create(self, validated_data):

        request = self.context.get("request")

        if not validated_data.get("uuid"):
            validated_data.pop("uuid")

        if not validated_data.get("date_created"):
            validated_data.pop("date_created")

        if not validated_data.get("date_modified"):
            validated_data.pop("date_modified")

        source = validated_data.pop("source", None)
        collections = validated_data.pop("collections", None)
        tags = validated_data.pop("tags", None)
        origin = validated_data.pop("origin", None)

        node = models.Node.objects.create(user=request.user, **validated_data)

        if any(source.values()):

            source_name = source.get("name", None)
            source_individuals = source.get("individuals", None)

            source = models.Source.objects.get_or_create(
                request.user, source_name, source_individuals
            )
            node.source = source

        if tags:
            for t in tags:
                t.save()
            node.tags.set(tags)

        if collections:
            for c in collections:
                c.save()
            node.collections.set(collections)

        if origin:
            origin.save()
            node.origin = origin

        node.save()

        return node

    def update(self, instance, validated_data):
        # TODO: Implement this...
        return super().update(instance, validated_data)
