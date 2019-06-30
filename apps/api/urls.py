from django.urls import include, path, re_path

from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token

from . import views


class SimpleRouter(routers.SimpleRouter):
    """ Re-configured for optional trailing slashes.

    TODO: This still seems to add oddly on a DELETE request.
    """

    def __init__(self):
        self.trailing_slash = "/?"
        super().__init__()


router = SimpleRouter()
router.register("nodes", views.NodesViewSet, basename="node")
router.register("sources", views.SourcesViewSet, basename="source")
router.register("individuals", views.IndividualsViewSet, basename="individual")
router.register("tags", views.TagsViewSet, basename="tag")
router.register("collections", views.CollectionsViewSet, basename="collection")
router.register("origins", views.OriginsViewSet, basename="origin")


urlpatterns = [
    path("", views.ApiRoot.as_view()),
    path("", include(router.urls)),
    path("auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("auth/token/", obtain_jwt_token),
    re_path(
        r"^merge/(?P<basename>source|tag|collection|origin)/$",
        views.MergeView.as_view(),
        name="merge",
    ),
    re_path(r"^.*/$", views.NotFound.as_view()),
]
