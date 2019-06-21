from django.urls import include, path

from rest_framework.urlpatterns import format_suffix_patterns

from apps.api import views


urlpatterns = [
    path("", views.api_root),
    path("auth/", include("rest_framework.urls", namespace="rest_framework")),

    path("nodes/", views.NodesListView.as_view(), name="nodes-list"),
    path("nodes/<int:pk>", views.NodesDetailView.as_view(), name="nodes-detail"),

    path("tags/", views.TagsListView.as_view(), name="tags-list"),
    path("tags/<int:pk>", views.TagsDetailView.as_view(), name="tags-detail"),

    path("collections/", views.CollectionsListView.as_view(), name="collections-list"),
    path("collections/<int:pk>", views.CollectionsDetailView.as_view(), name="collections-detail"),
]

urlpatterns = format_suffix_patterns(urlpatterns)