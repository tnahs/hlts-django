from django.contrib.auth import get_user_model

from rest_framework import viewsets, generics

from ..nodes import models, serializers


class BaseNodeAttributesViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        return self.queryset \
            .filter(user=self.request.user) \
            .order_by("name")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TagDetailViewSet(BaseNodeAttributesViewSet):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagDetailSerializer


class CollectionDetailViewSet(BaseNodeAttributesViewSet):
    queryset = models.Collection.objects.all()
    serializer_class = serializers.CollectionDetailSerializer


class IndividualDetailViewSet(BaseNodeAttributesViewSet):
    queryset = models.Individual.objects.all()
    serializer_class = serializers.IndividualDetailSerializer


class SourceDetailViewSet(BaseNodeAttributesViewSet):
    queryset = models.Source.objects.all()
    serializer_class = serializers.SourceDetailSerializer


#


class BaseNodeViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        return self.queryset \
            .filter(user=self.request.user) \
            .order_by("date_created")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NodeTextViewSet(BaseNodeViewSet):

    queryset = models.Text.objects.all()
    serializer_class = serializers.NodeTextSerializer


class NodeImageViewSet(BaseNodeViewSet):

    queryset = models.Image.objects.all()
    serializer_class = serializers.NodeImageSerializer


#


class NodesViewSet(viewsets.ModelViewSet):

    queryset = get_user_model().objects.all()
    serializer_class = serializers.NodesSerializer

    def get_queryset(self):
        return self.queryset.filter(pk=self.request.user.pk)
