from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError

from .models import (Origin, Individual, Source, Tag, Collection, Text, Image)


admin.site.unregister(Group)


class ModelAdminSaveMixin:
    """ Mixin to append the 'user' to object. """

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)


@admin.register(Origin)
class OriginAdmin(ModelAdminSaveMixin, admin.ModelAdmin):

    readonly_fields = ("user", )
    search_fields = ("name", )


@admin.register(Individual)
class IndividualAdmin(ModelAdminSaveMixin, admin.ModelAdmin):

    readonly_fields = ("user", )
    filter_horizontal = ("aka", )
    search_fields = ("name", )


class SourceAdminForm(forms.ModelForm):

    def clean_individuals(self):

        source_pk = self.instance.pk
        source_name = self.cleaned_data.get("name")
        source_individuals = self.cleaned_data.get("individuals")

        try:
            Source.validate_individuals(source_pk, source_name, source_individuals)
        except ValidationError:
            raise

        return source_individuals


@admin.register(Source)
class SourceAdmin(ModelAdminSaveMixin, admin.ModelAdmin):

    form = SourceAdminForm

    readonly_fields = ("user", )
    filter_horizontal = ("individuals", )
    search_fields = ("name", )


@admin.register(Tag)
class TagAdmin(ModelAdminSaveMixin, admin.ModelAdmin):

    readonly_fields = ("user", )


@admin.register(Collection)
class CollectionAdmin(ModelAdminSaveMixin, admin.ModelAdmin):

    readonly_fields = ("user", )


class NodeAdmin(ModelAdminSaveMixin, admin.ModelAdmin):

    list_display = ("__str__", "_source", "_tags", "_collections", "is_starred")
    filter_horizontal = ("tags", "collections")
    autocomplete_fields = ("origin", "source")
    readonly_fields = (
        "user", "date_created", "date_modified", "topics", "count_seen",
        "count_query"
    )
    fieldsets = (
        (
            "Node", {
                "fields": (
                    "source", "notes", "tags", "collections", "origin",
                    "is_starred", "in_trash"
                ),
            },
        ),
        (
            "Read-only", {
                "fields": (
                    "user", "date_created", "date_modified", "topics",
                    "count_seen", "count_query"
                ),
            },
        ),
    )

    def _source(self, obj):

        if not obj.source:
            return ""

        if not obj.source.individuals.count():
            return obj.source.name

        individuals = ", ".join([a.name for a in obj.source.individuals.all()])

        return f"{obj.source.name} - {individuals}"

    def _tags(self, obj):
        return ", ".join([t.name for t in obj.tags.all()])

    def _collections(self, obj):
        return ", ".join([c.name for c in obj.collections.all()])


@admin.register(Text)
class TextAdmin(NodeAdmin):

    readonly_fields = ("uuid", ) + NodeAdmin.readonly_fields
    fieldsets = (
        (
            "Text", {
                "fields": ("uuid", "body"),
            },
        ),
    ) + NodeAdmin.fieldsets


@admin.register(Image)
class ImageAdmin(NodeAdmin):

    fieldsets = (
        (
            "Image", {
                "fields": ("file", "name", "description"),
            },
        ),
    ) + NodeAdmin.fieldsets
