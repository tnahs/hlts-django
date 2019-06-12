from rest_framework import viewsets

from ..nodes.models import Text, Link, Image, Audio, Video, Document
from ..nodes.serializers import (TextSerializer, LinkSerializer,
    ImageSerializer, AudioSerializer, VideoSerializer, DocumentSerializer)


class TextViewSet(viewsets.ModelViewSet):

    queryset = Text.objects.all()
    serializer_class = TextSerializer


class LinkViewSet(viewsets.ModelViewSet):

    queryset = Link.objects.all()
    serializer_class = LinkSerializer


class ImageViewSet(viewsets.ModelViewSet):

    queryset = Image.objects.all()
    serializer_class = ImageSerializer


class AudioViewSet(viewsets.ModelViewSet):

    queryset = Audio.objects.all()
    serializer_class = AudioSerializer


class VideoViewSet(viewsets.ModelViewSet):

    queryset = Video.objects.all()
    serializer_class = VideoSerializer


class DocumentViewSet(viewsets.ModelViewSet):

    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
