from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='dashboard'),
    path('view', views.view, name='view'),
    path('add', views.add, name='add'),
]