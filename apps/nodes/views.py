from rest_framework import views, viewsets, status
from rest_framework.response import Response

from .models import Collection, Individual, Node, Origin, Source, Tag
from .serializers import (
    CollectionSerializer,
    IndividualSerializer,
    MergeSerializer,
    NodeSerializer,
    OriginSerializer,
    SourceSerializer,
    TagSerializer,
)


class QuerysetMixin:
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        return serializer.save(user=self.request.user)


class SourcesViewSet(QuerysetMixin, viewsets.ModelViewSet):
    queryset = Source.objects.all()
    serializer_class = SourceSerializer


class IndividualsViewSet(QuerysetMixin, viewsets.ModelViewSet):
    queryset = Individual.objects.all()
    serializer_class = IndividualSerializer


class TagsViewSet(QuerysetMixin, viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class CollectionsViewSet(QuerysetMixin, viewsets.ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer


class OriginsViewSet(QuerysetMixin, viewsets.ModelViewSet):
    queryset = Origin.objects.all()
    serializer_class = OriginSerializer


class NodesViewSet(QuerysetMixin, viewsets.ModelViewSet):
    queryset = Node.objects.all()
    serializer_class = NodeSerializer


# Actions Views


class MergeView(views.APIView):
    """
    Merge Documentation...
    """

    serializer_class = MergeSerializer

    def post(self, request):
        """
        {
            "which": "tags",
            "into": "mauris",
            "merging": [
                "mauris",
                "posuere",
                "maecenas"
            ]
        }
        """

        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid(raise_exception=True):
            serializer.save()

        return Response(status=status.HTTP_200_OK)
