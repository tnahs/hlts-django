from django.urls import include, path

from rest_framework import routers

from apps.api import views


router = routers.DefaultRouter()
router.register("nodes", views.NodesViewSet, basename="node")
router.register("sources", views.SourcesViewSet, basename="source")
router.register("individuals", views.IndividualsViewSet, basename="individual")
router.register("tags", views.TagsViewSet, basename="tag")
router.register("collections", views.CollectionsViewSet, basename="collection")
router.register("origins", views.OriginsViewSet, basename="origin")


urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("rest_framework.urls", namespace="rest_framework")),
]
