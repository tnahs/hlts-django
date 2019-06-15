from django.contrib.auth import get_user_model

from rest_framework import viewsets, mixins

from ..nodes.models import Text, Image, Tag, Collection
from ..nodes.serializers import (NodesSerializer, TextSerializer,
    ImageSerializer, TagSerializer, CollectionSerializer)


class BaseNodeAttributesViewSet(viewsets.GenericViewSet,
                                mixins.ListModelMixin,
                                mixins.CreateModelMixin):

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by("name")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TagViewSet(BaseNodeAttributesViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class CollectionViewSet(BaseNodeAttributesViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer


#


class BaseNodeViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by("date_created")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TextViewSet(BaseNodeViewSet):

    queryset = Text.objects.all()
    serializer_class = TextSerializer


class ImageViewSet(BaseNodeViewSet):

    queryset = Image.objects.all()
    serializer_class = ImageSerializer


#


class NodesViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = get_user_model().objects.all()
    serializer_class = NodesSerializer

    def get_queryset(self):
        return self.queryset.filter(pk=self.request.user.pk)
