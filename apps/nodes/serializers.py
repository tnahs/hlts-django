from django.core.exceptions import ValidationError, FieldDoesNotExist

from rest_framework import serializers, exceptions, validators
from rest_framework.reverse import reverse

from . import models


def _update_instance(instance, data: dict, attrs: list):
    """ instance.attr = data.get("attr", instance.attr) """

    for attr in attrs:
        value_original = getattr(instance, attr)
        value_new = data.get(attr, value_original)
        setattr(instance, attr, value_new)

    return instance


def _get_metadata(
    obj, self_basename, connection_queryset, connection_basename, request
):
    self_view = f"{self_basename}-detail"
    connection_view = f"{connection_basename}-detail"

    api_url = reverse(self_view, args=[obj.pk], request=request)
    connections_count = connection_queryset.count()
    connections = [
        reverse(connection_view, args=[n.pk], request=request)
        for n in connection_queryset
    ]

    return {
        "api_url": api_url,
        f"{connection_basename}_connections_count": connections_count,
        f"{connection_basename}_connections": connections,
        "date_created": obj.date_created,
        "date_modified": obj.date_modified,
    }


UserField = serializers.SlugRelatedField(
    slug_field="email", default=serializers.CurrentUserDefault(), read_only=True
)


class PrimaryKeyToUserField(serializers.PrimaryKeyRelatedField):
    """ A field requiring a user for retrieveing, appending objects based on
    their primary keys. """

    def get_queryset(self):
        request = self.context.get("request")
        return self.queryset.filter(user=request.user)


class UniqueToUserField(serializers.RelatedField):
    """ A field requiring a user for retrieveing, creating and appending
    objects based on a unique_together constraint with the "user".

    Primarily used to implicitly enfore a unique_together contraint with the
    "user" when creating nested objects in a serializer.

    Parameters:
        unique_field:str
        default:None
        required:True
            The field on the target instance used to represent it. It should
            uniquely identify any given instance with with respect to its user.
            In other words, the sibling to a unique_together constraint.
            i.e. unique_together = [user, unique_field] """

    def __init__(self, *args, **kwargs):
        self._unique_field = kwargs.pop("unique_field", None)
        super().__init__(*args, **kwargs)

        self.model = self.queryset.model

        if self._unique_field is None:
            raise ValueError("UniqueToUserField 'unique_field' must be defined.")

        try:
            self.model._meta.get_field(self._unique_field)
        except FieldDoesNotExist:
            raise

    def get_queryset(self):
        request = self.context.get("request")
        return self.queryset.filter(user=request.user)

    def to_internal_value(self, data):

        try:
            return self.get_queryset().get(**{self._unique_field: data})
        except self.model.DoesNotExist:
            request = self.context.get("request")
            return self.model(user=request.user, **{self._unique_field: data})

    def to_representation(self, obj):
        return getattr(obj, self._unique_field)


#


class MergeSerializer(serializers.Serializer):

    id = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=256)

    _metadata = serializers.SerializerMethodField("get_metadata")

    def get_metadata(self, obj):
        return _get_metadata(
            obj=obj,
            self_basename=self.context.get("basename"),
            connection_queryset=obj.node_set.all(),
            connection_basename="node",
            request=self.context.get("request"),
        )


class SourceSerializer(serializers.Serializer):

    id = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=256, allow_blank=True)
    individuals = UniqueToUserField(
        unique_field="name",
        many=True,
        allow_null=True,
        queryset=models.Individual.objects.all(),
    )
    url = serializers.URLField(max_length=256, allow_blank=True)
    date = serializers.DateField(allow_null=True)
    notes = serializers.CharField(allow_blank=True)

    _metadata = serializers.SerializerMethodField("get_metadata")

    def get_metadata(self, obj):
        return _get_metadata(
            obj=obj,
            self_basename="source",
            connection_queryset=obj.node_set.all(),
            connection_basename="node",
            request=self.context.get("request"),
        )

    def validate(self, data):
        """ See apps.nodes.models.Source """

        request = self.context.get("request")

        name = data.get("name")
        individuals = data.get("individuals")

        if not name and not individuals:
            raise exceptions.ValidationError(
                "Both 'name' and 'individuals' cannot be blank."
            )

        try:
            models.Source.validate_unique_together(request.user, name, individuals)
        except ValidationError as error:
            raise serializers.ValidationError(error.message)

        return data

    def create(self, validated_data):

        user = validated_data.get("user", None)
        name = validated_data.get("name", None)
        individuals = validated_data.get("individuals", None)

        source = models.Source.objects.get_or_create(user, name, individuals)

        source.url = validated_data.get("url", None)
        source.date = validated_data.get("date", None)
        source.notes = validated_data.get("notes", None)

        source.save()

        return source

    def update(self, instance, validated_data):

        updated_instance = _update_instance(
            instance, validated_data, ["name", "url", "date", "notes"]
        )

        individuals = validated_data.get("individuals", instance.individuals)
        updated_instance.individuals.set(individuals)

        updated_instance.save()

        return updated_instance


