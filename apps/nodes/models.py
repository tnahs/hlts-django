import uuid
from typing import List, Union

from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone


class CommonDataMixin(models.Model):
    class Meta:
        abstract = True

    # TODO: Add a method to stamp the time when a node is modified.
    date_created = models.DateTimeField(default=timezone.now)
    date_modified = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.__repr__()


class Individual(CommonDataMixin, models.Model):
    """ Individual.aka handles name variants i.e. 'John Dough', 'J. Dough'
    and 'Dough, John J.' would be considered the same individual. """

    class Meta:
        unique_together = ["user", "name"]

    user = models.ForeignKey(
        get_user_model(), related_name="individuals", on_delete=models.CASCADE
    )

    name = models.CharField(max_length=256)
    first_name = models.CharField(max_length=256, blank=True)
    last_name = models.CharField(max_length=256, blank=True)
    aka = models.ManyToManyField("self", blank=True)

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.display_name}>"

    @property
    def display_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.name


class SourceManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def get_or_create(
        self, user, name: str, individuals: List[Union[int, Individual, str]]
    ):

        # TODO: Add documentation.

        sources = (
            self.get_queryset()
            .filter(name=name, user=user)
            .annotate(count=models.Count("individuals"))
            .filter(count=len(individuals))
        )

        if sources:

            new_pks = Source.get_individuals_pks(user, individuals)

            for source in sources:
                source_pks = {i.pk for i in source.individuals.all()}
                if source_pks == new_pks:
                    return sources

        individuals = Source.get_or_create_individuals(user, individuals)

        source = self.get_queryset().create(name=name, user=user)

        source.individuals.set(individuals)
        source.save()

        return source


class Source(CommonDataMixin, models.Model):

    user = models.ForeignKey(
        get_user_model(), related_name="sources", on_delete=models.CASCADE
    )

    name = models.CharField(max_length=256, blank=True)
    individuals = models.ManyToManyField(Individual, blank=True)
    url = models.URLField(max_length=256, blank=True)
    date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    objects = SourceManager()

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.name}{self.by}>"

    @property
    def display_name(self):
        return f"{self.name}{self.by}"

    @property
    def by(self):
        if self.individuals:
            individuals = ", ".join([i.display_name for i in self.individuals.all()])
            return f" - {individuals}"

    # NOTE: Field validation has be done at the form/serializer level because
    # of the way Django handles many-to-many relationships. Primary keys are
    # needed to perform the Model.clean() method when validating a unique
    # together between a field and a many-to-many relationship. The following
    # validation methods **must** be called before any database transaction.

    @staticmethod
    def validate_unique_together(
        user,
        name: str,
        individuals: List[Union[int, Individual, str]],
        source_pk: int = None,
    ):
        """ A Source may have multiple individuals. But two sources cannot have
        the same set of individuals."""

        # TODO: Add documentation.

        sources = Source.objects.filter(name=name, user=user)

        if source_pk:
            sources = sources.exclude(pk=source_pk)

        sources = (
            sources.filter(name=name, user=user)
            .annotate(count=models.Count("individuals"))
            .filter(count=len(individuals))
        )

        if not sources:
            return

        new_pks = Source.get_individuals_pks(user, individuals)

        for source in sources:
            source_pks = {i.pk for i in source.individuals.all()}
            if source_pks == new_pks:
                raise ValidationError(
                    f"Source '{name}' with selected individuals already exists."
                )

    @staticmethod
    def get_individuals_pks(user, individuals: List[Union[int, Individual, str]]):

        # TODO: Add documentation.

        if not isinstance(individuals, list):
            raise TypeError(f"Argument 'individuals' must be of type list.")

        if not individuals:
            return []

        if isinstance(individuals[0], int):
            return individuals
        elif isinstance(individuals[0], Individual):
            return {i.pk for i in individuals}
        elif isinstance(individuals[0], str):
            pks = []
            for name in individuals:
                try:
                    obj = Individual.objects.get(name=name, user=user)
                except Individual.DoesNotExist:
                    obj = None
                pks.add(obj.pk)
            return pks
        else:
            raise TypeError(
                f"Unrecognized type {type(individuals[0])} in {individuals}."
            )

    @staticmethod
    def get_or_create_individuals(user, individuals: List[Union[int, Individual, str]]):

        # TODO: Add documentation.

        if not isinstance(individuals, list):
            raise TypeError(f"Argument 'individuals' must be of type list.")

        if not individuals:
            return []

        if isinstance(individuals[0], Individual):
            [i.save() for i in individuals]
            return individuals
        elif isinstance(individuals[0], int):
            return [Individual.objects.get(pk=pk, user=user) for pk in individuals]
        elif isinstance(individuals[0], str):
            objs = []
            for name in individuals:
                try:
                    obj = Individual.objects.get(name=name, user=user)
                except Individual.DoesNotExist:
                    obj = Individual.objects.create(name=name, user=user)
                objs.add(obj)
            return objs
        else:
            raise TypeError(
                f"Unrecognized type {type(individuals[0])} in {individuals}."
            )


