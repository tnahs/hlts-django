from django.urls import include, path

from rest_framework import routers

from apps.api import views


router = routers.DefaultRouter()
router.register(r"texts", views.TextViewSet)
router.register(r"links", views.LinkViewSet)
router.register(r"images", views.ImageViewSet)
router.register(r"audios", views.AudioViewSet)
router.register(r"videos", views.VideoViewSet)
router.register(r"documents", views.DocumentViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include('rest_framework.urls', namespace='rest_framework'))
]
