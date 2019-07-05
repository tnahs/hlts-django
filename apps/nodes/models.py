from __future__ import annotations

# https://stackoverflow.com/a/49872353

import pathlib
import uuid
from typing import List

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class CommonDataMixin(models.Model):

    date_created = models.DateTimeField(default=timezone.now)
    date_modified = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def __repr__(self):
        return self.__str__()

    def save(self, *args, **kwargs):
        if self.pk:
            self.modified = timezone.now()
        super().save(*args, **kwargs)

    @staticmethod
    def update_fields(instance, data: dict, fields: list):
        """ Sets instance fields to new value if new value exists. Runs:
        instance.field = data.get(field, instance.field) on each field. """

        for field in fields:
            value_original = getattr(instance, field)
            value_new = data.get(field, value_original)
            setattr(instance, field, value_new)

        return instance


class IndividualManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def bulk_get_or_create(self, user, individuals):

        individuals = self.model.validate_type(individuals)

        # Case List[int]:
        # ---------------------------------------------------------------------
        # Individual were passed as a list of primary keys. Gets and returns.
        #
        # Case List[str]:
        # ---------------------------------------------------------------------
        # Individuals were passed as a list of (presumably) Individual names.
        # Gets/creates and returns.
        #
        # Case List[self.model]:
        # ---------------------------------------------------------------------
        # Individuals were passed as a list of Individual objects. Returns.
        #
        # NOTE: This method accomidates a mixed list of Individual pks, names
        # and objects. Not sure if Django allows or supports mixing model
        # objects with other types of data.

        individual_objs = []

        for individual in individuals:

            if isinstance(individual, int):
                obj = super().get(pk=individual, user=user)

            elif isinstance(individual, str):
                try:
                    obj = super().get(name=individual, user=user)
                except self.model.DoesNotExist:
                    obj = super().create(name=individual, user=user)

            elif isinstance(individual, self.model):
                obj = individual

            individual_objs.append(obj)

        return individual_objs

    def create(self, user, **data):

        aka = data.pop("aka")
        aka_objs = self.bulk_get_or_create(user, aka)

        obj = super().create(user=user, **data)
        obj.aka.set(aka_objs)
        obj.save()

        return obj

    def update(self, user, instance, **data):

        fields = ["name", "first_name", "last_name"]

        aka = data.pop("aka")
        aka_objs = self.bulk_get_or_create(user, aka)

        instance = self.update_fields(instance, data, fields)
        instance.aka.set(aka_objs)
        instance.save()

        return instance


class Individual(CommonDataMixin, models.Model):

    user = models.ForeignKey(
        get_user_model(), related_name="individuals", on_delete=models.CASCADE
    )

    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=256)
    first_name = models.CharField(max_length=256, blank=True)
    last_name = models.CharField(max_length=256, blank=True)

    # Name variations are handled by 'aka` i.e.
    #
    #  John Dough
    #  Dough, John
    #  J. Dough
    #  ...
    #
    # If related, all variants would be considered the same individual.
    aka = models.ManyToManyField("self", blank=True)

    objects = IndividualManager()

    class Meta:
        unique_together = ("user", "name")

    def __str__(self):
        return f"<{self.__class__.__name__}:{self.display_name}>"

    @property
    def display_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.name

    @classmethod
    def validate_type(cls, items: List[int, str, Individual]):

        if not items:
            items = []

        if not isinstance(items, (list, models.QuerySet)):
            raise TypeError(
                f"Individuals must be of type 'list' or 'QuerySet'. Received {type(items)}."
            )

        for item in items:
            if not isinstance(item, (int, str, cls)):
                raise TypeError(f"Unrecognized type {type(item)} in {items}.")

        return items

    @classmethod
    def get_pks(cls, user, individuals):
        """ Returns a set of primary keys from a list of various types of
        Individuals. Types include integers, model instances and strings.

        Used in Source.ojects.get() and Source.validate_unique_together() for
        checking the uniqueness between one set of Source/Individuals and
        another."""

        individuals = cls.validate_type(individuals)

        # Case List[int]:
        # ---------------------------------------------------------------------
        # Individual were passed as a list of primary keys. Returns unchanged.
        #
        # Case List[str]:
        # ---------------------------------------------------------------------
        # Individuals were passed as a list of (presumably) Individual names.
        # Compiles a list of all existing Individuals that match the list of
        # name. If no Individual exists (for this current user) then appends
        # None to the list in its place. This is done to make sure that if the
        # user is creating a Source that has the same name as an existing
        # Source but a slighlty different set of Individuals the validation
        # will not misfire. i.e.
        #
        #    Existing Source and Individuals:
        #    Source: "The Source"
        #    Individuals: ("John Doe", "Jane Doe")
        #
        #    Existing Source with one new Individual:
        #    Source: "The Source"
        #    Individuals: ("John Doe", "Jane Doe", "Jinny Doe")
        #              == ("John Doe", "Jane Doe", None)
        #              != ("John Doe", "Jane Doe")
        #
        # 'None' is appended as a placeholder for a not yet created Individual
        # object. Otherwise the two Sources would be considered the same and
        # validation would misfire, returning the existing Source rather than
        # creating a new Source with a different set of Individuals.
        #
        # Case List[obj]:
        # ---------------------------------------------------------------------
        # Individuals were passed as a list of Individual objects. Compiles a
        # set of their primary keys and returns.
        #
        # NOTE: This method accomidates a mixed list of Individual pks, names
        # and objects. Not sure if Django allows or supports mixing model
        # objects with other types of data.

        individual_pks = []

        for individual in individuals:

            if isinstance(individual, int):
                pk = individual

            elif isinstance(individual, str):
                try:
                    obj = cls.objects.get(name=individual, user=user)
                    pk = obj.pk
                except cls.DoesNotExist:
                    pk = None

            elif isinstance(individual, cls):
                pk = individual.pk

            individual_pks.append(pk)

        return individual_pks


class SourceManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def get_or_create(self, user, **data):
        """ Overwrites the QuerySet.get_or_create() function:
        via https://github.com/django/django/blob/master/django/db/models/query.py#L536
        """

        source = self.get(user, **data)

        if source:
            return source

        return self.create(user, **data)

    def get(self, user, **data):
        """ Returns a Source with a specific set of Individuals. """

        name = data.get("name", None)
        individuals = data.get("individuals", None)
        individuals = Individual.validate_type(individuals)

        # Compiles a list of Sources that match the target Source name and
        # user. Filters the list down by comparing the number of Individuals in
        # each matching Source to the target Source.
        sources = (
            self.get_queryset()
            .filter(name=name, user=user)
            .annotate(count=models.Count("individuals"))
            .filter(count=len(individuals))
        )

        # Compiles a set of primary keys of the target Souce Individuals.
        # Compares them against a set from every matching Source. The first
        # Source with an idential Individual primary key set is returned.
        #
        # Seeing as the uniquness of a Source to its Individuals is enforced
        # with the Source.validate_unique_together() method, we can be sure the
        # first match is the only match.
        if sources:
            new_pks = Individual.get_pks(user, individuals)
            for source in sources:
                source_pks = {i.pk for i in source.individuals.all()}
                if source_pks == new_pks:
                    return source

        return None

    def create(self, user, **data):

        individuals = data.pop("individuals", None)
        individuals = Individual.validate_type(individuals)
        individual_objs = Individual.objects.bulk_get_or_create(user, individuals)

        obj = super().create(user=user, **data)
        obj.individuals.set(individual_objs)
        obj.save()

        return obj

    def update(self, user, instance, **data):

        fields = ["name", "color", "description"]

        individuals = data.get("individuals")
        individuals = Individual.validate_type(individuals)
        individual_objs = Individual.objects.bulk_get_or_create(user, individuals)

        instance = self.update_fields(instance, data, fields)
        instance.individuals.set(individual_objs)
        instance.save()

        return instance


