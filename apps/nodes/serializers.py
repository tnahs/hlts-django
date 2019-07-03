from django.core.exceptions import FieldDoesNotExist, ValidationError
from rest_framework import exceptions, serializers, validators
from rest_framework.reverse import reverse

from .models import Collection, Individual, Node, Origin, Source, Tag


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
    }


UserField = serializers.PrimaryKeyRelatedField(
    read_only=True, default=serializers.CurrentUserDefault()
)


class PrimaryKeyToUserField(serializers.PrimaryKeyRelatedField):
    """ A field requiring a user for retrieveing and appending objects based on
    their primary keys. """

    def get_queryset(self):
        request = self.context.get("request")
        return self.queryset.filter(user=request.user)


class UniqueToUserField(serializers.RelatedField):
    """ A field requiring a user for retrieveing objects. Implicitly enfores a
    unique_together contraint with the "user" when creating nested objects in a
    serializer.

    Parameters:
        unique_field:str
        default:None
        required:True
        The field on the target instance used to represent it. It should
        uniquely identify any given instance with with respect to its user.
        In other words, the sibling to a unique_together constraint.
        i.e. unique_together = (user, unique_field) """

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
        return data

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


class IndividualSerializer(serializers.Serializer):

    user = UserField
    id = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=256)
    first_name = serializers.CharField(max_length=256, allow_blank=True)
    last_name = serializers.CharField(max_length=256, allow_blank=True)

    # FIXME
    # date_created = serializers.DateTimeField(allow_null=True)
    # date_modified = serializers.DateTimeField(allow_null=True)

    aka = UniqueToUserField(
        unique_field="name",
        queryset=Individual.objects.all(),
        many=True,
        allow_null=True,
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

    class Meta:
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Individual.objects.all(),
                fields=("user", "name"),
                message="Individual already exists.",
            )
        ]

    def create(self, validated_data):
        return Individual.objects.create(validated_data)

    def update(self, instance, validated_data):
        return Individual.objects.update(validated_data)


class SourceSerializer(serializers.Serializer):

    # QUESTION: Can we use this data somehow during .validate() ?
    user = UserField

    id = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=256, allow_blank=True)
    individuals = UniqueToUserField(
        unique_field="name",
        queryset=Individual.objects.all(),
        many=True,
        allow_null=True,
    )
    url = serializers.CharField(allow_blank=True)
    date = serializers.CharField(max_length=256, allow_blank=True)
    notes = serializers.CharField(allow_blank=True)

    # FIXME
    # date_created = serializers.DateTimeField(allow_null=True)
    # date_modified = serializers.DateTimeField(allow_null=True)

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

        name = data.get("name", None)
        individuals = data.get("individuals", None)

        if not name and not individuals:
            raise exceptions.ValidationError(
                "Both 'name' and 'individuals' cannot be blank."
            )

        try:
            Source.validate_unique_together(request.user, name, individuals)
        except ValidationError:
            raise exceptions.ValidationError(
                f"Source {name} already exists with {', '.join(individuals)}."
            )

        return data

    def create(self, validated_data):
        return Source.objects.create(validated_data)

    def update(self, instance, validated_data):
        return Source.objects.update(validated_data)


class TagSerializer(serializers.Serializer):

    user = UserField
    id = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=64)

    date_created = serializers.DateTimeField(allow_null=True)
    date_modified = serializers.DateTimeField(allow_null=True)

    _metadata = serializers.SerializerMethodField("get_metadata")

    def get_metadata(self, obj):
        return _get_metadata(
            obj=obj,
            self_basename="tag",
            connection_queryset=obj.node_set.all(),
            connection_basename="node",
            request=self.context.get("request"),
        )

    class Meta:
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Tag.objects.all(),
                fields=("user", "name"),
                message="Tag already exists.",
            )
        ]

    def create(self, validated_data):
        return Tag.objects.create(**validated_data)

    def update(self, instance, validated_data):
        return Tag.objects.update(validated_data)


class CollectionSerializer(serializers.Serializer):

    user = UserField
    id = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=64)
    color = serializers.CharField(max_length=32, allow_blank=True)
    description = serializers.CharField(allow_blank=True)

    date_created = serializers.DateTimeField(allow_null=True)
    date_modified = serializers.DateTimeField(allow_null=True)

    _metadata = serializers.SerializerMethodField("get_metadata")

    def get_metadata(self, obj):
        return _get_metadata(
            obj=obj,
            self_basename="collection",
            connection_queryset=obj.node_set.all(),
            connection_basename="node",
            request=self.context.get("request"),
        )

    class Meta:
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Collection.objects.all(),
                fields=("user", "name"),
                message="Collection already exists.",
            )
        ]

    def create(self, validated_data):
        return Collection.objects.create(**validated_data)

    def update(self, instance, validated_data):
        return Collection.objects.update(validated_data)


class OriginSerializer(serializers.Serializer):

    user = UserField
    id = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=64)

    date_created = serializers.DateTimeField(allow_null=True)
    date_modified = serializers.DateTimeField(allow_null=True)

    _metadata = serializers.SerializerMethodField("get_metadata")

    def get_metadata(self, obj):
        return _get_metadata(
            obj=obj,
            self_basename="origin",
            connection_queryset=obj.node_set.all(),
            connection_basename="node",
            request=self.context.get("request"),
        )

    class Meta:
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Origin.objects.all(),
                fields=("user", "name"),
                message="Origin already exists.",
            )
        ]

    def create(self, validated_data):
        return Origin.objects.create(**validated_data)

    def update(self, instance, validated_data):
        return Origin.objects.update(**validated_data)


#


class NestedSourceSerializer(serializers.Serializer):

    name = serializers.CharField(max_length=256, allow_blank=True)
    individuals = UniqueToUserField(
        unique_field="name",
        queryset=Individual.objects.all(),
        many=True,
        allow_null=True,
    )

    # QUESTION: Do we want to pass extra fields here during a nested creation?


class NodeSerializer(serializers.Serializer):

    id = serializers.UUIDField(allow_null=True)
    text = serializers.CharField(allow_blank=True)
    media = serializers.FileField(allow_null=True)

    source = NestedSourceSerializer(allow_null=True)
    notes = serializers.CharField(allow_blank=True)
    tags = UniqueToUserField(
        unique_field="name", queryset=Tag.objects.all(), many=True, allow_null=True
    )
    collections = UniqueToUserField(
        unique_field="name",
        queryset=Collection.objects.all(),
        many=True,
        allow_null=True,
    )

    origin = UniqueToUserField(
        unique_field="name", queryset=Origin.objects.all(), allow_null=True
    )

    in_trash = serializers.BooleanField()
    is_starred = serializers.BooleanField()

    related = PrimaryKeyToUserField(
        many=True, allow_null=True, queryset=Node.objects.all()
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
        return Node.objects.create(validated_data)

    def update(self, instance, validated_data):
        return Node.objects.update(instance, validated_data)
