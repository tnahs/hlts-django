
import uuid
from typing import Union

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

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


class Origin(models.Model):

    class Meta:
        unique_together = ["owner", "name"]

    owner = models.ForeignKey(User,
                              related_name="origins",
                              on_delete=models.CASCADE)
    name = models.CharField(max_length=128, unique=True,)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.name}>"


class Medium(models.Model):

    class Meta:
        verbose_name_plural = "media"
        unique_together = ["owner", "name"]

    owner = models.ForeignKey(User,
                              related_name="media",
                              on_delete=models.CASCADE)
    name = models.CharField(max_length=128)

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
        self.pinged = timezone.now()


class Author(BaseModel):
    """ Author.aka handles those with name variants i.e. 'John Dough',
    'J. Dough' and 'Dough, John J.' would be considered the same author. """

    class Meta:
        unique_together = ["owner", "name"]

    owner = models.ForeignKey(User,
                              related_name="authors",
                              on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
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

    class Meta:
        unique_together = ["owner", "name"]

    owner = models.ForeignKey(User,
                              related_name="sources",
                              on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    authors = models.ManyToManyField(Author)
    publication = models.CharField(max_length=256, blank=True)
    url = models.URLField(max_length=256, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    medium = models.ForeignKey(Medium,
                               default=1,
                               on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.authors_as_str}"

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.name}>"

    @property
    def authors_as_str(self):
        return ", ".join([author.name for author in list(self.authors.all())])

    @staticmethod
    def validate_authors(pk: Union[int, None], name: str, authors: models.QuerySet):
        """ Custom validatation to make sure no two Sources have the same
        Source.name and Source.authors. Currently there's no way to set unique
        constraints that includes ManyToManyFields.

        This method *must* be called manually in forms and de-serializers.

        All parameters are related to the Source to be added or edited.

        pk: Source's primary key
        name: Source's name
        authors: Source's new authors
        """

        similar_sources = Source.objects.filter(name=name).exclude(pk=pk)

        if not similar_sources:
            return

        new_author_pks = {author.pk for author in authors}

        for similar_source in similar_sources:
            author_pks = {a.pk for a in similar_source.authors.all()}
            if author_pks == new_author_pks:
                raise ValidationError(f"Source with selected author(s) already exists.")


class Tag(BaseModel):

    class Meta:
        unique_together = ["owner", "name"]

    owner = models.ForeignKey(User,
                              related_name="tags",
                              on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    color = models.CharField(max_length=64, blank=True)
    description = models.TextField(blank=True)
    pinned = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.name}>"


class Collection(BaseModel):

    class Meta:
        unique_together = ["owner", "name"]

    owner = models.ForeignKey(User,
                              related_name="collections",
                              on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    color = models.CharField(max_length=64, blank=True)
    description = models.TextField(blank=True)
    pinned = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.name}>"


class Topic(BaseModel):

    class Meta:
        unique_together = ["owner", "name"]

    owner = models.ForeignKey(User,
                              related_name="topics",
                              on_delete=models.CASCADE)
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.name}>"


class Passage(BaseModel):

    class Meta:
        unique_together = ["owner", "uuid"]

    owner = models.ForeignKey(User,
                              related_name="passages",
                              on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    body = models.TextField()
    notes = models.TextField(blank=True)
    source = models.ForeignKey(Source,
                               on_delete=models.CASCADE,
                               default=1)
    tags = models.ManyToManyField(Tag, blank=True)
    collections = models.ManyToManyField(Collection, blank=True)
    topics = models.ManyToManyField(Topic, blank=True)
    origin = models.ForeignKey(Origin,
                               on_delete=models.CASCADE,
                               default=1)
    is_starred = models.BooleanField(default=False)
    is_refreshable = models.BooleanField(default=False)
    in_trash = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.body[:64]}..."

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.uuid}>"
