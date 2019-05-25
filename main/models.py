import uuid

from django.db import models


class Author(models.Model):

    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=256, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    pinged = models.DateTimeField(auto_now_add=True)
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
    author = models.ForeignKey(Author,
                               on_delete=models.DO_NOTHING)
    title  = models.CharField(max_length=256, blank=True)
    publication  = models.CharField(max_length=256, blank=True)
    chapter  = models.CharField(max_length=256, blank=True)
    date  = models.CharField(max_length=256, blank=True)
    website  = models.CharField(max_length=256, blank=True)
    notes  = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    pinged = models.DateTimeField(auto_now_add=True)

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
    color = models.CharField(max_length=64, blank=True)
    pinned = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    pinged = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('name', )
        verbose_name = 'tag'
        verbose_name_plural = 'tags'

    def __str__(self):
        return f"<Tag:{self.slug}>"


class Collection(models.Model):

    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=256, unique=True)
    color = models.CharField(max_length=64, blank=True)
    pinned = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    pinged = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('name', )
        verbose_name = 'collection'
        verbose_name_plural = 'collections'

    def __str__(self):
        return f"<Collection:{self.slug}>"


class Passage(models.Model):

    uuid = models.UUIDField(default=uuid.uuid4)
    body = models.TextField()
    tags = models.ManyToManyField(Tag, blank=True)
    collections = models.ManyToManyField(Collection, blank=True)
    notes  = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now_add=True)
    origin = models.ForeignKey(Origin,
                               on_delete=models.DO_NOTHING,
                               default=default_origin)
    is_starred = models.BooleanField(default=False)
    is_api_refreshable = models.BooleanField(default=False)
    in_trash = models.BooleanField(default=False)
    source = models.ForeignKey(Source,
                               on_delete=models.DO_NOTHING,
                               default=default_source)

    class Meta:
        ordering = ('created', )
        verbose_name = 'passage'
        verbose_name_plural = 'passages'

    def __str__(self):
        return f"<Passage:{self.uuid}>"


"""
passage:
    <Passage>
        uuid
        body
        notes
        tags:
            <Tag>
                name
                slug
                color
                pinned
                description
                created
                pinged
        collections:
            <Collection>
                name
                slug
                color
                pinned
                description
                created
                pinged
        created
        modified
        origin:
            <Origin>
                name
                slug
        is_starred
        is_api_refreshable
        in_trash
        source:
            <Source>
                name
                slug
                author:
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