from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import validators


from ..nodes import models, serializers


class MergeView(APIView):

    serializer_class = serializers.MergeSerializer

    def get(self, request, which):
        queryset = getattr(request.user, which).all()
        serialized = self.serializer_class(
            queryset, many=True, context={"request": request}
        )
        return Response({f"mergable {which}": serialized.data})

    def post(self, request, which):
        """ 90% of this logic will be moved to the MergeSerializer.
        TODO: Process data here.
        TODO: Warn that all data in src items will be lost and that only the.
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
            destination_obj, context={"request": request}
        )

        srcs_serialized = self.serializer_class(
            src_objs, many=True, context={"request": request}
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
