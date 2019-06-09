
import uuid
from typing import Union

from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError
from django.dispatch import receiver


class Origin(models.Model):

    class Meta:
        unique_together = ["owner", "name"]

    owner = models.ForeignKey(get_user_model(),
                              related_name="origins",
                              on_delete=models.CASCADE)

    # Origin
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.name}>"


class Medium(models.Model):

    class Meta:
        verbose_name_plural = "media"
        unique_together = ["owner", "name"]

    owner = models.ForeignKey(get_user_model(),
                              related_name="media",
                              on_delete=models.CASCADE)

    # Medium
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.name}>"


class BaseModel(models.Model):

    class Meta:
        abstract = True

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)


class Author(BaseModel):
    """ Author.aka handles those with name variants i.e. 'John Dough',
    'J. Dough' and 'Dough, John J.' would be considered the same author. """

    class Meta:
        unique_together = ["owner", "name"]

    owner = models.ForeignKey(get_user_model(),
                              related_name="authors",
                              on_delete=models.CASCADE)

    # Author
    name = models.CharField(max_length=256)
    first_name = models.CharField(max_length=256, blank=True)
    last_name = models.CharField(max_length=256, blank=True)
    aka = models.ManyToManyField("self", blank=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.name}>"

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.name


class Source(BaseModel):
    """ A Source may have multiple authors. But two sources cannot
    have same set of multiple authors. This is enforced using a signal
    receiver verify_source_authors_is_unique() below. """

    class Meta:
        unique_together = ["owner", "name"]

    owner = models.ForeignKey(get_user_model(),
                              related_name="sources",
                              on_delete=models.CASCADE)

    # Source
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
        return self.name

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.name}>"

    @staticmethod
    def validate_authors(source_pk: Union[int, None], source_name: str,
                         source_authors: models.QuerySet):
        """ Custom validatation to make sure no two Sources have the same
        Source.name and Source.authors. Currently there's no way to set unique
        constraints that includes ManyToManyFields in Django.

        This method *must* be called manually in forms and APIs.

        All parameters are related to the Source to be added or edited.

        source_pk: Source's primary key
        source_name: Source's name
        source_authors: Source's new authors
        """

        # Return a QuerySet of all Source's with the same name as this source
        # while excluding this Source.
        sources = Source.objects.filter(name=source_name).exclude(pk=source_pk)

        if not sources:
            return

        new_author_pk_set = {author.pk for author in source_authors}

        # Check the Author primary key set against those of all found sources.
        # If there are any Sources that have the same name and the same Author
        # primary key set then raise a ValidationError.
        for source in sources:
            existing_author_pk_set = {author.pk for author in source.authors.all()}
            if existing_author_pk_set == new_author_pk_set:
                raise ValidationError(f"Source with selected author(s) already exists.")


class Tag(BaseModel):

    class Meta:
        unique_together = ["owner", "name"]

    owner = models.ForeignKey(get_user_model(),
                              related_name="tags",
                              on_delete=models.CASCADE)

    # Tag
    name = models.CharField(max_length=64)
    color = models.CharField(max_length=64, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.name}>"


class Collection(BaseModel):

    class Meta:
        unique_together = ["owner", "name"]

    owner = models.ForeignKey(get_user_model(),
                              related_name="collections",
                              on_delete=models.CASCADE)

    # Collection
    name = models.CharField(max_length=64)
    color = models.CharField(max_length=64, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.name}>"


class Topic(BaseModel):

    class Meta:
        unique_together = ["owner", "name"]

    owner = models.ForeignKey(get_user_model(),
                              related_name="topics",
                              on_delete=models.CASCADE)

    # Topic
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.name}>"


class Passage(BaseModel):

    class Meta:
        unique_together = ["owner", "uuid"]

    owner = models.ForeignKey(get_user_model(),
                              related_name="passages",
                              on_delete=models.CASCADE)

    # Passage
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    body = models.TextField()
    notes = models.TextField(blank=True)
    source = models.ForeignKey(Source,
                               on_delete=models.CASCADE,
                               default=1)
    tags = models.ManyToManyField(Tag, blank=True)
    collections = models.ManyToManyField(Collection, blank=True)
    origin = models.ForeignKey(Origin,
                               on_delete=models.CASCADE,
                               default=1)
    is_starred = models.BooleanField(default=False)
    in_trash = models.BooleanField(default=False)
    is_refreshable = models.BooleanField(default=False)

    # Read-only
    topics = models.ManyToManyField(Topic, blank=True)
    related = models.ManyToManyField("self", blank=True)
    count_read = models.IntegerField(default=0)
    count_query = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.body[:64]}..."

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.uuid}>"


AppUser = get_user_model()


@receiver(post_save, sender=AppUser)
def init_new_user(instance: AppUser, created: bool, raw: bool, **kwargs):
    """
    Create default objects for new users.

    via https://docs.djangoproject.com/en/2.2/ref/signals/
    via https://stackoverflow.com/a/19427227

    created: True if a new record was created.
    raw: True if the model is saved exactly as presented i.e. when loading a
    fixture. One should not query/modify other records in the database as the
    database might not be in a consistent state yet.
    """

    if not created or raw:
        return

    origin = Origin.objects.create(name="app", owner=instance)
    origin.save()

    medium = Medium.objects.create(name="Unknown", owner=instance)
    medium.save()

    author = Author.objects.create(name="Unknown", owner=instance)
    author.save()

    source = Source.objects.create(name="Unknown", medium=medium, owner=instance)
    source.authors.add(author)
    source.save()
