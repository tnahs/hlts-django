
import uuid
import datetime

from django.db import models
from django.db.models.signals import m2m_changed
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.dispatch import receiver


"""
Basic Passage structure:

<passage>
    uuid: uuid
    body: string
    notes: string
    source: obj (OtoM)
        <source>
            name: string
            authors: list[obj] (MtoM)
                <author>
                    name: string
                    aka: list[obj] (MtoM)
                        <author>
                            ...
                    created: datetime
                    modified: datetime
                    pinged: datetime
            publication:
            url: url
            date: datetime
            notes: string
            medium: obj (OtoM)
                <medium>
                    name: string
            created: datetime
            modified: datetime
            pinged: datetime
    tags: list[obj] (MtoM)
        <tag>
            name: string
            color: string
            description: string
            pinned: bool
            created: datetime
            modified: datetime
            pinged: datetime
    collections: list[obj] (MtoM)
        <collection>
            name: string
            color: string
            pinned: bool
            description: string
            created: datetime
            modified: datetime
            pinged: datetime
    topics: list[obj] (MtoM)
        <topic>
            name: string
            created: datetime
            modified: datetime
            pinged: datetime
    origin: obj (OtoM)
        <origin>
            name: string
            created: datetime
            modified: datetime
            pinged: datetime
    is_starred: bool
    is_refreshable: bool
    is_trash: bool
    created: datetime
    modified: datetime
    pinged: datetime
"""


""" TODO: replace with fixtures """


def default_origin():

    try:
        origin = Origin.objects.get(pk=1)
    except Origin.DoesNotExist:
        origin = Origin(name="app")
        origin.save()

    return origin.pk


def default_medium():

    try:
        medium = Medium.objects.get(pk=1)
    except Medium.DoesNotExist:
        medium = Medium(name="Unknown")
        medium.save()

    return medium.pk


def default_source():

    try:
        source = Source.objects.get(pk=1)
    except Source.DoesNotExist:

        try:
            author = Author.objects.get(pk=1)
        except Author.DoesNotExist:
            author = Author(name="Unknown")
            author.save()

        source = Source(name="Unknown")
        # source.save(commit=False)

        # ns = Source.objects.get(pk=1)
        source.save()
        source.authors.add(author)
        source.save()

    return source.pk


class Origin(models.Model):

    name = models.CharField(max_length=128, unique=True,)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.name}>"


class Medium(models.Model):

    class Meta:
        verbose_name_plural = "media"

    name = models.CharField(max_length=128, unique=True,)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.name}>"


class BaseModel(models.Model):

    class Meta:
        abstract = True

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    pinged = models.DateTimeField(auto_now=True)

    def ping(self):
        """ TODO: https://docs.djangoproject.com/en/2.2/topics/i18n/timezones/ """
        self.pinged = datetime.datetime.utcnow()


class Author(BaseModel):
    """ Author.aka handles those with name variants i.e. 'John Dough',
    'J. Dough' and 'Dough, John J.' would be considered the same author. """

    name = models.CharField(max_length=256, unique=True)
    first_name = models.CharField(max_length=256, blank=True)
    last_name = models.CharField(max_length=256, blank=True)
    aka = models.ManyToManyField("self", blank=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.name}>"


class Source(BaseModel):
    """ A Source may have multiple authors. But two sources cannot
    have same set of multiple authors. This is enforced using a signal
    receiver verify_source_authors_is_unique() below. """

    name = models.CharField(max_length=256)
    authors = models.ManyToManyField(Author)
    publication = models.CharField(max_length=256, blank=True)
    url = models.URLField(max_length=256, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    medium = models.ForeignKey(Medium,
                               default=default_medium,
                               on_delete=models.CASCADE)

    @property
    def authors_as_str(self):
        return ", ".join([author.name for author in list(self.authors.all())])

    def __str__(self):
        return f"{self.name} - {self.authors_as_str}"

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.name}>"


@receiver(m2m_changed, sender=Source.authors.through)
def verify_source_authors_is_unique(sender, **kwargs):
    """ Signals in Django:
    https://docs.djangoproject.com/en/2.2/topics/signals/#receiver-functions
    https://docs.djangoproject.com/en/2.2/ref/signals/#m2m-changed

    FIXME: This does not work if the Source name is different and then changed
    after adding the m2m data.

    TODO: This works however the error does not bubble up to the user this way.
    https://stackoverflow.com/a/38167329
    https://docs.djangoproject.com/en/2.2/ref/forms/validation/#cleaning-and-validating-fields-that-depend-on-each-other
    """

    source = kwargs.get("instance", None)
    action = kwargs.get("action", None)
    author_pks = kwargs.get("pk_set", None)

    if action == "pre_add":

        similar_sources = Source.objects.filter(name=source.name)

        for source in similar_sources:

            this_source_author_pks = {a.pk for a in source.authors.all()}

            if this_source_author_pks == author_pks:

                author_set = [a.name for a in Author.objects.filter(pk__in=author_pks)]

                raise IntegrityError(
                    f"Source '{source.name}' with author set {author_set} already exists.")


class Tag(BaseModel):

    name = models.CharField(max_length=64, unique=True)
    color = models.CharField(max_length=64, blank=True)
    description = models.TextField(blank=True)
    pinned = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.name}>"


class Collection(BaseModel):

    name = models.CharField(max_length=64, unique=True)
    color = models.CharField(max_length=64, blank=True)
    description = models.TextField(blank=True)
    pinned = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.name}>"


class Topic(BaseModel):

    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.name}>"


class Passage(BaseModel):

    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    body = models.TextField()
    notes = models.TextField(blank=True)
    source = models.ForeignKey(Source,
                                    on_delete=models.CASCADE,
                                    default=default_source)
    tags = models.ManyToManyField(Tag, blank=True)
    collections = models.ManyToManyField(Collection, blank=True)
    topics = models.ManyToManyField(Topic, blank=True)
    origin = models.ForeignKey(Origin,
                               on_delete=models.CASCADE,
                               default=default_origin)
    is_starred = models.BooleanField(default=False)
    is_refreshable = models.BooleanField(default=False)
    in_trash = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.body[:64]}..."

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.uuid}>"
