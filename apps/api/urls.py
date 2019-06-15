from django.urls import include, path

from rest_framework import routers

from apps.api import views


router = routers.DefaultRouter(trailing_slash=False)

# TODO: read about routers... not sure how they work...

router.register("nodes", views.NodesViewSet)
router.register("texts", views.TextViewSet)
router.register("images", views.ImageViewSet)
router.register("tags", views.TagViewSet)
router.register("collections", views.CollectionViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("rest_framework.urls", namespace="rest_framework"))
]
