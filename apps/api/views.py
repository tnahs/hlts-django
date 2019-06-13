from rest_framework import viewsets

from ..users.models import AppUser
from ..users.serializers import UserNodesSerializer
from ..nodes.models import Text, Image
from ..nodes.serializers import TextSerializer, ImageSerializer


class UserNodesViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = UserNodesSerializer

    def get_queryset(self):
        return AppUser.objects.filter(pk=self.request.user.pk)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TextViewSet(viewsets.ModelViewSet):

    serializer_class = TextSerializer

    def get_queryset(self):
        return Text.objects.filter(owner=self.request.user.pk)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ImageViewSet(viewsets.ModelViewSet):

    serializer_class = ImageSerializer

    def get_queryset(self):
        return Image.objects.filter(owner=self.request.user.pk)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)