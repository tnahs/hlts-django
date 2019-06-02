from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="dashboard"),
    path("add", views.add, name="add"),
    path("view", views.view, name="view"),
    path("save/<str:uuid>", views.save, name="save"),
]