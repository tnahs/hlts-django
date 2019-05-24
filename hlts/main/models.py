import uuid

from django.db import models


def uuid_(prefix=""):
    """ Genrerate UUID4 with an optional prefix.
    """
    print(uuid.uuid4())
    print(type(uuid.uuid4()))
    uuid_ = f"{prefix}{uuid.uuid4()}"
    return uuid_.upper()


class Author(models.Model):

    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=256, unique=True)
    # Add a field so we can connect different name configurations
    # Krishnamurti == J Krishnamurit == Jiddu Krishnamurti

    class Meta:
        ordering = ('name', )
        verbose_name = 'author'
        verbose_name_plural = 'authors'

    def __str__(self):
        return f"<Author:{self.slug}>"


class Source(models.Model):

    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=256, unique=True)
    author = models.ForeignKey(Author, on_delete=models.DO_NOTHING, null=True)
    title  = models.CharField(max_length=256, blank=True)
    publication  = models.CharField(max_length=256, blank=True)
    chapter  = models.CharField(max_length=256, blank=True)
    date  = models.CharField(max_length=256, blank=True)
    website  = models.CharField(max_length=256, blank=True)
    notes  = models.TextField(blank=True)

    class Meta:
        ordering = ('name', )
        verbose_name = 'source'
        verbose_name_plural = 'sources'

    def __str__(self):
        return f"<Source:{self.slug}>"


class Origin(models.Model):

    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=256, unique=True)

    class Meta:
        ordering = ('name', )
        verbose_name = 'origin'
        verbose_name_plural = 'origins'

    def __str__(self):
        return f"<Origin:{self.slug}>"


def default_origin():

    try:
        origin = Origin.objects.get(pk=1)
    except Origin.DoesNotExist:
        origin = Origin(name='app', slug='app')
        origin.save()

    return origin


def default_source():

    try:
        source = Source.objects.get(pk=1)
    except Source.DoesNotExist:
        author = Author(name='Unknown', slug='unknown')
        author.save()
        source = Source(name='Unknown', slug='unknown', author=author)
        source.save()
    return source


class Tag(models.Model):

    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=256, unique=True)

    def __str__(self):
        return f"<Tag:{self.slug}>"


class Passage(models.Model):

    uuid = models.UUIDField(primary_key=True, default=uuid_, editable=False)
    body = models.TextField()
    notes  = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag)
    # collections = models.ManyToManyField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField()
    origin = models.ForeignKey(Origin,
                               on_delete=models.DO_NOTHING,
                               default=default_origin)
    in_trash = models.BooleanField(default=False)
    is_starred = models.BooleanField(default=False)
    is_refreshable = models.BooleanField(default=False)
    source = models.ForeignKey(Source,
                               on_delete=models.CASCADE,
                               default=default_source)

    class Meta:
        ordering = ('created', )
        verbose_name = 'passage'
        verbose_name_plural = 'passages'

    def __str__(self):
        return f"<Passage:{self.uuid}>"


"""
<Passage>
    uuid
    body
    notes
    created
    modified
    <Origin>
        name
        slug
    in_trash
    is_starred
    is_refreshable
    <Tags>
        name
        slug
        color
        pinned
        description
        created
        pinged
    <Collections>
        name
        slug
        color
        pinned
        description
        created
        pinged
    <Source>
        <Author>
            name
            slug
            created
            pinged
        title
        publication
        chapter
        date
        website
        created
        pinged
"""