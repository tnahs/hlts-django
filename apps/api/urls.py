from django.urls import include, path

from rest_framework import routers

from apps.api import views


router = routers.DefaultRouter(trailing_slash=False)

# TODO: read about 'basename' not sure what it is...
# TODO: read about routers... not sure how they work...

router.register("nodes", views.UserNodesViewSet, basename="nodes")
router.register("nodes-text", views.TextViewSet, basename="nodes-text")
router.register("nodes-image", views.ImageViewSet, basename="nodes-image")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("rest_framework.urls", namespace="rest_framework"))
]
