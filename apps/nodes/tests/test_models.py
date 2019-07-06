import pytest
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.utils import timezone

from ..models import Collection, Individual, Node, Origin, Source, Tag


@pytest.fixture
@pytest.mark.django_db
def user():
    email = "user@email.com"
    password = "password"
    return get_user_model().objects.create_user(email=email, password=password)


@pytest.mark.django_db
class TestSource:

    # TODO: Source might need a bit more testing. Revisit after testing serializers.

    name = "Test Source"
    individuals = ["Test Individual1", "Test Individual2"]
    url = "http://www.source-url.com"
    date = "January, 1, 2000"
    notes = "Source notes."

    def test_create(self, user):

        fields = {
            "name": self.name,
            "individuals": self.individuals,
            "url": self.url,
            "date": self.date,
            "notes": self.notes,
        }

        source = Source.objects.create(user, **fields)

        assert source.user == user
        assert source.name == self.name
        assert source.individuals.count() == len(self.individuals)
        assert source.url == self.url
        assert source.date == self.date
        assert source.notes == self.notes

    def test_create_minimum(self, user):
        """ Test user can create Source with name or individuals only. """

        source = Source.objects.create(user, name=self.name)
        assert source.user == user
        assert source.name == self.name

        source = Source.objects.create(user, individuals=self.individuals)
        assert source.user == user
        assert source.individuals.count() == len(self.individuals)

    def test_missing_user(self):
        """ Test Source always has a user. """

        with pytest.raises(IntegrityError):
            Source.objects.create(user=None, name=self.name)


@pytest.mark.django_db
class TestIndividual:

    name = "John Doe"
    first_name = "John"
    last_name = "Doe"
    aka = ["Johnathan Doe", "John J. Doe"]

    def test_create(self, user):

        fields = {
            "name": self.name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "aka": self.aka,
        }

        individual = Individual.objects.create(user, **fields)

        assert individual.user == user
        assert individual.name == self.name
        assert individual.first_name == self.first_name
        assert individual.last_name == self.last_name
        assert individual.aka.count() == len(self.aka)

        # Test __str__ and __repr__ return strings.
        assert isinstance(individual.__str__(), str)
        assert isinstance(individual.__repr__(), str)

    def test_create_minimum(self, user):
        """ Test user can create Individual with name only. """

        individual = Individual.objects.create(user, name=self.name)

        assert individual.user == user
        assert individual.name == self.name

    def test_create_unique_together(self, user):
        """ Test creating Individuals cannot have the same name and user. """

        Individual.objects.create(user, name=self.name)

        with pytest.raises(IntegrityError):
            Individual.objects.create(user, name=self.name)

    def test_update(self, user):

        updated_name = "Johnny Doe"

        individual = Individual.objects.create(user, name=self.name)
        Individual.objects.update(user, individual, name=updated_name)

        assert individual.name == updated_name

    def test_update_unique_together(self, user):
        """ Test updating Individuals cannot have the same name and user. """

        existing_name = "Johnny Doe"
        Individual.objects.create(user, name=existing_name)

        individual = Individual.objects.create(user, name=self.name)

        with pytest.raises(IntegrityError):
            Individual.objects.update(user, individual, name=existing_name)

    def test_missing_user(self):
        """ Test Individual always has a user. """

        with pytest.raises(IntegrityError):
            Individual.objects.create(user=None, name=self.name)


@pytest.mark.django_db
class TestTag:

    name = "tag"

    def test_create(self, user):

        fields = {"name": self.name}

        tag = Tag.objects.create(user, **fields)

        assert tag.user == user
        assert tag.name == self.name

        # Test __str__ and __repr__ return strings.
        assert isinstance(tag.__str__(), str)
        assert isinstance(tag.__repr__(), str)

    def test_create_minimum(self, user):
        """ Test user can create Tag with name only. """

        tag = Tag.objects.create(user, name=self.name)

        assert tag.user == user
        assert tag.name == self.name

    def test_create_unique_together(self, user):
        """ Test creating Tags cannot have the same name and user. """

        Tag.objects.create(user, name=self.name)

        with pytest.raises(IntegrityError):
            Tag.objects.create(user, name=self.name)

    def test_update(self, user):

        tag = Tag.objects.create(user, name=self.name)

        assert tag.user == user
        assert tag.name == self.name

    def test_update_unique_together(self, user):
        """ Test updating Tags cannot have the same name and user. """
        pass

    def test_missing_user(self):
        """ Test Tag always has a user. """

        with pytest.raises(IntegrityError):
            Tag.objects.create(user=None, name=self.name)


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

        collection = Collection.objects.create(user, **fields)

        assert collection.user == user
        assert collection.name == self.name
        assert collection.color == self.color
        assert collection.description == self.description

        # Test __str__ and __repr__ return strings.
        assert isinstance(collection.__str__(), str)
        assert isinstance(collection.__repr__(), str)

    def test_create_minimum(self, user):
        """ Test user can create Collection with name only. """

        collection = Collection.objects.create(user, name=self.name)

        assert collection.user == user
        assert collection.name == self.name

    def test_create_unique_together(self, user):
        """ Test creating Collections cannot have the same name and user. """

        Collection.objects.create(user, name=self.name)

        with pytest.raises(IntegrityError):
            Collection.objects.create(user, name=self.name)

    def test_update(self, user):
        pass

    def test_update_unique_together(self, user):
        """ Test updating Collections cannot have the same name and user. """
        pass

    def test_missing_user(self):
        """ Test Collection always has a user. """

        with pytest.raises(IntegrityError):
            Collection.objects.create(user=None, name=self.name)


