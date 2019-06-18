import ast

import django
from django.db import models
from django.contrib.auth import get_user_model
from rest_framework import serializers, exceptions

from .models import (Individual, Source, Tag, Collection, Node, Text, Image)


""" Most of these serializers will need .create() and .update() methods to
handle the unique together constraints ie [user, name].

The others will need them because of nested serialization.
"""


def get_current_user(context):

    # TODO: Can we make this cleaner? Implicity get the user in any field?

    user = None

    request = context.get("request")

    if request and hasattr(request, "user"):
        user = request.user

    return user


class TagSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Tag
        fields = ("api_url", "id", "name")
        read_only_fields = ("id", )

    def validate_name(self, value):

        try:
            Tag.objects.get(name=value)
        except Tag.DoesNotExist:
            return value
        else:
            raise serializers.ValidationError(f"Tag '{value}' already exists.")


class CollectionSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Collection
        fields = ("api_url", "id", "name")
        read_only_fields = ("id", )

    def validate_name(self, value):

        try:
            Collection.objects.get(name=value)
        except Collection.DoesNotExist:
            return value
        else:
            raise serializers.ValidationError(f"Collection '{value}' already exists.")


class IndividualSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Individual
        fields = ("api_url", "name", "first_name", "last_name")

    def validate_name(self, value):

        try:
            Individual.objects.get(name=value)
        except Individual.DoesNotExist:
            return value
        else:
            raise serializers.ValidationError(f"Individual '{value}' already exists.")


#


class MtoMListSerializer(serializers.Field):
    """ Converts a MtoM relation into a list.

    Args:
        model: django.db.models.Model
            default: None

        serialize_field: str
            default: None
    """

    def __init__(self, *args, **kwargs):

        self.model = kwargs.pop("model", None)
        self.serialize_field = kwargs.pop("serialize_field", None)

        if self.model is None:
            raise ValueError("MtoMListSerializer 'model' must be defined.")

        if self.serialize_field is None:
            raise ValueError("MtoMListSerializer 'serialize_field' must be defined.")

        super().__init__(*args, **kwargs)

    def get_attribute(self, instance):
        """
        via https://github.com/encode/django-rest-framework/blob/master/rest_framework/fields.py#L341
        and https://github.com/encode/dsjango-rest-framework/blob/master/rest_framework/fields.py#L423
        """

        try:
            return getattr(instance, self.source).all()
        except AttributeError as error:
            raise AttributeError(
                f"The field source '{self.source}' does not match any "
                f"field on the '{instance}' instance."
            ) from error

    def to_representation(self, values: models.QuerySet):

        try:
            return [getattr(obj, self.serialize_field) for obj in values]
        except AttributeError as error:
            raise AttributeError(
                f"The serialize_field '{self.serialize_field}' does not match "
                f"any field inside {[repr(v) for v in values]}."
            ) from error

        return

    def to_internal_value(self, data: str):

        if not data:
            return []

        user = get_current_user(self.context)

        data_list = ast.literal_eval(data)

        for name in data_list:

            obj, created = self.model.objects.get_or_create(
                name=name,
                user=user
            )

            yield obj


class SourceSerializer(serializers.HyperlinkedModelSerializer):

    individuals = MtoMListSerializer(
        model=Individual,
        serialize_field="name"
    )

    # TODO: Can we have these choices change based on view? Post/Put

    SOURCE_ACTIONS = [
        (None, "None"),
        ("create_new", "Create new"),
        ("use_existing", "Use Existing"),
        ("update_existing", "Update Existing"),
    ]

    action = serializers.ChoiceField(
        choices=SOURCE_ACTIONS,
        default="auto",
        write_only=True
    )

    name = serializers.CharField(required=False)

    class Meta:
        model = Source
        fields = ("action", "api_url", "name", "individuals", "url", "date",
                  "notes")
        read_only_fields = ("api_url", )

    def validate(self, data):

        # FIXME: We need to make sure these validations work in POST and PUT!

        user = get_current_user(self.context)
        action = data.get("action")
        name = data.get("name")
        individuals = data.get("individuals")

        if action == None:

            # If any of the Source fields have data raise ValidationError.
            if any(data.values()):
                raise exceptions.ValidationError(
                    exceptions._get_error_details(
                        {
                            "action": f"Selected action '{action}' does not "
                                       "support passing Source data."
                        }
                    )
                )

            return data

        if action in ["create_new", "use_existing"]:

            if not name:
                raise exceptions.ValidationError(
                    exceptions._get_error_details(
                        {
                            "name": f"Selected action '{action}' requires name."
                        }
                    )
                )

        if action == "create_new":

            try:
                Source.validate_unique_source_individuals(
                    user,
                    name,
                    individuals_qs=individuals
                )
            except django.core.exceptions.ValidationError as error:
                raise exceptions.ValidationError(
                    exceptions._get_error_details(
                        {
                            "name": error.message,
                            "individuals": error.message
                        }
                    )
                )

        if action in "use_existing":

            try:
                Source.get_or_raise(user, name, individuals_qs=individuals)
            except django.core.exceptions.ValidationError as error:
                if error.code == "source_only":
                    raise exceptions.ValidationError(
                        exceptions._get_error_details(
                            {
                                "name": error.message,
                            }
                        )
                    )
                elif error.code == "source_and_individual":
                    raise exceptions.ValidationError(
                        exceptions._get_error_details(
                            {
                                "name": error.message,
                                "individuals": error.message
                            }
                        )
                    )

            data_ = data.copy()
            data_.pop("action", None)
            data_.pop("name", None)
            data_.pop("individuals", None)

            if any(data_.values()):
                raise exceptions.ValidationError(
                    exceptions._get_error_details(
                        {
                            "action": f"Selected action '{action}' only supports "
                                       "passing name and individuals."
                        }
                    )
                )

        return data

    def create(self, data):

        user = get_current_user(self.context)

        action = data.pop("action", None)
        name = data.pop("name", None)
        individuals = data.pop("individuals", None)

        if action == None:

            obj = None

        elif action == "use_existing":

            obj = Source.get_or_raise(user, name, individuals_names=individuals)

        elif action == "create_new":

            obj = Source.objects.create(
                name=name,
                user=user
            )

            obj.individuals.set(individuals)

            for key, value in data.items():
                setattr(obj, key, value)

        return obj


