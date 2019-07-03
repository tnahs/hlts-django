import pytest
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.utils import timezone

from .models import Collection, Node, Tag


@pytest.fixture
@pytest.mark.django_db
def user():
    email = "user@email.com"
    password = "password"
    return get_user_model().objects.create_user(email=email, password=password)


@pytest.mark.django_db
class TestTag:

    name = "tag"

    def test_create(self, user):

        tag = Tag.objects.create(name=self.name, user=user)

        assert tag.name == self.name
        assert tag.user == user

        # Test __str__ and __repr__ return strings.
        assert isinstance(tag.__str__(), str)
        assert isinstance(tag.__repr__(), str)

    def test_missing_user(self):
        """ Test Tag always has a user. """

        with pytest.raises(IntegrityError):
            Tag.objects.create(name=self.name)

    def test_unique_together(self, user):
        """ Test no two Tags have the same name and user. """

        Tag.objects.create(name=self.name, user=user)

        with pytest.raises(IntegrityError):
            Tag.objects.create(name=self.name, user=user)


@pytest.mark.django_db
class TestCollection:

    name = "collection"
    color = "color"
    description = "Collection description."
    fields = {"name": name, "color": color, "description": description}

    def test_create(self, user):

        collection = Collection.objects.create(user=user, **self.fields)

        assert collection.name == self.name
        assert collection.user == user

        # Test all extra_fileds map correctly to model.
        for name, value in self.fields.items():
            assert getattr(collection, name, value) == value

        # Test __str__ and __repr__ return strings.
        assert isinstance(collection.__str__(), str)
        assert isinstance(collection.__repr__(), str)

    def test_create_minimum_requirements(self, user):
        """ Test user can create Collection with name only. """

        collection = Collection.objects.create(name=self.name, user=user)

        assert collection.name == self.name
        assert collection.user == user

    def test_missing_user(self):
        """ Test Collection always has a user. """

        with pytest.raises(IntegrityError):
            Collection.objects.create(name=self.name)

    def test_unique_together(self, user):
        """ Test no two Collections have the same name and user. """

        Collection.objects.create(name=self.name, user=user)

        with pytest.raises(IntegrityError):
            Collection.objects.create(name=self.name, user=user)


@pytest.mark.django_db
class TestNode:

    id = "538b847e-9c14-11e9-a2a3-2a2ae2dbcce4"
    text = "Node text."
    media = "/path/to/media.png"
    # source
    notes = "Node notes"
    tags = {"tag1", "tag2", "tag3"}
    collections = {"collection1", "collection2", "collection3"}
    # origin
    in_trash = False
    is_starred = False
    # related
    # auto_ocr
    # auto_tags
    # auto_related
    date_created = timezone.now().isoformat()

    # FIXME If the date_modified it set to a specific date at creation time,
    # it is immediately replaced when the .save() method is called. We want to
    # be able to set the date_modified time without affecting it when .save()
    # is called.
    # date_modified = timezone.now().isoformat()

    fields = {
        "text": text,
        "media": media,
        "notes": notes,
        "in_trash": in_trash,
        "is_starred": is_starred,
        "date_created": date_created,
        # "date_modified": date_modified,
    }

    def tag_objs(self, user):
        tag_objs = []
        for tag in self.tags:
            obj = Tag.objects.create(name=tag, user=user)
            tag_objs.append(obj)
        return tag_objs

    def collection_objs(self, user):
        collection_objs = []
        for collection in self.collections:
            obj = Collection.objects.create(name=collection, user=user)
            collection_objs.append(obj)
        return collection_objs

    def test_create(self, user):
        """ Test full creation of a Node. """

        node = Node.objects.create(user=user, **self.fields)

        tag_objs = self.tag_objs(user)
        node.tags.set(tag_objs)

        collection_objs = self.collection_objs(user)
        node.collections.set(collection_objs)

        assert node.user == user

        # Test m2m relationships bound.
        assert node.tags.count() == len(self.tags)
        assert node.collections.count() == len(self.collections)

        # Test all fileds map correctly to model.
        for name, value in self.fields.items():
            assert getattr(node, name, value) == value

        # Test __str__ and __repr__ return strings.
        assert isinstance(node.__str__(), str)
        assert isinstance(node.__repr__(), str)

    def test_create_minimum_requirements(self, user):
        """ Test user can create Node with text only or media only. """

        node_text = Node.objects.create(text=self.text, user=user)
        assert node_text.text == self.text
        assert node_text.user == user

        node_media = Node.objects.create(media=self.media, user=user)
        assert node_media.media == self.media
        assert node_media.user == user

        """
        # QUESTION: Do we actually want this functionality?
        # FIXME Either text or media must be set, both cannot be empty...
        with pytest.raises(IntegrityError):
            Node.objects.create(user=user)
        """

    def test_missing_user(self):
        """ Test Node always has a user. """

        with pytest.raises(IntegrityError):
            Node.objects.create(text=self.text)
