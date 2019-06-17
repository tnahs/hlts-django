
import uuid
from typing import Union, List

from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError
from django.dispatch import receiver


""" Node Data """


class NodeData(models.Model):

    class Meta:
        abstract = True

    # Read-only
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)


class Origin(NodeData):

    class Meta:
        verbose_name = "NodeData Origin"
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


class Individual(NodeData):
    """ Individual.aka handles those with name variants i.e. 'John Dough',
    'J. Dough' and 'Dough, John J.' would be considered the same individual. """

    class Meta:
        verbose_name = "NodeData Individual"
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


class Source(NodeData):
    """ A Source may have multiple individuals. But two sources cannot
    have same set of multiple individuals. This is enforced using a signal
    receiver verify_source_individuals_is_unique() below. """

    class Meta:
        verbose_name = "NodeData Source"
        # unique_together = ("user", "name")

    user = models.ForeignKey(get_user_model(),
                            related_name="sources",
                            on_delete=models.CASCADE)

    # Source
    name = models.CharField(max_length=256)
    individuals = models.ManyToManyField(Individual,
                                         blank=True)
    url = models.URLField(max_length=256, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    # Read-only
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.name}>"

    @staticmethod
    def validate_individuals(source_name: str,
                             source_individuals: models.QuerySet,
                             source_pk: Union[int, None] = None):
        """ Custom validatation to make sure no two Sources have the same
        Source.name and Source.individuals. Currently there's no way to set unique
        constraints that includes ManyToManyFields in Django.

        This method *must* be called manually in forms and APIs.

        All parameters are related to the Source to be added or edited.

        source_pk: Source's primary key
        source_name: Source's name
        source_individuals: Source's new individuals
        """

        # FIXME this needs to also be filtered by the user.
        sources = Source.objects.filter(name=source_name)

        if source_pk:
            sources = sources.exclude(pk=source_pk)

        if not sources:
            return

        pk_set = {individual.pk for individual in source_individuals}
        individuals_names = ", ".join({individual.name for individual in source_individuals})

        # Check the Individual primary key set against those of all found sources.
        # If there are any Sources that have the same name and the same Individual
        # primary key set then raise a ValidationError.
        for source in sources:
            existing_pk_set = {individual.pk for individual in source.individuals.all()}
            if existing_pk_set == pk_set:
                raise ValidationError(f"Source '{source_name}' by '{individuals_names}' "
                                      f"already exists.")

    @staticmethod
    def validate_unique_source_individuals(user,
                                           name: str,
                                           source_pk: int = None,
                                           individuals_pks: List[int] = None,
                                           individuals_qs: models.QuerySet = None,
                                           individuals_names: List[str] = None):

        sources = Source.objects.filter(name=name, user=user)

        if source_pk:
            sources = sources.exclude(pk=source_pk)

        if not sources:
            return

        pk_set = set()
        individuals_display_names = ""

        if individuals_pks:

            pk_set = individuals_pks
            individuals_display_names = ", ".join(Individual.objects.get(pk=pk).name for pk in pk_set)

        elif individuals_qs:

            pk_set = {individual.pk for individual in individuals_qs}
            individuals_display_names = ", ".join({individual.name for individual in individuals_qs})

        elif individuals_names:

            for individual in individuals_names:

                try:
                    obj = Individual.objects.get(
                        name=individual,
                        user=user
                    )
                except Individual.DoesNotExist:
                    pk_set.add(-1)
                else:
                    pk_set.add(obj.pk)

            individuals_display_names = ", ".join(individuals_names)

        # Check the Individual primary key set against those of all found sources.
        # If there are any Sources that have the same name and the same Individual
        # primary key set then raise a ValidationError.
        for source in sources:
            existing_pk_set = {individual.pk for individual in source.individuals.all()}
            if existing_pk_set == pk_set:
                raise ValidationError(f"Source '{name}' by '{individuals_display_names}' already exists.")

    @staticmethod
    def get_or_raise(user,
                     name: str,
                     individuals_pks: List[int] = None,
                     individuals_qs: models.QuerySet = None,
                     individuals_names: List[str] = None):

        sources = Source.objects.filter(name=name, user=user)

        if not sources:
            raise ValidationError(f"Source '{name}' does not exist.",
                                  code="source_only")

        pk_set = set()
        individuals_display_names = ""

        if individuals_pks:

            pk_set = individuals_pks
            individuals_display_names = ", ".join(Individual.objects.get(pk=pk).name for pk in pk_set)

        elif individuals_qs:

            pk_set = {individual.pk for individual in individuals_qs}
            individuals_display_names = ", ".join({individual.name for individual in individuals_qs})

        elif individuals_names:

            for individual in individuals_names:

                try:
                    obj = Individual.objects.get(
                        name=individual,
                        user=user
                    )
                except Individual.DoesNotExist:
                    pk_set.add(-1)
                else:
                    pk_set.add(obj.pk)

            individuals_display_names = ", ".join(individuals_names)

        for source in sources:
            existing_pk_set = {individual.pk for individual in source.individuals.all()}
            if existing_pk_set == pk_set:
                return source

        raise ValidationError(f"Source '{name}' by '{individuals_display_names}' does not exist.",
                              code="source_and_individual")


class Tag(NodeData):

    class Meta:
        verbose_name = "NodeData Tag"
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


class Collection(NodeData):

    class Meta:
        verbose_name = "NodeData Collection"
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


class Topic(NodeData):

    class Meta:
        verbose_name = "NodeData Topic"
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

    related = models.ManyToManyField("self", blank=True)

    # QUESTION: Is there any way to have this display the node type?
    def __str__(self):
        return self.__class__.__name__
"""


class Node(models.Model):

    class Meta:
        abstract = True

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


class Text(Node):

    class Meta:
        verbose_name = "Node Text"
        unique_together = ["user", "uuid"]

    user = models.ForeignKey(get_user_model(),
                             related_name="texts",
                             on_delete=models.CASCADE)

    # Text
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    body = models.TextField()

    def __str__(self):
        return f"{self.body[:64]}..."

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.uuid}>"


class Image(Node):

    class Meta:
        verbose_name = "Node Image"

    user = models.ForeignKey(get_user_model(),
                            related_name="images",
                            on_delete=models.CASCADE)

    # Image
    file = models.ImageField(upload_to=Node.dir_images)
    name = models.CharField(max_length=128, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.file.url

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.file.url}>"


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
