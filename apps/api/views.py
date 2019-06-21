from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from ..nodes import models, serializers


@api_view(["GET"])
def api_root(request, format=None):

    nodes_url = reverse("nodes-list", request=request, format=format)
    tags_url = reverse("tags-list", request=request, format=format)
    collections_url = reverse("collections-list", request=request, format=format)

    urls = {
        "nodes": nodes_url,
        "tags": tags_url,
        "collections": collections_url,
    }

    return Response(urls)


# Tags


class TagsViewMixin:
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class TagsListView(TagsViewMixin, generics.ListCreateAPIView):
    pass


class TagsDetailView(TagsViewMixin, generics.RetrieveUpdateDestroyAPIView):
    pass


# Collections


class CollectionsViewMixin:
    queryset = models.Collection.objects.all()
    serializer_class = serializers.CollectionSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class CollectionsListView(CollectionsViewMixin, generics.ListCreateAPIView):
    pass


class CollectionsDetailView(CollectionsViewMixin, generics.RetrieveUpdateDestroyAPIView):
    pass


# Nodes


class NodesViewMixin:
    queryset = models.Node.objects.all()
    serializer_class = serializers.NodeSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class NodesListView(NodesViewMixin, generics.ListCreateAPIView):
    pass


class NodesDetailView(NodesViewMixin, generics.RetrieveUpdateDestroyAPIView):
    pass