class NodeSerializer(serializers.HyperlinkedModelSerializer):

    origin = serializers.StringRelatedField()
    source = SourceSerializer()
    tags = MtoMListSerializer(
        model=Tag,
        serialize_field="name"
    )
    collections = MtoMListSerializer(
        model=Collection,
        serialize_field="name"
    )

    class Meta:
        model = Node
        fields = ("notes", "in_trash", "is_starred", "tags", "collections",
                  "source")

    def _create(self, model, data):

        source = data.pop("source", None)
        tags = data.pop("tags", None)
        collections = data.pop("collections", None)

        obj_source = self._create_source_obj(source)
        objs_tags = self._create_m2m_objs(Tag, tags)
        objs_collections = self._create_m2m_objs(Collection, collections)

        obj = model.objects.create(**data)

        obj.source = obj_source
        obj.tags.set(objs_tags)
        obj.collections.set(objs_collections)

        return obj

    def _update(self, instance, validated_data):

        source = validated_data.pop("source", None)
        tags = validated_data.pop("tags", None)
        collections = validated_data.pop("collections", None)

        obj_source = self._create_source_obj(source)
        objs_tags = self._create_m2m_objs(Tag, tags)
        objs_collections = self._create_m2m_objs(Collection, collections)

        instance.source = obj_source
        instance.tags.set(objs_tags)
        instance.collections.set(objs_collections)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        return instance

    def _create_source_obj(self, data):

        user = get_current_user(self.context)

        action = data.pop("action", None)
        name = data.pop("name", None)
        individuals = data.pop("individuals", None)

        if action == None:

            obj = None

        elif action == "use_existing":

            obj = Source.get_or_raise(user, name, individuals_names=individuals)

        elif action == "create_new":

            obj = Source.objects.create(
                name=name,
                user=user
            )

            objs_individuals = self._create_m2m_objs(
                model=Individual,
                data=individuals
            )

            obj.individuals.set(objs_individuals)

            for key, value in data.items():
                setattr(obj, key, value)

            obj.save()

        return obj

    def _create_m2m_objs(self, model, data):

        user = get_current_user(self.context)

        objs = []
        for name in data:

            obj, created = model.objects.get_or_create(
                name=name,
                user=user
            )

            obj.save()
            objs.append(obj)

        return objs


class NodeTextSerializer(NodeSerializer):

    class Meta(NodeSerializer.Meta):
        model = Text
        fields = ("api_url", "uuid", "body") + NodeSerializer.Meta.fields
        read_only_fields = ("api_url", )

    def create(self, validated_data):
        return super()._create(Text, validated_data)

    def update(self, instance, validated_data):
        return super()._update(instance, validated_data)


class NodeImageSerializer(NodeSerializer):

    class Meta(NodeSerializer.Meta):
        model = Image
        fields = ("api_url", "file", "name", "description") + NodeSerializer.Meta.fields
        read_only_fields = ("api_url", )

    def create(self, validated_data):
        return super()._create(Image, validated_data)


#


class NodesSerializer(serializers.ModelSerializer):

    texts = NodeTextSerializer(many=True)
    images = NodeImageSerializer(many=True)

    class Meta:
        model = get_user_model()
        fields = ("texts", "images")
