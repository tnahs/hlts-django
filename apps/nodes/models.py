
import uuid
from typing import List, Union

from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError
from django.dispatch import receiver


""" Node Data """


class NodeAttribute(models.Model):

    class Meta:
        abstract = True

    # Read-only
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)


class Origin(NodeAttribute):

    class Meta:
        verbose_name = "NodeAttribute Origin"
        unique_together = ("user", "name")

    user = models.ForeignKey(get_user_model(),
                            related_name="origins",
                            on_delete=models.CASCADE)

    # Origin
    name = models.CharField(max_length=128)

    # Read-only
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.name}>"


class Individual(NodeAttribute):
    """ Individual.aka handles those with name variants i.e. 'John Dough',
    'J. Dough' and 'Dough, John J.' would be considered the same individual. """

    class Meta:
        verbose_name = "NodeAttribute Individual"
        unique_together = ("user", "name")

    user = models.ForeignKey(get_user_model(),
                             related_name="individuals",
                             on_delete=models.CASCADE)

    # Individual
    name = models.CharField(max_length=256)
    first_name = models.CharField(max_length=256, blank=True)
    last_name = models.CharField(max_length=256, blank=True)
    aka = models.ManyToManyField("self", blank=True)

    # Read-only
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.name}>"

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.name


class SourceManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset()

    def get_or_create(self, user, name: str,
                      individuals: List[Union[int, Individual, str]]):

        # TODO: Document this.

        sources = self.get_queryset().filter(name=name, user=user)

        # TODO: Add that query method that culled itself by the number of items
        # in the m2m relationship.

        if not sources:
            return self.get_queryset().create(name=name, user=user)

        new_pks = Source.get_individuals_pks(user, individuals)

        for source in sources:
            source_pks = {i.pk for i in source.individuals.all()}
            if source_pks == new_pks:
                return source

        return self.get_queryset().create(name=name, user=user)


class Source(NodeAttribute):
    """ A Source may have multiple individuals. But two sources cannot
    have same set of multiple individuals. This is enforced using a signal
    receiver verify_source_individuals_is_unique() below. """

    class Meta:
        verbose_name = "NodeAttribute Source"

    user = models.ForeignKey(get_user_model(),
                            related_name="sources",
                            on_delete=models.CASCADE)

    # Source
    name = models.CharField(max_length=256, blank=True)
    individuals = models.ManyToManyField(Individual,
                                         blank=True)
    url = models.URLField(max_length=256, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    # Read-only
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    objects = SourceManager()

    def __str__(self):

        if not self.individuals:
            return self.name

        if not self.name:
            return self.by

        return f"{self.name} - {self.by}"

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.__str__()}>"

    @property
    def by(self):
        return ", ".join([i.name for i in self.individuals.all()])

    # NOTE: Field validation has be done at the form/serializer level because
    # of the way Django handles many-to-many relationships. Primary keys are
    # needed to perform the Model.clean() method when validating a unique
    # together between a field and a many-to-many relationship. The following
    # validation methods **must** be called before any database transaction.

    @staticmethod
    def validate_unique_together(user, name: str,
                                 individuals: List[Union[int, Individual, str]],
                                 source_pk: int = None):
        # TODO: Document this.

        sources = Source.objects.filter(name=name, user=user)

        # TODO: Add that query method that culled itself by the number of items
        # in the m2m relationship.

        if source_pk:
            sources = sources.exclude(pk=source_pk)

        if not sources:
            return

        new_pks = Source.get_individuals_pks(user, individuals)

        for source in sources:
            source_pks = {i.pk for i in source.individuals.all()}
            if source_pks == new_pks:
                raise ValidationError(
                    f"Source '{name}' with selected individuals already exists.")

    @staticmethod
    def get_individuals_pks(user, individuals: List[Union[int, Individual, str]]):

        # TODO: Document this.

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
                    pks.add(None)
                else:
                    pks.add(obj.pk)
            return pks
        else:
            raise TypeError(f"Unrecognized type {type(individuals[0])} in "
                            f"{individuals}.")


