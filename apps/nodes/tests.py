import pytest
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.utils import timezone

from .models import Collection, Individual, Node, Origin, Source, Tag


# TODO:
#  Test create from dictionaries.
#  Text create objects and append to parents.
#  Text update from dictionaries.
#  Text update objects and append to parents.


@pytest.fixture
@pytest.mark.django_db
def user():
    email = "user@email.com"
    password = "password"
    return get_user_model().objects.create_user(email=email, password=password)


@pytest.mark.django_db
class TestSource:

    source_name = "Test Source"
    source_individuals = ["Test Individual1", "Test Individual2"]
    url = "http://www.source-url.com"
    date = "January, 1, 2000"
    notes = "Source notes."

    def test_create(self, user):

        fields = {
            "user": user,
            "name": self.source_name,
            "individuals": self.source_individuals,
            # "url": self.url,
            # "date": self.date,
            # "notes": self.notes,
        }

        source = Source.objects.create(fields)

        assert source.user == user
        assert source.name == self.source_name
        assert source.individuals.count() == len(self.source_individuals)
        # assert source.url == self.url
        # assert source.data == self.data
        # assert source.notes == self.notes

    def test_create_minimum(self, user):

        fields = {
            "user": user,
            "name": self.source_name,
            "individuals": self.source_individuals,
        }

        source = Source.objects.create(fields)

        assert source.user == user
        assert source.name == self.source_name
        assert source.individuals.count() == len(self.source_individuals)


@pytest.mark.django_db
class TestIndividual:
    pass


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

    def test_create(self, user):

        fields = {
            "name": self.name,
            "color": self.color,
            "description": self.description,
        }

        collection = Collection.objects.create(user=user, **fields)

        assert collection.name == self.name
        assert collection.user == user

        # Test all extra_fileds map correctly to model.
        for name, value in fields.items():
            assert getattr(collection, name, value) == value

        # Test __str__ and __repr__ return strings.
        assert isinstance(collection.__str__(), str)
        assert isinstance(collection.__repr__(), str)

    def test_create_minimum(self, user):
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
class TestOrigin:
    pass


@pytest.mark.django_db
class TestNode:

    id = "538b847e-9c14-11e9-a2a3-2a2ae2dbcce4"
    text = "Node text."
    media = "/path/to/media.png"
    source_name = "Test Source"
    source_individuals = ["Test Individual1", "Test Individual2"]
    notes = "Node notes."
    tags = {"tag1", "tag2", "tag3"}
    collections = {"collection1", "collection2", "collection3"}
    origin = "app"
    in_trash = False
    is_starred = False
    # TODO: Create a dummy Node and relate it.
    related = []
    date_created = timezone.now().isoformat()
    # TODO: Figure out how to set date_modified without the .save() method
    # overwriting it.
    # date_modified = timezone.now().isoformat()

    def test_create(self, user):
        """ Test full creation of a Node. """

        fields = {
            "user": user,
            "id": self.id,
            "text": self.text,
            "media": self.media,
            "source": {
                "name": self.source_name,
                "individuals": self.source_individuals,
            },
            "notes": self.notes,
            "tags": self.tags,
            "collections": self.collections,
            "origin": self.origin,
            "in_trash": self.in_trash,
            "is_starred": self.is_starred,
            "related": self.related,
            "date_created": self.date_created,
            # "date_modified": self.date_modified,
        }

        node = Node.objects.create(fields)

        assert node.user == user
        assert node.id == self.id
        assert node.text == self.text
        assert node.media == self.media
        assert node.source.name == self.source_name
        assert node.source.individuals.count() == len(self.source_individuals)
        assert node.notes == self.notes
        assert node.tags.count() == len(self.tags)
        assert node.collections.count() == len(self.collections)
        assert node.origin.name == self.origin
        assert node.in_trash == self.in_trash
        assert node.is_starred == self.is_starred
        assert node.related.count() == len(self.related)
        assert node.date_created == self.date_created
        # assert node.date_modified == self.date_modified

        # Test __str__ and __repr__ return strings.
        assert isinstance(node.__str__(), str)
        assert isinstance(node.__repr__(), str)

    def test_create_minimum(self, user):
        """ Test user can create Node with text only or media only. """

        fields_text = {"user": user, "text": self.text}
        node_text = Node.objects.create(fields_text)

        assert node_text.text == self.text
        assert node_text.user == user

        fields_media = {"user": user, "media": self.media}
        node_media = Node.objects.create(fields_media)

        assert node_media.media == self.media
        assert node_media.user == user

        """
        # FIXME Either text or media must be set, both cannot be empty...
        fields_invalid = {"user": user}
        with pytest.raises(IntegrityError):
            Node.objects.create(fields_invalid)
        """

    def test_missing_user(self):
        """ Test Node always has a user. """

        fields_invalid = {"text": self.text}

        with pytest.raises(IntegrityError):
            Node.objects.create(fields_invalid)
