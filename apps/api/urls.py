from django.urls import include, path, re_path
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token

from ..nodes.views import (
    CollectionsViewSet,
    IndividualsViewSet,
    MergeView,
    NodesViewSet,
    OriginsViewSet,
    SourcesViewSet,
    TagsViewSet,
)
from ..users.views import UserView, UserPasswordChangeView
from .views import ApiRoot


router = routers.SimpleRouter(trailing_slash=False)
router.register("nodes", NodesViewSet, basename="node")
router.register("sources", SourcesViewSet, basename="source")
router.register("individuals", IndividualsViewSet, basename="individual")
router.register("tags", TagsViewSet, basename="tag")
router.register("collections", CollectionsViewSet, basename="collection")
router.register("origins", OriginsViewSet, basename="origin")


urlpatterns = [
    path("", ApiRoot.as_view()),
    path("", include(router.urls)),
    path("user/", UserView.as_view(), name="user"),
    path("user/password/", UserPasswordChangeView.as_view(), name="password"),
    path("auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("auth/token/", obtain_jwt_token),
    path("merge/", MergeView.as_view(), name="merge"),
]