class Tag(NodeAttribute):

    class Meta:
        verbose_name = "NodeAttribute Tag"
        unique_together = ("user", "name")

    user = models.ForeignKey(get_user_model(),
                            related_name="tags",
                            on_delete=models.CASCADE)

    # Tag
    name = models.CharField(max_length=64)

    # Read-only
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.name}>"


class Collection(NodeAttribute):

    class Meta:
        verbose_name = "NodeAttribute Collection"
        unique_together = ("user", "name")

    user = models.ForeignKey(get_user_model(),
                             related_name="collections",
                             on_delete=models.CASCADE)

    # Collection
    name = models.CharField(max_length=64)

    # Read-only
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.name}>"


class Topic(NodeAttribute):

    class Meta:
        verbose_name = "NodeAttribute Topic"
        unique_together = ("user", "name")

    user = models.ForeignKey(get_user_model(),
                             related_name="topics",
                             on_delete=models.CASCADE)

    # Topic
    name = models.CharField(max_length=64)

    # Read-only
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.name}>"


""" Nodes """

"""
class BaseNode():

    # TODO: Whats the best way to creat a connection between nodes?


    # QUESTION: Is there any way to have this display the node type?
    def __str__(self):
        return self.__class__.__name__
"""


class Node(models.Model):

    class Meta:
        unique_together = ["user", "uuid"]

    user = models.ForeignKey(get_user_model(),
                             related_name="nodes",
                             on_delete=models.CASCADE)

    uuid = models.UUIDField(default=uuid.uuid4, unique=True)

    body = models.TextField()
    file = models.FileField(upload_to="files", blank=True)

    source = models.ForeignKey(Source,
                               on_delete=models.CASCADE,
                               null=True,
                               blank=True)
    notes = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    collections = models.ManyToManyField(Collection, blank=True)

    origin = models.ForeignKey(Origin,
                               on_delete=models.CASCADE,
                               null=True,
                               blank=True)
    in_trash = models.BooleanField(default=False)
    is_starred = models.BooleanField(default=False)

    related = models.ManyToManyField("self", blank=True)

    # Read-only
    topics = models.ManyToManyField(Topic, blank=True)
    count_seen = models.IntegerField(default=0)
    count_query = models.IntegerField(default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    @staticmethod
    def dir_images(instance, filename):
        # MEDIA_ROOT/user_<pk>/images/<filename>
        return instance.user.dir_images / filename

    def __str__(self):
        return f"{self.body[:64]}..."

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.uuid}>"


# class Text(Node):

#     class Meta:
#         verbose_name = "Node Text"
#         unique_together = ["user", "uuid"]

#     user = models.ForeignKey(get_user_model(),
#                              related_name="texts",
#                              on_delete=models.CASCADE)

#     # Text
#     uuid = models.UUIDField(default=uuid.uuid4, unique=True)
#     body = models.TextField()

#     def __str__(self):
#         return f"{self.body[:64]}..."

#     def __repr__(self):
#         return f"<{self.__class__.__name__}:{self.uuid}>"


# class Image(Node):

#     class Meta:
#         verbose_name = "Node Image"

#     user = models.ForeignKey(get_user_model(),
#                             related_name="images",
#                             on_delete=models.CASCADE)

#     # Image
#     file = models.ImageField(upload_to=Node.dir_images)
#     name = models.CharField(max_length=128, blank=True)
#     description = models.TextField(blank=True)

#     def __str__(self):
#         return self.file.url

#     def __repr__(self):
#         return f"<{self.__class__.__name__}:{self.file.url}>"


User = get_user_model()


@receiver(post_save, sender=User)
def init_new_user(instance: User, created: bool, raw: bool, **kwargs):
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

    origin = Origin.objects.create(name="app", user=instance)
    origin.save()
