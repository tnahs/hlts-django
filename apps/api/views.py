from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from ..nodes import models, serializers


@api_view(["GET"])
def api_root(request, format=None):
    return Response({
        "tags": reverse("tag-list", request=request, format=format),
    })


class TagListCreateView(generics.ListCreateAPIView):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer

    def get_queryset(self):
        return self.queryset \
            .filter(user=self.request.user) \
            .order_by("date_created")


class TagRetrieveUpdateDestroyViews(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer

    def get_queryset(self):
        return self.queryset \
            .filter(user=self.request.user) \
            .order_by("date_created")
