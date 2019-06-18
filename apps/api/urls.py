from django.urls import include, path

from rest_framework import routers

from apps.api import views


router = routers.DefaultRouter(trailing_slash=False)

# TODO: read about routers... not sure how they work...

router.register("nodes", views.NodesViewSet)
router.register("texts", views.NodeTextViewSet)
router.register("images", views.NodeImageViewSet)

router.register("tags", views.TagViewSet)
router.register("collections", views.CollectionViewSet)
router.register("sources", views.SourceViewSet)
router.register("individuals", views.IndividualViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("rest_framework.urls", namespace="rest_framework"))
]
