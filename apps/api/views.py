from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from ..nodes import models, serializers


@api_view(["GET"])
def api_root(request, format=None):

    nodes_url = reverse("nodes-list", request=request, format=format)
    sources_url = reverse("sources-list", request=request, format=format)
    individuals_url = reverse("individuals-list", request=request, format=format)
    tags_url = reverse("tags-list", request=request, format=format)
    collections_url = reverse("collections-list", request=request, format=format)
    origins_url = reverse("origins-list", request=request, format=format)

    urls = {
        "nodes": nodes_url,
        "attributes": {
            "sources": sources_url,
            "individuals": individuals_url,
            "tags": tags_url,
            "collections": collections_url,
            "origins": origins_url,
        },
    }

    return Response(urls)


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
