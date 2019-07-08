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

    name = "Source"
    individual0 = "Individual0"
    individual1 = "Individual1"
    individuals = [individual0, individual1]
    url = "http://www.source-url.com"
    date = "January 1, 2000"
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
        assert Individual.objects.get(name=self.individual0) in source.individuals.all()
        assert Individual.objects.get(name=self.individual1) in source.individuals.all()
        assert source.url == self.url
        assert source.date == self.date
        assert source.notes == self.notes

        # Test __str__ and __repr__ return strings.
        assert isinstance(source.__str__(), str)
        assert isinstance(source.__repr__(), str)

    def test_create_minimum(self, user):
        """ Test user can create Source with name or individuals only. """

        source = Source.objects.create(user, name=self.name)
        assert source.user == user
        assert source.name == self.name

        source = Source.objects.create(user, individuals=self.individuals)
        assert source.user == user
        assert source.individuals.count() == len(self.individuals)

    def test_create_missing_user(self):
        """ Test Source always has a user. """

        with pytest.raises(IntegrityError):
            Source.objects.create(user=None, name=self.name)

    def test_create_unique_to_user(self, user):
        pass

    def test_update(self, user):

        source = Source.objects.create(user, name=self.name)

        name = "Source Updated"
        individual0 = "Individual0 Updated"
        individual1 = "Individual1 Updated"
        individuals = [individual0, individual1]
        url = "http://www.source-url-updated.com"
        date = "February 1, 2000"
        notes = "Source notes updated."
        updated_fields = {
            "name": name,
            "individuals": individuals,
            "url": url,
            "date": date,
            "notes": notes,
        }

        updated = Source.objects.update(user, source, **updated_fields)

        assert updated.pk == source.pk
        assert updated.name == name
        assert updated.individuals.count() == len(individuals)
        assert Individual.objects.get(name=individual0) in source.individuals.all()
        assert Individual.objects.get(name=individual1) in source.individuals.all()
        assert updated.url == url
        assert updated.date == date
        assert updated.notes == notes

    def test_update_unique_to_user(self, user):
        pass


