from django.core.exceptions import ValidationError, FieldDoesNotExist
from django.urls import reverse

from rest_framework import serializers, exceptions

from . import models


def update_instance(instance, data: dict, attrs: list):
    """ instance.attr = data.get("attr", instance.attr) """

    for attr in attrs:
        value_original = getattr(instance, attr)
        value_new = data.get(attr, value_original)
        setattr(instance, attr, value_new)

    return instance


class NestedRelatedToUserFied(serializers.RelatedField):
    def __init__(self, *args, **kwargs):
        """ Creates a field that obeys a unique together constraint between the
        the `user` field and the `unique_field`.

        Parameters
            unique_field:str
            default:None
            This field must be the sibling to "user" in the unique_together
            contraint i.e `unique_together = ["user", unique_field]`

            create_new:bool
            default:True
            When performing a create/update on the parent serializer should the
            field create a new model object if it cannot retrieve one.

            display_as:str ["str", "url"]
            default:None

            url_view_name:str
            default:None

            url_lookup_field:str
            default:None

        """
        self.unique_field = kwargs.pop("unique_field", None)
        self.create_new = kwargs.pop("create_new", True)
        self.display_as = kwargs.pop("display_as", None)
        self.url_view_name = kwargs.pop("url_view_name", None)
        self.url_lookup_field = kwargs.pop("url_lookup_field", None)

        super().__init__(*args, **kwargs)

        self.model = self.queryset.model

        if self.unique_field is None:
            raise ValueError("NestedRelatedToUserFied 'unique_field' must be defined.")

        try:
            self.model._meta.get_field(self.unique_field)
        except FieldDoesNotExist:
            raise

        if self.display_as == "url":
            if self.url_view_name is None or self.url_lookup_field is None:
                raise ValueError(
                    "NestedRelatedToUserFied 'url_view_name' and 'url_lookup_field' "
                    "must be defined if display_as=True."
                )

    def get_queryset(self):
        request = self.context.get("request")
        return self.queryset.filter(user=request.user)

    def to_internal_value(self, data):

        try:
            return self.get_queryset().get(**{self.unique_field: data})
        except self.model.DoesNotExist:

            if self.create_new:
                request = self.context.get("request")
                return self.model(user=request.user, **{self.unique_field: data})

            raise ValidationError(
                f"Model {self.model.__name__} has no object with {self.unique_field}={data}."
            )

    def to_representation(self, obj):

        if self.display_as == "url":
            request = self.context.get("request")
            url = reverse(
                self.url_view_name,
                kwargs={self.url_lookup_field: getattr(obj, self.url_lookup_field)},
            )
            return request.build_absolute_uri(url)

        elif self.display_as == "str":
            return str(obj)

        return getattr(obj, self.unique_field)


# class CustomRelated(serializers.RelatedField):
#     """ This field only supports getting objects.
#     """

#     def __init__(self, *args, **kwargs):
#         self.unique_field = kwargs.pop("unique_field", None)
#         self.as_str = kwargs.pop("as_str", None)
#         self.as_hyperlink = kwargs.pop("as_hyperlink", None)
#         self.view_name = kwargs.pop("view_name", None)
#         super().__init__(*args, **kwargs)

#         print(self.read_only)

#         self.model = self.queryset.model

#         if self.unique_field is None:
#             raise ValueError("CustomRelated 'unique_field' must be defined.")

#         if self.unique_field not in [f.name for f in self.model._meta.get_fields()]:
#             raise AttributeError("Field {unique_field} does not exist in {self.model}.")

#         if self.as_hyperlink and self.as_str:
#             raise ValueError(
#                 "CustomRelated 'as_hyperlink' and 'as_str' cannot both be 'True'."
#             )

#         if self.as_hyperlink:
#             if self.view_name is None:
#                 raise ValueError(
#                     "CustomRelated 'view_name' must be defined if as_hyperlink=True."
#                 )

#     def get_queryset(self):
#         request = self.context.get("request")
#         return self.queryset.filter(user=request.user)

#     def to_internal_value(self, data):
#         try:
#             return self.get_queryset().get(**{self.unique_field: data})
#         except self.model.DoesNotExist:
#             raise exceptions.ValidationError("NO!!!!!")

#     def to_representation(self, obj):

#         if self.as_hyperlink:
#             request = self.context.get("request")
#             # NOTE: This should eventually allow for non-pk urls.
#             url = reverse(self.view_name, kwargs={"pk": obj.pk})
#             url = request.build_absolute_uri(url)
#             return url

#         if self.as_str:
#             return str(obj)