class IndividualSerializer(serializers.Serializer):
    class Meta:
        validators = [
            validators.UniqueTogetherValidator(
                queryset=models.Individual.objects.all(),
                fields=("user", "name"),
                message="Individual already exists.",
            )
        ]

    user = UserField
    id = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=256)
    first_name = serializers.CharField(max_length=256, allow_blank=True)
    last_name = serializers.CharField(max_length=256, allow_blank=True)

    aka = UniqueToUserField(
        unique_field="name",
        many=True,
        allow_null=True,
        queryset=models.Individual.objects.all(),
    )

    _metadata = serializers.SerializerMethodField("get_metadata")

    def get_metadata(self, obj):
        return _get_metadata(
            obj=obj,
            self_basename="individual",
            connection_queryset=obj.source_set.all(),
            connection_basename="source",
            request=self.context.get("request"),
        )

    def create(self, validated_data):

        aka = validated_data.pop("aka")

        individual = models.Individual.objects.create(**validated_data)
        individual.aka.set(aka)
        individual.save()

        return individual

    def update(self, instance, validated_data):

        updated_instance = _update_instance(
            instance, validated_data, ["name", "first_name", "last_name"]
        )
        updated_instance.save()

        return updated_instance


class TagSerializer(serializers.Serializer):
    class Meta:
        validators = [
            validators.UniqueTogetherValidator(
                queryset=models.Tag.objects.all(),
                fields=("user", "name"),
                message="Tag already exists.",
            )
        ]

    user = UserField
    id = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=64)

    _metadata = serializers.SerializerMethodField("get_metadata")

    def get_metadata(self, obj):
        return _get_metadata(
            obj=obj,
            self_basename="tag",
            connection_queryset=obj.node_set.all(),
            connection_basename="node",
            request=self.context.get("request"),
        )

    def create(self, validated_data):
        return models.Tag.objects.create(**validated_data)

    def update(self, instance, validated_data):

        updated_instance = _update_instance(instance, validated_data, ["name"])
        updated_instance.save()

        return updated_instance


class CollectionSerializer(serializers.Serializer):
    class Meta:
        validators = [
            validators.UniqueTogetherValidator(
                queryset=models.Collection.objects.all(),
                fields=("user", "name"),
                message="Collection already exists.",
            )
        ]

    user = UserField
    id = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=64)
    color = serializers.CharField(allow_blank=True, max_length=32)
    description = serializers.CharField(allow_blank=True)

    _metadata = serializers.SerializerMethodField("get_metadata")

    def get_metadata(self, obj):
        return _get_metadata(
            obj=obj,
            self_basename="collection",
            connection_queryset=obj.node_set.all(),
            connection_basename="node",
            request=self.context.get("request"),
        )

    def create(self, validated_data):
        return models.Collection.objects.create(**validated_data)

    def update(self, instance, validated_data):

        updated_instance = _update_instance(
            instance, validated_data, ["name", "color", "description"]
        )
        updated_instance.save()

        return updated_instance


class OriginSerializer(serializers.Serializer):
    class Meta:
        validators = [
            validators.UniqueTogetherValidator(
                queryset=models.Origin.objects.all(),
                fields=("user", "name"),
                message="Origin already exists.",
            )
        ]

    user = UserField
    id = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=64)

    _metadata = serializers.SerializerMethodField("get_metadata")

    def get_metadata(self, obj):
        return _get_metadata(
            obj=obj,
            self_basename="origin",
            connection_queryset=obj.node_set.all(),
            connection_basename="node",
            request=self.context.get("request"),
        )

    def create(self, validated_data):
        return models.Origin.objects.create(**validated_data)

    def update(self, instance, validated_data):

        updated_instance = _update_instance(instance, validated_data, ["name"])
        updated_instance.save()

        return updated_instance