class Tag(CommonDataMixin, models.Model):
    class Meta:
        unique_together = ["user", "name"]

    user = models.ForeignKey(
        get_user_model(), related_name="tags", on_delete=models.CASCADE
    )

    name = models.CharField(max_length=64)

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.name}>"


class Collection(CommonDataMixin, models.Model):
    class Meta:
        unique_together = ["user", "name"]

    user = models.ForeignKey(
        get_user_model(), related_name="collections", on_delete=models.CASCADE
    )

    name = models.CharField(max_length=64)
    color = models.CharField(max_length=32)
    description = models.TextField()

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.name}>"


class Origin(CommonDataMixin, models.Model):
    class Meta:
        unique_together = ["user", "name"]

    user = models.ForeignKey(
        get_user_model(), related_name="origins", on_delete=models.CASCADE
    )

    name = models.CharField(max_length=128)

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.name}>"


class Topic(CommonDataMixin, models.Model):
    class Meta:
        unique_together = ["user", "name"]

    user = models.ForeignKey(
        get_user_model(), related_name="topics", on_delete=models.CASCADE
    )

    name = models.CharField(max_length=64)

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.name}>"


""" Nodes """


def dir_user_files(instance, filename):
    # TODO Is there a cleaner way to do this?
    # MEDIA_ROOT/user_<pk>/<filename>
    return instance.user.dir_media / filename


class Node(CommonDataMixin, models.Model):
    class Meta:
        unique_together = ["user", "uuid"]

    user = models.ForeignKey(
        get_user_model(), related_name="nodes", on_delete=models.CASCADE
    )

    uuid = models.UUIDField(default=uuid.uuid4, unique=True)

    # TODO: Validate that either text or file has a value.
    text = models.TextField(blank=True)
    # TODO: Have this dynamically find out file type. Only accept supported
    # file formats. Send the file to MEDIA_ROOT/user_<pk>/images/<filename>
    # Then mark the Node as a certain "type".
    file = models.FileField(upload_to=dir_user_files, blank=True)

    source = models.ForeignKey(Source, on_delete=models.CASCADE, null=True, blank=True)
    notes = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    collections = models.ManyToManyField(Collection, blank=True)

    origin = models.ForeignKey(Origin, on_delete=models.CASCADE, null=True, blank=True)
    in_trash = models.BooleanField(default=False)
    is_starred = models.BooleanField(default=False)

    related = models.ManyToManyField("self", blank=True)

    # Read-only
    topics = models.ManyToManyField(Topic, blank=True)
    related_auto = models.ManyToManyField("self", blank=True)

    def __repr__(self):

        name = []

        if self.text:
            name.append(f"{self.text[:64].strip()}")
        if self.file:
            name.append(f"{self.file.name}")

        name = ":".join(name)

        return f"<{self.__class__.__name__}:{name}>"