#         return getattr(obj, self.unique_field)


#


class SourceSerializer(serializers.Serializer):

    name = serializers.CharField(max_length=256, allow_blank=True)
    individuals = NestedRelatedToUserFied(
        unique_field="name",
        many=True,
        allow_null=True,
        queryset=models.Individual.objects.all(),
    )
    url = serializers.URLField(max_length=256, allow_blank=True)
    date = serializers.DateField(allow_null=True)
    notes = serializers.CharField(allow_blank=True)

    _connections = serializers.HyperlinkedRelatedField(
        source="node_set", many=True, read_only=True, view_name="node-detail"
    )
    _url = serializers.HyperlinkedIdentityField(view_name="source-detail")

    def validate(self, data):
        """ See Source model in nodes.models for notes. """

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

    aka = NestedRelatedToUserFied(
        unique_field="name",
        create_new=False,
        display_as="url",
        url_view_name="individual-detail",
        url_lookup_field="pk",
        many=True,
        allow_null=True,
        queryset=models.Individual.objects.all(),
    )

    _connections = serializers.HyperlinkedRelatedField(
        source="source_set", many=True, read_only=True, view_name="source-detail"
    )
    _url = serializers.HyperlinkedIdentityField(view_name="individual-detail")

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

    _connections = serializers.HyperlinkedRelatedField(
        source="node_set", many=True, read_only=True, view_name="node-detail"
    )
    _url = serializers.HyperlinkedIdentityField(view_name="tag-detail")

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

    _connections = serializers.HyperlinkedRelatedField(
        source="node_set", many=True, read_only=True, view_name="node-detail"
    )
    _url = serializers.HyperlinkedIdentityField(view_name="collection-detail")

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

    _connections = serializers.HyperlinkedRelatedField(
        source="node_set", many=True, read_only=True, view_name="node-detail"
    )
    _url = serializers.HyperlinkedIdentityField(view_name="origin-detail")

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
    individuals = NestedRelatedToUserFied(
        unique_field="name",
        many=True,
        allow_null=True,
        queryset=models.Individual.objects.all(),
    )


class NodeSerializer(serializers.Serializer):

    id = serializers.ReadOnlyField()

    uuid = serializers.UUIDField(allow_null=True)

    text = serializers.CharField(allow_blank=True)
    media = serializers.FileField(allow_null=True)

    source = NestedSourceSerializer(allow_null=True)
    notes = serializers.CharField(allow_blank=True)
    tags = NestedRelatedToUserFied(
        unique_field="name",
        many=True,
        allow_null=True,
        queryset=models.Tag.objects.all(),
    )
    collections = NestedRelatedToUserFied(
        unique_field="name",
        many=True,
        allow_null=True,
        queryset=models.Collection.objects.all(),
    )

    origin = NestedRelatedToUserFied(
        unique_field="name", allow_null=True, queryset=models.Origin.objects.all()
    )
    in_trash = serializers.BooleanField()
    is_starred = serializers.BooleanField()

    related = NestedRelatedToUserFied(
        unique_field="id",
        create_new=False,
        display_as="url",
        url_view_name="node-detail",
        url_lookup_field="pk",
        many=True,
        allow_null=True,
        queryset=models.Node.objects.all(),
    )

    date_created = serializers.DateTimeField(allow_null=True)
    date_modified = serializers.DateTimeField(allow_null=True)

    auto_tags = serializers.StringRelatedField(many=True, read_only=True)
    auto_related = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name="node-detail"
    )
    count_seen = serializers.ReadOnlyField()
    count_query = serializers.ReadOnlyField()

    _url = serializers.HyperlinkedIdentityField(view_name="node-detail")

    def validate(self, data):

        text = data.get("text", None)
        media = data.get("media", None)

        if not text and not media:
            raise exceptions.ValidationError("Both 'text' and 'media' cannot be blank.")

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
        related = validated_data.pop("related", None)

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

        if related:
            node.related.set(related)

        node.save()

        return node

    def update(self, instance, validated_data):

        request = self.context.get("request")

        source = validated_data.pop("source", None)
        collections = validated_data.pop("collections", None)
        tags = validated_data.pop("tags", None)
        origin = validated_data.pop("origin", None)
        related = validated_data.pop("related", None)

        if any(source.values()):

            source_name = source.get("name", None)
            source_individuals = source.get("individuals", None)

            source = models.Source.objects.get_or_create(
                request.user, source_name, source_individuals
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

        update_instance(
            instance,
            validated_data,
            [
                "uuid",
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
