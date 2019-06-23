from django.urls import include, path

from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import routers

from apps.api import views


router = routers.SimpleRouter()
router.register("nodes", views.NodesViewSet, basename="nodes")
router.register("sources", views.SourcesViewSet, basename="sources")
router.register("individuals", views.IndividualsViewSet, basename="individuals")
router.register("tags", views.TagsViewSet, basename="tags")
router.register("collections", views.CollectionsViewSet, basename="collections")
router.register("origins", views.OriginsViewSet, basename="origins")


urlpatterns = [
    path("", views.api_root),
    path("", include(router.urls)),
    path("auth/", include("rest_framework.urls", namespace="rest_framework")),
]

urlpatterns = format_suffix_patterns(urlpatterns)