class Source(CommonDataMixin, models.Model):

    user = models.ForeignKey(
        get_user_model(), related_name="sources", on_delete=models.CASCADE
    )

    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=256, blank=True)
    individuals = models.ManyToManyField(Individual, blank=True)
    url = models.TextField(blank=True)
    date = models.CharField(max_length=256, blank=True)
    notes = models.TextField(blank=True)

    objects = SourceManager()

    def __str__(self):
        return f"<{self.__class__.__name__}:{self.name}{self.by}>"

    @property
    def display_name(self):
        return f"{self.name}{self.by}"

    @property
    def by(self):
        if self.individuals:
            individuals = ", ".join([i.display_name for i in self.individuals.all()])
            return f" - {individuals}"

    @staticmethod
    def validate_unique_together(user, name, individuals, source_pk=None):
        """ Validates that no two sources have the same set of Individuals.

        Raises a bare ValidationError. It is expected that this error is caught
        and a message is appeneded to it at the form/serializer level.

        This validator *must* be run anytime a Source is created or updated. """

        if not individuals:
            individuals = []

        if not isinstance(individuals, (list, models.QuerySet)):
            raise TypeError(
                f"Argument 'individuals' must be of type list or QuerySet. "
                f"Received {type(individuals)}."
            )

        if len(individuals):
            if not isinstance(individuals[0], (int, str, Individual)):
                raise TypeError(
                    f"Unrecognized type {type(individuals[0])} in {individuals}."
                )

        # Compiles a list of Sources that match the target Source name and user.
        sources = Source.objects.filter(name=name, user=user)

        # In the case where a Source is being updated, we remove it from the
        # list of matches. Otherwise it would raise a ValidationError if the
        # Source's Individuals are not part of the data being updated. It would
        # find a Source with the same user, name and set of Individuals without
        # realizing it had just found the target Source.
        if source_pk:
            sources = sources.exclude(pk=source_pk)

        # Filters the list down by comparing the number of Individuals in each
        # matching Source to the target Source.
        sources = sources.annotate(count=models.Count("individuals")).filter(
            count=len(individuals)
        )

        if not sources:
            return

        # Compiles a set of primary keys of the target Souce Individuals.
        # Compares them against a set from every matching Source. A
        # ValidationError is raised if any of existing Source Individual
        # primary key sets are idential to the target Source's Individual
        # primary key set.

        new_pks = Individual.get_pks(user, individuals)

        for source in sources:
            source_pks = {i.pk for i in source.individuals.all()}
            if source_pks == new_pks:
                # Target Source already exists with the selected individuals.
                raise ValidationError()


class TagManager(models.Manager):
    def create(self, user, **data):
        return super().create(user=user, **data)

    def update(self, user, instance, **data):

        fields = ["name"]

        instance = self.update_fields(instance, data, fields)
        instance.save()

        return instance


class Tag(CommonDataMixin, models.Model):

    user = models.ForeignKey(
        get_user_model(), related_name="tags", on_delete=models.CASCADE
    )

    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=64)

    objects = TagManager()

    class Meta:
        unique_together = ("user", "name")

    def __str__(self):
        return f"<{self.__class__.__name__}:{self.name}>"


class CollectionManager(models.Manager):
    def create(self, user, **data):
        return super().create(user=user, **data)

    def update(self, user, instance, **data):

        fields = ["name", "color", "description"]

        instance = self.update_fields(instance, data, fields)
        instance.save()

        return instance


class Collection(CommonDataMixin, models.Model):

    user = models.ForeignKey(
        get_user_model(), related_name="collections", on_delete=models.CASCADE
    )

    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=64)
    color = models.CharField(max_length=32, blank=True)
    description = models.TextField(blank=True)

    objects = CollectionManager()

    class Meta:
        unique_together = ("user", "name")

    def __str__(self):
        return f"<{self.__class__.__name__}:{self.name}>"


class OriginManager(models.Manager):
    def create(self, user, **data):
        return super().create(user=user, **data)

    def update(self, user, instance, **data):

        fields = ["name"]

        instance = self.update_fields(instance, data, fields)
        instance.save()

        return instance


class Origin(CommonDataMixin, models.Model):

    user = models.ForeignKey(
        get_user_model(), related_name="origins", on_delete=models.CASCADE
    )

    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=64)

    objects = OriginManager()

    class Meta:
        unique_together = ("user", "name")

    def __str__(self):
        return f"<{self.__class__.__name__}:{self.name}>"


""" Nodes """


class MediaManager:

    VALID_IMAGE_TYPES = [".jpg", ".png", ".gif"]
    VALID_AUDIO_TYPES = [".mp3", ".aiff"]
    VALID_VIDEO_TYPES = [".mp4"]
    VALID_DOCUMENT_TYPES = [".pdf", ".txt", ".md"]

    @staticmethod
    def get_filename(path):
        return pathlib.Path(path).name

    @classmethod
    def get_folder(cls, instance, name):
        """ See apps.users.models.User """

        filetype = pathlib.Path(name).suffix

        if filetype in cls.VALID_IMAGE_TYPES:
            return instance.user.dir_images / name
        elif filetype in cls.VALID_AUDIO_TYPES:
            return instance.user.dir_audios / name
        elif filetype in cls.VALID_VIDEO_TYPES:
            return instance.user.dir_videos / name
        elif filetype in cls.VALID_DOCUMENT_TYPES:
            return instance.user.dir_documents / name
        else:
            return instance.user.dir_misc / name

    @classmethod
    def get_type(cls, name):

        filetype = pathlib.Path(name).suffix

        if filetype in cls.VALID_IMAGE_TYPES:
            return "image"
        elif filetype in cls.VALID_AUDIO_TYPES:
            return "audio"
        elif filetype in cls.VALID_VIDEO_TYPES:
            return "video"
        elif filetype in cls.VALID_DOCUMENT_TYPES:
            return "document"
        else:
            return "misc"


class NodeManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def create(self, user, **data):

        source = data.pop("source", None)
        tags = data.pop("tags", None)
        collections = data.pop("collections", None)
        origin = data.pop("origin", None)
        related = data.pop("related", None)

        obj = super().create(user=user, **data)

        if source and any(source.values()):
            self._set_source(obj, source, user)

        if tags:
            self._set_tags(obj, tags, user)

        if collections:
            self._set_collections(obj, collections, user)

        if origin:
            self._set_origin(obj, origin, user)

        if related:
            obj.related.set(related)

        obj.save()

        return obj

    def update(self, user, instance, **data):

        fields = [
            "text",
            "media",
            "notes",
            "in_trash",
            "is_starred",
            "date_created",
            "date_modified",
        ]

        source = data.pop("source", None)
        tags = data.pop("tags", None)
        collections = data.pop("collections", None)
        origin = data.pop("origin", None)
        related = data.pop("related", None)

        instance = self.update_fields(instance, data, fields)

        if source and any(source.values()):
            self._set_source(instance, source, user)

        if tags:
            self._set_tags(instance, tags, user)

        if collections:
            self._set_collections(instance, collections, user)

        if origin:
            self._set_origin(instance, origin, user)

        if related:
            instance.related.set(related)

        instance.save()

        return instance

    def _set_source(self, _obj, source, user):
        source_obj = Source.objects.get_or_create(user, **source)
        _obj.source = source_obj

    def _set_tags(self, _obj, tags, user):

        tags = set(tags)

        tag_objs = []
        for name in tags:
            tag_obj, created = Tag.objects.get_or_create(user=user, name=name)
            tag_objs.append(tag_obj)

        _obj.tags.set(tag_objs)

    def _set_collections(self, _obj, collections, user):

        collections = set(collections)

        collection_objs = []
        for name in collections:
            collection_obj, created = Collection.objects.get_or_create(
                user=user, name=name
            )
            collection_objs.append(collection_obj)

        _obj.collections.set(collection_objs)

    def _set_origin(self, _obj, origin, user):

        origin_obj, created = Origin.objects.get_or_create(user=user, name=origin)

        _obj.origin = origin_obj


class Node(CommonDataMixin, models.Model):

    user = models.ForeignKey(
        get_user_model(), related_name="nodes", on_delete=models.CASCADE
    )

    id = models.UUIDField(default=uuid.uuid4, primary_key=True)

    text = models.TextField(blank=True)
    link = models.URLField(blank=True)
    media = models.FileField(upload_to=MediaManager.get_folder, blank=True)

    source = models.ForeignKey(Source, on_delete=models.CASCADE, null=True, blank=True)
    notes = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    collections = models.ManyToManyField(Collection, blank=True)

    origin = models.ForeignKey(Origin, on_delete=models.CASCADE, null=True, blank=True)

    in_trash = models.BooleanField(default=False)
    is_starred = models.BooleanField(default=False)

    related = models.ManyToManyField("self", blank=True)

    # Read-only
    auto_ocr = models.TextField(blank=True)
    auto_tags = models.ManyToManyField(Tag, blank=True, related_name="auto_tagged")
    auto_related = models.ManyToManyField(
        "self", blank=True, related_name="auto_related"
    )

    objects = NodeManager()

    def __str__(self):
        return f"<{self.__class__.__name__}:{self.display_name}>"

    @property
    def display_name(self):

        name = [self.node_type]

        if self.text:
            name.append(f"{self.text[:32].strip()}...")
        if self.link:
            name.append(f"{self.link[:32].strip()}...")
        if self.media:
            name.append(MediaManager.get_filename(self.media.name))

        return ":".join(name)

    @property
    def node_type(self):

        _type = []

        if self.text:
            _type.append("text")
        if self.link:
            _type.append("link")
        if self.media:
            _type.append(MediaManager.get_type(self.media.name))

        return "/".join(_type)
