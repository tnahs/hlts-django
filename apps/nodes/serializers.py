from django.core.exceptions import FieldDoesNotExist, ValidationError
from rest_framework import exceptions, serializers, validators
from rest_framework.reverse import reverse

from .models import Collection, Individual, Node, Origin, Source, Tag


class MetadataMixin:
    def _get_metadata(
        self, obj, self_basename, connection_queryset, connection_basename, request
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


HiddenCurrentUserField = serializers.HiddenField(
    default=serializers.CurrentUserDefault()
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


class IndividualSerializer(MetadataMixin, serializers.Serializer):

    user = HiddenCurrentUserField
    id = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=256)
    first_name = serializers.CharField(max_length=256, allow_blank=True)
    last_name = serializers.CharField(max_length=256, allow_blank=True)

    date_created = serializers.DateTimeField(read_only=True)
    date_modified = serializers.DateTimeField(read_only=True)

    aka = UniqueToUserField(
        unique_field="name",
        queryset=Individual.objects.all(),
        many=True,
        allow_null=True,
    )

    metadata = serializers.SerializerMethodField()

    def get_metadata(self, obj):
        return self._get_metadata(
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
        user = validated_data.pop("user")
        return Individual.objects.create(user, **validated_data)

    def update(self, instance, validated_data):
        user = validated_data.pop("user")
        return Individual.objects.update(user, instance, **validated_data)


class SourceSerializer(MetadataMixin, serializers.Serializer):

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

    date_created = serializers.DateTimeField(read_only=True)
    date_modified = serializers.DateTimeField(read_only=True)

    metadata = serializers.SerializerMethodField()

    def get_metadata(self, obj):
        return self._get_metadata(
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
                "Source 'name' and 'individuals' cannot be blank."
            )

        try:
            Source.validate_unique_together(request.user, name, individuals)
        except ValidationError:
            raise exceptions.ValidationError(
                f"Source {name} already exists with {', '.join(individuals)}."
            )

        return data

    def create(self, validated_data):
        user = validated_data.pop("user")
        return Source.objects.create(user, **validated_data)

    def update(self, instance, validated_data):
        user = validated_data.pop("user")
        return Source.objects.update(user, instance, **validated_data)


class TagSerializer(MetadataMixin, serializers.Serializer):

    user = HiddenCurrentUserField
    id = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=64)

    date_created = serializers.DateTimeField(read_only=True)
    date_modified = serializers.DateTimeField(read_only=True)

    metadata = serializers.SerializerMethodField()

    def get_metadata(self, obj):
        return self._get_metadata(
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
        user = validated_data.pop("user")
        return Tag.objects.create(user, **validated_data)

    def update(self, instance, validated_data):
        user = validated_data.pop("user")
        return Tag.objects.update(user, instance, **validated_data)


class CollectionSerializer(MetadataMixin, serializers.Serializer):

    user = HiddenCurrentUserField
    id = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=64)
    color = serializers.CharField(max_length=32, allow_blank=True)
    description = serializers.CharField(allow_blank=True)

    date_created = serializers.DateTimeField(read_only=True)
    date_modified = serializers.DateTimeField(read_only=True)

    metadata = serializers.SerializerMethodField()

    def get_metadata(self, obj):
        return self._get_metadata(
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
        user = validated_data.pop("user")
        return Collection.objects.create(user, **validated_data)

    def update(self, instance, validated_data):
        user = validated_data.pop("user")
        return Collection.objects.update(user, instance, **validated_data)


class OriginSerializer(MetadataMixin, serializers.Serializer):

    user = HiddenCurrentUserField
    id = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=64)

    date_created = serializers.DateTimeField(read_only=True)
    date_modified = serializers.DateTimeField(read_only=True)

    metadata = serializers.SerializerMethodField()

    def get_metadata(self, obj):
        return self._get_metadata(
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
        user = validated_data.pop("user")
        return Origin.objects.create(user, **validated_data)

    def update(self, instance, validated_data):
        user = validated_data.pop("user")
        return Origin.objects.update(user, instance, **validated_data)


#


class NestedSourceSerializer(MetadataMixin, serializers.Serializer):

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


class NodeSerializer(MetadataMixin, serializers.Serializer):

    id = serializers.UUIDField(allow_null=True)
    text = serializers.CharField(allow_blank=True)
    media = serializers.FileField(allow_null=True)
    link = serializers.URLField(allow_blank=True)

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

    auto_ocr = serializers.CharField(read_only=True)
    auto_tags = serializers.StringRelatedField(many=True, read_only=True)
    auto_related = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    date_created = serializers.DateTimeField(allow_null=True)
    date_modified = serializers.DateTimeField(allow_null=True)

    metadata = serializers.SerializerMethodField()

    def get_metadata(self, obj):
        return self._get_metadata(
            obj=obj,
            self_basename="node",
            connection_queryset=obj.related.all() | obj.auto_related.all(),
            connection_basename="node",
            request=self.context.get("request"),
        )

    def validate(self, data):

        text = data.get("text", None)
        link = data.get("link", None)
        media = data.get("media", None)

        if not any([text, media, link]):
            raise exceptions.ValidationError(
                "Nodes cannot have 'text', 'link' and 'media' blank."
            )

        if not data.get("date_created", None):
            data.pop("date_created", None)
        if not data.get("date_modified", None):
            data.pop("date_modified", None)

        return data

    def create(self, validated_data):
        user = validated_data.pop("user")
        return Node.objects.create(user, **validated_data)

    def update(self, instance, validated_data):
        user = validated_data.pop("user")
        return Node.objects.update(user, instance, **validated_data)


class MergeSerializer(MetadataMixin, serializers.Serializer):

    CHOICES = ("sources", "tags", "collections", "origins")

    which = serializers.ChoiceField(choices=CHOICES)
    into = serializers.CharField(max_length=256)
    merging = serializers.ListField(child=serializers.CharField(max_length=256))

    def validate(self, data):

        # TODO: Clean-up up errors.

        request = self.context.get("request")

        which = data.get("which")
        into = data.get("into")
        merging = data.get("merging")

        Model = getattr(request.user, which).model

        errors = {}

        try:
            into_obj = Model.objects.get(name=into)
        except Model.DoesNotExist:
            errors["into"] = f"Item '{into}' does not exist."

        merging_objs = []
        errors["merging"] = []
        for name in merging:
            try:
                merging_obj = Model.objects.get(name=name)
            except Model.DoesNotExist:
                errors["merging"].append(f"Item '{name}' does not exist.")
            else:
                merging_objs.append(merging_obj)

        if any(errors.values()):
            raise validators.ValidationError(errors)

        objs = {"into": into_obj, "merging": merging_objs}

        return objs

    def create(self, validated_data):
        # TODO: Process merge here...
        return validated_data