#


class NestedSourceSerializer(serializers.Serializer):

    name = serializers.CharField(max_length=256, allow_blank=True)
    individuals = UniqueToUserField(
        unique_field="name",
        many=True,
        allow_null=True,
        queryset=models.Individual.objects.all(),
    )


class NodeSerializer(serializers.Serializer):

    id = serializers.UUIDField(allow_null=True)
    text = serializers.CharField(allow_blank=True)
    media = serializers.FileField(allow_null=True)

    source = NestedSourceSerializer(allow_null=True)
    notes = serializers.CharField(allow_blank=True)
    tags = UniqueToUserField(
        unique_field="name",
        many=True,
        allow_null=True,
        queryset=models.Tag.objects.all(),
    )
    collections = UniqueToUserField(
        unique_field="name",
        many=True,
        allow_null=True,
        queryset=models.Collection.objects.all(),
    )

    origin = UniqueToUserField(
        unique_field="name", allow_null=True, queryset=models.Origin.objects.all()
    )

    in_trash = serializers.BooleanField()
    is_starred = serializers.BooleanField()

    related = PrimaryKeyToUserField(
        many=True, allow_null=True, queryset=models.Node.objects.all()
    )

    auto_tags = serializers.StringRelatedField(many=True, read_only=True)
    auto_related = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    date_created = serializers.DateTimeField(allow_null=True)
    date_modified = serializers.DateTimeField(allow_null=True)

    _metadata = serializers.SerializerMethodField("get_metadata")

    def get_metadata(self, obj):
        return _get_metadata(
            obj=obj,
            self_basename="node",
            connection_queryset=obj.related.all() | obj.auto_related.all(),
            connection_basename="node",
            request=self.context.get("request"),
        )

    def validate(self, data):

        text = data.get("text", None)
        media = data.get("media", None)

        if not text and not media:
            raise exceptions.ValidationError("Both 'text' and 'media' cannot be blank.")

        return data

    def create(self, validated_data):

        user = validated_data.pop("user", None)

        # TODO why does sending null not fire-off the default value in model?
        if not validated_data.get("date_created"):
            validated_data.pop("date_created")

        if not validated_data.get("date_modified"):
            validated_data.pop("date_modified")

        source = validated_data.pop("source", None)
        collections = validated_data.pop("collections", None)
        tags = validated_data.pop("tags", None)
        origin = validated_data.pop("origin", None)
        related = validated_data.pop("related", None)

        # FIXME make sure to run set() on anything that is [user, name] unique.
        # Unique together constraint fails if the user put in 2 of the same name.

        node = models.Node.objects.create(user=user, **validated_data)

        if any(source.values()):

            source_name = source.get("name", None)
            source_individuals = source.get("individuals", None)

            source = models.Source.objects.get_or_create(
                user, source_name, source_individuals
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

        if related:
            node.related.set(related)

        node.save()

        return node

    def update(self, instance, validated_data):

        user = validated_data.pop("user", None)

        source = validated_data.pop("source", None)
        collections = validated_data.pop("collections", None)
        tags = validated_data.pop("tags", None)
        origin = validated_data.pop("origin", None)
        related = validated_data.pop("related", None)

        if source:
            if any(source.values()):

                source_name = source.get("name", None)
                source_individuals = source.get("individuals", None)

                source = models.Source.objects.get_or_create(
                    user, source_name, source_individuals
                )
                instance.source = source

        if tags:
            for t in tags:
                t.save()
            instance.tags.set(tags)

        if collections:
            for c in collections:
                c.save()
            instance.collections.set(collections)

        if origin:
            origin.save()
            instance.origin = origin

        if related:
            instance.related.set(related)

        _update_instance(
            instance,
            validated_data,
            [
                "text",
                "media",
                "notes",
                "in_trash",
                "is_starred",
                "date_created",
                "date_modified",
            ],
        )

        instance.save()

        return instance