@pytest.mark.django_db
class TestIndividual:

    name = "Individual"
    first_name = "Individual-First"
    last_name = "Individual-Last"
    aka0 = "Individual-alt0"
    aka1 = "Individual-alt1"
    aka = [aka0, aka1]

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
        assert Individual.objects.get(name=self.aka0) in individual.aka.all()
        assert Individual.objects.get(name=self.aka1) in individual.aka.all()

        # Test __str__ and __repr__ return strings.
        assert isinstance(individual.__str__(), str)
        assert isinstance(individual.__repr__(), str)

    def test_create_minimum(self, user):
        """ Test user can create Individual with name only. """

        individual = Individual.objects.create(user, name=self.name)

        assert individual.user == user
        assert individual.name == self.name

    def test_create_missing_user(self):
        """ Test Individual always has a user. """

        with pytest.raises(IntegrityError):
            Individual.objects.create(user=None, name=self.name)

    def test_create_unique_to_user(self, user):
        """ Test creating Individuals cannot have the same name and user. """

        Individual.objects.create(user, name=self.name)

        with pytest.raises(IntegrityError):
            Individual.objects.create(user, name=self.name)

    def test_aka(self, user):
        """ Test aka list items are created and related to one another. """

        name_alt0 = "Individual-alt0"
        name_alt1 = "Individual-alt1"
        name_alt2 = "Individual-alt2"
        aka = [name_alt1, name_alt2]

        fields = {"name": name_alt0, "aka": aka}

        Individual.objects.create(user, **fields)

        individual_alt0 = Individual.objects.get(name=name_alt0)
        individual_alt1 = Individual.objects.get(name=name_alt1)
        individual_alt2 = Individual.objects.get(name=name_alt2)

        assert individual_alt0 in individual_alt1.aka.all()
        assert individual_alt0 in individual_alt2.aka.all()

        # FIXME This does not work yet.
        assert individual_alt1 in individual_alt0.aka.all()
        assert individual_alt1 in individual_alt2.aka.all()

        # FIXME This does not work yet.
        assert individual_alt2 in individual_alt0.aka.all()
        assert individual_alt2 in individual_alt1.aka.all()

    def test_update(self, user):

        individual = Individual.objects.create(user, name=self.name)

        name = "Individual Updated"
        first_name = "Individual-First Updated"
        last_name = "Individual-Last Updated"
        aka0 = "Individual-alt0 Updated"
        aka1 = "Individual-alt1 Updated"
        aka = [aka0, aka1]
        updated_fields = {
            "name": name,
            "first_name": first_name,
            "last_name": last_name,
            "aka": aka,
        }

        updated = Individual.objects.update(user, individual, **updated_fields)

        assert updated.pk == individual.pk
        assert updated.name == name
        assert updated.first_name == first_name
        assert updated.last_name == last_name
        assert updated.aka.count() == len(aka)
        assert Individual.objects.get(name=aka0) in updated.aka.all()
        assert Individual.objects.get(name=aka1) in updated.aka.all()

    def test_update_unique_to_user(self, user):
        """ Test updating Individuals cannot have the same name and user. """

        existing_name = "Individual Existing"
        Individual.objects.create(user, name=existing_name)

        individual = Individual.objects.create(user, name=self.name)

        with pytest.raises(IntegrityError):
            Individual.objects.update(user, individual, name=existing_name)


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

    def test_create_missing_user(self):
        """ Test Tag always has a user. """

        with pytest.raises(IntegrityError):
            Tag.objects.create(user=None, name=self.name)

    def test_create_unique_to_user(self, user):
        """ Test creating Tags cannot have the same name and user. """

        Tag.objects.create(user, name=self.name)

        with pytest.raises(IntegrityError):
            Tag.objects.create(user, name=self.name)

    def test_update(self, user):

        tag = Tag.objects.create(user, name=self.name)

        updated_name = "tag-updated"
        updated_fields = {"name": updated_name}

        updated = Tag.objects.update(user, tag, **updated_fields)

        assert tag.pk == updated.pk
        assert updated.name == updated_name

    def test_update_unique_to_user(self, user):
        """ Test updating Tags cannot have the same name and user. """

        existing_name = "tag-existing"
        Tag.objects.create(user, name=existing_name)

        tag = Tag.objects.create(user, name=self.name)

        with pytest.raises(IntegrityError):
            Tag.objects.update(user, tag, name=existing_name)


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

    def test_create_missing_user(self):
        """ Test Collection always has a user. """

        with pytest.raises(IntegrityError):
            Collection.objects.create(user=None, name=self.name)

    def test_create_unique_to_user(self, user):
        """ Test creating Collections cannot have the same name and user. """

        Collection.objects.create(user, name=self.name)

        with pytest.raises(IntegrityError):
            Collection.objects.create(user, name=self.name)

    def test_update(self, user):

        collection = Collection.objects.create(user, name=self.name)

        updated_name = "collection-updated"
        updated_color = "color-updated"
        updated_description = "Collection description updated."
        updated_fields = {
            "name": updated_name,
            "color": updated_color,
            "description": updated_description,
        }

        updated = Collection.objects.update(user, collection, **updated_fields)

        assert updated.pk == collection.pk
        assert updated.name == updated_name
        assert updated.color == updated_color
        assert updated.description == updated_description

    def test_update_unique_to_user(self, user):
        """ Test updating Tags cannot have the same name and user. """

        existing_name = "collection-existing"
        Collection.objects.create(user, name=existing_name)

        collection = Collection.objects.create(user, name=self.name)

        with pytest.raises(IntegrityError):
            Collection.objects.update(user, collection, name=existing_name)


@pytest.mark.django_db
class TestOrigin:

    name = "origin"

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

    def test_create_missing_user(self):
        """ Test Origin always has a user. """

        with pytest.raises(IntegrityError):
            Origin.objects.create(user=None, name=self.name)

    def test_create_unique_to_user(self, user):
        """ Test creating Origins cannot have the same name and user. """

        Origin.objects.create(user, name=self.name)

        with pytest.raises(IntegrityError):
            Origin.objects.create(user, name=self.name)

    def test_update(self, user):

        origin = Origin.objects.create(user, name=self.name)

        updated_name = "origin-updated"
        updated_fields = {"name": updated_name}

        updated = Origin.objects.update(user, origin, **updated_fields)

        assert updated.pk == origin.pk
        assert origin.name == updated_name

    def test_update_unique_to_user(self, user):
        """ Test updating Tags cannot have the same name and user. """

        existing_name = "origin-existing"
        Origin.objects.create(user, name=existing_name)

        origin = Origin.objects.create(user, name=self.name)

        with pytest.raises(IntegrityError):
            Origin.objects.update(user, origin, name=existing_name)


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

    def test_create_missing_user(self):
        """ Test Node always has a user. """

        with pytest.raises(IntegrityError):
            Node.objects.create(user=None, text=self.text)

    def test_update(self, user):
        pass

    def test_related(self, user):

        node_a = Node.objects.create(user, text=self.text)
        node_b = Node.objects.create(user, text=self.text)

        node_a.related.add(node_b)
        node_a.save()

        assert node_a in node_b.related.all()
        assert node_b in node_a.related.all()
