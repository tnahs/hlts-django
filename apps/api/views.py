from rest_framework import status, validators, viewsets
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from ..nodes.models import Collection, Individual, Node, Origin, Source, Tag
from ..nodes.serializers import (
    CollectionSerializer,
    IndividualSerializer,
    MergeSerializer,
    NodeSerializer,
    OriginSerializer,
    SourceSerializer,
    TagSerializer,
)


class NotFound(APIView):
    def http_404_not_found(self):
        return Response(
            {"status": status.HTTP_404_NOT_FOUND, "detail": "Not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    def get(self, request):
        return self.http_404_not_found()

    def post(self, request):
        return self.http_404_not_found()

    def put(self, request):
        return self.http_404_not_found()

    def patch(self, request):
        return self.http_404_not_found()

    def delete(self, request):
        return self.http_404_not_found()


class ApiRoot(APIView):
    """
    API Documentation...
    """

    def get(self, request):

        # Nodes
        nodes = reverse("node-list", request=request)

        # Node Data
        sources = reverse("source-list", request=request)
        individuals = reverse("individual-list", request=request)
        tags = reverse("tag-list", request=request)
        collections = reverse("collection-list", request=request)
        origins = reverse("origin-list", request=request)

        # Actions

        # Merge
        merge_sources = reverse("merge", args=["source"], request=request)
        merge_tags = reverse("merge", args=["tag"], request=request)
        merge_collections = reverse("merge", args=["collection"], request=request)
        merge_origins = reverse("merge", args=["origin"], request=request)

        return Response(
            {
                "data": {
                    "nodes": nodes,
                    "attributes": {
                        "sources": sources,
                        "individuals": individuals,
                        "tags": tags,
                        "collections": collections,
                        "origins": origins,
                    },
                },
                "actions": {
                    "merge": {
                        "sources": merge_sources,
                        "tags": merge_tags,
                        "collections": merge_collections,
                        "origins": merge_origins,
                    }
                },
            }
        )


class MergeView(APIView):
    """
    Merge Documentation...
    """

    serializer_class = MergeSerializer

    def get_queryset(self, basename):
        if basename == "source":
            return Source.objects.all()
        elif basename == "tag":
            return Tag.objects.all()
        elif basename == "collection":
            return Collection.objects.all()
        elif basename == "origin":
            return Origin.objects.all()

    def get(self, request, basename):
        queryset = self.get_queryset(basename).filter(user=request.user)
        serialized = self.serializer_class(
            queryset, many=True, context={"request": request, "basename": basename}
        )
        return Response({basename: serialized.data})

    def post(self, request, which):
        """ 90% of this logic will be moved to the MergeSerializer.
        TODO: Process data here.
        TODO: Warn that all data in src items will be lost.
        {
            "dest": {
                "name": "mauris"
            },
            "src": {
                "names": [
                    "posuere",
                    "maecenas"
                ]
            }
        }
        """
        user = request.user
        queryset = getattr(user, which)
        model = queryset.model

        dest = request.data.get("dest")
        dest_names = dest.get("name")

        if not dest_names:
            raise validators.ValidationError(
                f"Destination {which.capitalize()} name cannot be blank."
            )

        try:
            destination_obj = queryset.get(name=dest_names)
        except model.DoesNotExist:
            raise validators.ValidationError(
                f"Destination {which.capitalize()} '{dest_names}' does not exist."
            )

        src = request.data.get("src")
        src_names = src.get("names")

        if not src_names:
            raise validators.ValidationError(
                f"Source {which.capitalize()} names cannot be blank."
            )

        src_objs = []
        for src_name in src_names:
            try:
                src_obj = queryset.get(name=src_name)
            except model.DoesNotExist:
                raise validators.ValidationError(
                    f"Source {which.capitalize()} '{src_name}' does not exist."
                )
            src_objs.append(src_obj)

        dest_serialized = self.serializer_class(
            destination_obj, context={"request": request, "which": which}
        )

        srcs_serialized = self.serializer_class(
            src_objs, many=True, context={"request": request, "which": which}
        )

        return Response(
            {
                "dest": {"obj": dest_serialized.data},
                "src": {"objs": srcs_serialized.data},
            }
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
