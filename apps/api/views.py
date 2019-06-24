from rest_framework import viewsets

from ..nodes import models, serializers


class QuerysetMixin:
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class SourcesViewSet(QuerysetMixin, viewsets.ModelViewSet):
    queryset = models.Source.objects.all()
    serializer_class = serializers.SourceSerializer


class IndividualsViewSet(QuerysetMixin, viewsets.ModelViewSet):
    queryset = models.Individual.objects.all()
    serializer_class = serializers.IndividualSerializer


class TagsViewSet(QuerysetMixin, viewsets.ModelViewSet):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer


class CollectionsViewSet(QuerysetMixin, viewsets.ModelViewSet):
    queryset = models.Collection.objects.all()
    serializer_class = serializers.CollectionSerializer


class OriginsViewSet(QuerysetMixin, viewsets.ModelViewSet):
    queryset = models.Origin.objects.all()
    serializer_class = serializers.OriginSerializer


class NodesViewSet(QuerysetMixin, viewsets.ModelViewSet):
    queryset = models.Node.objects.all()
    serializer_class = serializers.NodeSerializer
