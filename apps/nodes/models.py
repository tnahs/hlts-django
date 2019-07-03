import pathlib
import uuid

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class CommonDataMixin(models.Model):

    # QUESTION: Do we need created/modified for all models?

    date_created = models.DateTimeField(default=timezone.now)
    date_modified = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True

    def __repr__(self):
        return self.__str__()

    def save(self, *args, **kwargs):
        self.date_modified = timezone.now()
        super().save(*args, **kwargs)


class IndividualManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def get_or_create(self, user, individuals):

        # TODO: Revisit and doucment...

        if not isinstance(individuals, (list, models.QuerySet)):
            raise TypeError(
                f"Argument 'individuals' must be of type list or QuerySet. "
                f"Received {type(individuals)}."
            )

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

    user = models.ForeignKey(
        get_user_model(), related_name="individuals", on_delete=models.CASCADE
    )

    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=256)
    first_name = models.CharField(max_length=256, blank=True)
    last_name = models.CharField(max_length=256, blank=True)

    """ Individual.aka handles name variants i.e. 'John Dough', 'J. Dough'
    and 'Dough, John J.' would be considered the same individual. """
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
    def get_pks(cls, user, individuals):
        """ Returns a set of primary keys from a list of various types of
        Individuals. Types include integers, model instances and strings.

        Used in Source.ojects.get() and Source.validate_unique_together() for
        checking the uniqueness between one set of Source/Individuals and
        another."""

        if not isinstance(individuals, (list, models.QuerySet)):
            raise TypeError(
                f"Argument 'individuals' must be of type list or QuerySet. "
                f"Received {type(individuals)}."
            )

        if not individuals:
            return []

        # Individuals were passed as a list of primary keys. Return unchanged.
        if isinstance(individuals[0], int):
            return individuals

        # Individuals were passed as a list of Individual instances. Compile a
        # set of their primary keys and return.
        elif isinstance(individuals[0], cls):
            return {i.pk for i in individuals}

        # Individuals were passed as a list of (presumably) Individual names.
        # Compile a list of all existing Individuals that match the list of
        # name. If no Individual exists (for this current user) then append
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
        elif isinstance(individuals[0], str):
            pks = []
            for name in individuals:
                try:
                    obj = cls.objects.get(name=name, user=user)
                    pks.append(obj.pk)
                except cls.DoesNotExist:
                    pks.append(None)
            return pks
        else:
            raise TypeError(
                f"Unrecognized type {type(individuals[0])} in {individuals}."
            )


class SourceManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def get_or_create(self, user, name, individuals, extra_data=None):
        """ Overwrites the QuerySet.get_or_create() function:
        via https://github.com/django/django/blob/master/django/db/models/query.py#L536
        """

        source = self.get(user, name, individuals)

        if source:
            return source

        return self.create(user, name, individuals, extra_data)

    def get(self, user, name, individuals):
        """
        Overwrites the QuerySet.get() function:
        via https://github.com/django/django/blob/master/django/db/models/query.py#L396

        Returns a Source with a specific set of Individuals. """

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

    def create(self, user, name, individuals, extra_data=None):
        """ Overwrites the QuerySet.create() function:
        via https://github.com/django/django/blob/master/django/db/models/query.py#L423

        Creates a Source with a specific set of Individuals. """

        individuals = Individual.objects.get_or_create(user, individuals)

        source = self.model(name=name, user=user, **extra_data)

        # Need to call .save() here for two reasons:
        # 1. An id is needed before a m2m relationshop can be created.
        # 2. The .create() method has been overwritten by this one.
        source.save(force_insert=True, using=self.db)
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
        """ A Source may have a set Individuals. But no two sources can have
        the same set of Individuals.

        Field validation must be done at the form/serializer level because of
        the way Django handles many-to-many relationships. Primary keys are
        needed to perform the Model.clean() method when validating a unique
        together between a field and a many-to-many relationship. The following
        validation methods **must** be called before any database transaction.
        """

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

    def __str__(self):
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

    def __str__(self):
        return f"<{self.__class__.__name__}:{self.name}>"


class Origin(CommonDataMixin, models.Model):

    user = models.ForeignKey(
        get_user_model(), related_name="origins", on_delete=models.CASCADE
    )

    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=128)

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


class Node(CommonDataMixin, models.Model):

    user = models.ForeignKey(
        get_user_model(), related_name="nodes", on_delete=models.CASCADE
    )

    id = models.UUIDField(default=uuid.uuid4, primary_key=True)

    # TODO: Validate that either text or media has a value.
    text = models.TextField(blank=True)
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
    # auto_ocr = models.TextField(blank=True)
    auto_tags = models.ManyToManyField(Tag, blank=True, related_name="auto_tagged")
    auto_related = models.ManyToManyField(
        "self", blank=True, related_name="auto_related"
    )

    def __str__(self):
        return f"<{self.__class__.__name__}:{self.display_name}>"

    @property
    def display_name(self):

        # TODO: Clean this up.

        name = [self.node_type]

        if self.text:
            name.append(f"{self.text[:32].strip()}...")

        if self.media:
            name.append(MediaManager.get_filename(self.media.name))

        return ":".join(name)

    @property
    def node_type(self):

        _type = []

        if self.text:
            _type.append("text")
        if self.media:
            _type.append(MediaManager.get_type(self.media.name))

        return "/".join(_type)
