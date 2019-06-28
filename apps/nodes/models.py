import uuid
import pathlib

from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone


VALID_IMAGE_TYPES = [".jpg", ".png", ".gif"]
VALID_AUDIO_TYPES = [".mp3", ".aiff"]
VALID_VIDEO_TYPES = [".mp4"]
VALID_DOCUMENT_TYPES = [".pdf", ".txt", ".md"]


class CommonDataMixin(models.Model):
    # QUESTION: Do we need created/modified for all models?
    date_created = models.DateTimeField(default=timezone.now)
    date_modified = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True

    def __str__(self):
        return self.__repr__()

    def save(self, *args, **kwargs):
        self.date_modified = timezone.now()
        super().save(*args, **kwargs)


class IndividualManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def get_or_create(self, user, individuals):

        if not isinstance(individuals, list):
            raise TypeError(f"Argument 'individuals' must be of type list.")

        if not individuals:
            return []

        if isinstance(individuals[0], self.model):
            [i.save() for i in individuals]
            return individuals
        elif isinstance(individuals[0], int):
            return [self.get(pk=pk, user=user) for pk in individuals]
        elif isinstance(individuals[0], str):
            objs = []
            for name in individuals:
                try:
                    obj = self.get(name=name, user=user)
                except self.model.DoesNotExist:
                    obj = self.create(name=name, user=user)
                objs.add(obj)
            return objs
        else:
            raise TypeError(
                f"Unrecognized type {type(individuals[0])} in {individuals}."
            )


class Individual(CommonDataMixin, models.Model):
    """ Individual.aka handles name variants i.e. 'John Dough', 'J. Dough'
    and 'Dough, John J.' would be considered the same individual. """

    user = models.ForeignKey(
        get_user_model(), related_name="individuals", on_delete=models.CASCADE
    )

    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=256)
    first_name = models.CharField(max_length=256, blank=True)
    last_name = models.CharField(max_length=256, blank=True)
    aka = models.ManyToManyField("self", blank=True)

    objects = IndividualManager()

    class Meta:
        unique_together = ("user", "name")

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.display_name}>"

    @property
    def display_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.name

    @classmethod
    def get_pks(cls, user, individuals):

        # TODO: Add documentation.

        if not isinstance(individuals, list):
            raise TypeError(f"Argument 'individuals' must be of type list.")

        if not individuals:
            return []

        if isinstance(individuals[0], int):
            return individuals
        elif isinstance(individuals[0], cls):
            return {i.pk for i in individuals}
        elif isinstance(individuals[0], str):
            pks = []
            for name in individuals:
                try:
                    obj = cls.objects.get(name=name, user=user)
                except cls.DoesNotExist:
                    obj = None
                pks.add(obj.pk)
            return pks
        else:
            raise TypeError(
                f"Unrecognized type {type(individuals[0])} in {individuals}."
            )


class SourceManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def get_or_create(self, user, name, individuals):

        # TODO: Add documentation.

        sources = (
            self.get_queryset()
            .filter(name=name, user=user)
            .annotate(count=models.Count("individuals"))
            .filter(count=len(individuals))
        )

        if sources:
            new_pks = Individual.get_pks(user, individuals)
            for source in sources:
                source_pks = {i.pk for i in source.individuals.all()}
                if source_pks == new_pks:
                    return source

        individuals = Individual.objects.get_or_create(user, individuals)

        source = self.get_queryset().create(name=name, user=user)
        source.individuals.set(individuals)
        source.save()

        return source


class Source(CommonDataMixin, models.Model):

    user = models.ForeignKey(
        get_user_model(), related_name="sources", on_delete=models.CASCADE
    )

    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
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

    @staticmethod
    def validate_unique_together(user, name, individuals, source_pk=None):
        """ A Source may have multiple individuals. But two sources cannot have
        the same set of individuals.

        NOTE: Field validation has be done at the form/serializer level because
        of the way Django handles many-to-many relationships. Primary keys are
        needed to perform the Model.clean() method when validating a unique
        together between a field and a many-to-many relationship. The following
        validation methods **must** be called before any database transaction.
        """

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

        new_pks = Individual.objects.get_individuals_pks(user, individuals)

        for source in sources:
            source_pks = {i.pk for i in source.individuals.all()}
            if source_pks == new_pks:
                raise ValidationError(
                    f"Source '{name}' with selected individuals already exists."
                )


class Tag(CommonDataMixin, models.Model):

    user = models.ForeignKey(
        get_user_model(), related_name="tags", on_delete=models.CASCADE
    )

    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=64)

    class Meta:
        unique_together = ("user", "name")

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.name}>"


class Collection(CommonDataMixin, models.Model):

    user = models.ForeignKey(
        get_user_model(), related_name="collections", on_delete=models.CASCADE
    )

    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=64)
    color = models.CharField(max_length=32, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ("user", "name")

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.name}>"


class Origin(CommonDataMixin, models.Model):

    user = models.ForeignKey(
        get_user_model(), related_name="origins", on_delete=models.CASCADE
    )

    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=128)

    class Meta:
        unique_together = ("user", "name")

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.name}>"


""" Nodes """


def media_manager(instance, filename):
    """ See apps.users.models.User """

    user = instance.user

    filetype = pathlib.Path(filename).suffix

    if filetype in VALID_IMAGE_TYPES:
        return user.dir_images / filename
    elif filetype in VALID_AUDIO_TYPES:
        return user.dir_audios / filename
    elif filetype in VALID_VIDEO_TYPES:
        return user.dir_videos / filename
    elif filetype in VALID_DOCUMENT_TYPES:
        return user.dir_documents / filename
    else:
        return user.dir_misc / filename


class Node(CommonDataMixin, models.Model):

    user = models.ForeignKey(
        get_user_model(), related_name="nodes", on_delete=models.CASCADE
    )

    id = models.UUIDField(default=uuid.uuid4, primary_key=True)

    # TODO: Validate that either text or media has a value.
    text = models.TextField(blank=True)
    media = models.FileField(upload_to=media_manager, blank=True)

    source = models.ForeignKey(Source, on_delete=models.CASCADE, null=True, blank=True)
    notes = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    collections = models.ManyToManyField(Collection, blank=True)

    origin = models.ForeignKey(Origin, on_delete=models.CASCADE, null=True, blank=True)
    in_trash = models.BooleanField(default=False)
    is_starred = models.BooleanField(default=False)

    related = models.ManyToManyField("self", blank=True)

    # Read-only
    auto_tags = models.ManyToManyField(Tag, blank=True, related_name="auto_tagged")
    auto_related = models.ManyToManyField(
        "self", blank=True, related_name="auto_related"
    )

    @property
    def display_name(self):

        name = []

        if self.text:
            name.append(f"{self.text[:64].strip()}")
        if self.media:
            name.append(f"{self.media.name}")

        name = ":".join(name)

        return name

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.display_name}>"

    @property
    def media_type(self):

        if self.media:

            filetype = pathlib.Path(self.media.name).suffix

            if filetype in VALID_IMAGE_TYPES:
                return "image"
            elif filetype in VALID_AUDIO_TYPES:
                return "audio"
            elif filetype in VALID_VIDEO_TYPES:
                return "video"
            elif filetype in VALID_DOCUMENT_TYPES:
                return "document"
            else:
                return "misc"
