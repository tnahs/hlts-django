from django.urls import include, path

from rest_framework.urlpatterns import format_suffix_patterns

from apps.api import views


urlpatterns = [
    path("", views.api_root),
    path("auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("nodes/tags/",
        views.TagListCreateView.as_view(), name="tag-list"),
    path("nodes/tags/<int:pk>",
        views.TagRetrieveUpdateDestroyViews.as_view(), name="tag-detail"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