@pytest.mark.django_db
class TestOrigin:

    name = "app"

    def test_create(self, user):

        fields = {"name": self.name}

        origin = Origin.objects.create(user, **fields)

        assert origin.user == user
        assert origin.name == self.name

        # Test __str__ and __repr__ return strings.
        assert isinstance(origin.__str__(), str)
        assert isinstance(origin.__repr__(), str)

    def test_create_minimum(self, user):
        """ Test user can create Origin with name only. """

        origin = Origin.objects.create(user, name=self.name)

        assert origin.user == user
        assert origin.name == self.name

    def test_create_unique_together(self, user):
        """ Test creating Origins cannot have the same name and user. """

        Origin.objects.create(user, name=self.name)

        with pytest.raises(IntegrityError):
            Origin.objects.create(user, name=self.name)

    def test_update(self, user):
        pass

    def test_update_unique_together(self, user):
        """ Test updating Origins cannot have the same name and user. """
        pass

    def test_missing_user(self):
        """ Test Origin always has a user. """

        with pytest.raises(IntegrityError):
            Origin.objects.create(user=None, name=self.name)


@pytest.mark.django_db
class TestNode:

    id = "538b847e-9c14-11e9-a2a3-2a2ae2dbcce4"
    text = "Node text."
    media = "/path/to/media.png"
    link = "http://node-link.com"
    source_name = "Test Source"
    source_individuals = ["Test Individual1", "Test Individual2"]
    source_url = "http://www.source-url.com"
    source_date = "January, 1, 2000"
    source_notes = "Source notes."
    notes = "Node notes."
    tags = {"tag1", "tag2", "tag3"}
    collections = {"collection1", "collection2", "collection3"}
    origin = "app"
    in_trash = False
    is_starred = False
    date_created = timezone.now().isoformat()
    date_modified = timezone.now().isoformat()

    def test_create(self, user):
        """ Test full creation of a Node. """

        fields = {
            "id": self.id,
            "text": self.text,
            "media": self.media,
            "link": self.link,
            "source": {
                "name": self.source_name,
                "individuals": self.source_individuals,
                "url": self.source_url,
                "date": self.source_date,
                "notes": self.source_notes,
            },
            "notes": self.notes,
            "tags": self.tags,
            "collections": self.collections,
            "origin": self.origin,
            "in_trash": self.in_trash,
            "is_starred": self.is_starred,
            "date_created": self.date_created,
            "date_modified": self.date_modified,
        }

        node = Node.objects.create(user, **fields)

        assert node.user == user
        assert node.id == self.id
        assert node.text == self.text
        assert node.media == self.media
        assert node.link == self.link
        assert node.source.name == self.source_name
        assert node.source.individuals.count() == len(self.source_individuals)
        assert node.notes == self.notes
        assert node.tags.count() == len(self.tags)
        assert node.collections.count() == len(self.collections)
        assert node.origin.name == self.origin
        assert node.in_trash == self.in_trash
        assert node.is_starred == self.is_starred
        assert node.date_created == self.date_created

        # Test __str__ and __repr__ return strings.
        assert isinstance(node.__str__(), str)
        assert isinstance(node.__repr__(), str)

    def test_create_minimum(self, user):
        """ Test user can create Node with only text, media or link. """

        node_text = Node.objects.create(user, text=self.text)
        assert node_text.text == self.text
        assert node_text.user == user

        node_media = Node.objects.create(user, media=self.media)
        assert node_media.media == self.media
        assert node_media.user == user

        node_media = Node.objects.create(user, link=self.link)
        assert node_media.link == self.link
        assert node_media.user == user

    def test_update(self, user):
        pass

    def test_related(self, user):

        node_a = Node.objects.create(user, text=self.text)
        node_b = Node.objects.create(user, text=self.text)

        node_a.related.add(node_b)
        node_a.save()

        assert node_a.related.count() == 1
        assert node_a.related.first() == node_b
        assert node_b.related.count() == 1
        assert node_b.related.first() == node_a

    def test_missing_user(self):
        """ Test Node always has a user. """

        fields = {"text": self.text}

        with pytest.raises(IntegrityError):
            Node.objects.create(user=None, **fields)
