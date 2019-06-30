from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from . import models


@admin.register(models.Origin)
class OriginAdmin(admin.ModelAdmin):
    readonly_fields = ("date_created", "date_modified")
    search_fields = ("name",)


@admin.register(models.Individual)
class IndividualAdmin(admin.ModelAdmin):
    readonly_fields = ("date_created", "date_modified")
    filter_horizontal = ("aka",)
    search_fields = ("name",)


class SourceAdminForm(forms.ModelForm):
    def clean(self):
        """ See apps.nodes.models.Source """

        pk = self.instance.pk
        user = self.cleaned_data.get("user")
        name = self.cleaned_data.get("name")
        individuals = self.cleaned_data.get("individuals")

        if not name and not individuals:
            error = forms.ValidationError(
                "Either 'name' or 'individuals' must be defined."
            )
            self.add_error("name", error)
            self.add_error("individuals", error)

        try:
            models.Source.validate_unique_together(
                user, name, individuals, source_pk=pk
            )
        except ValidationError as error:
            raise forms.ValidationError(error.message)

        return self.cleaned_data


@admin.register(models.Source)
class SourceAdmin(admin.ModelAdmin):

    form = SourceAdminForm

    readonly_fields = ("date_created", "date_modified")
    filter_horizontal = ("individuals",)
    search_fields = ("name",)


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    readonly_fields = ("date_created", "date_modified")


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    readonly_fields = ("date_created", "date_modified")


@admin.register(models.Node)
class NodeAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Node",
            {
                "fields": (
                    "id",
                    "text",
                    "media",
                    "source",
                    "notes",
                    "tags",
                    "collections",
                    "origin",
                    "is_starred",
                    "in_trash",
                    "related",
                    "user",
                )
            },
        ),
        (
            "Read-only",
            {"fields": ("date_created", "date_modified", "auto_tags", "auto_related")},
        ),
    )

    list_display = ("__str__", "source", "_tags", "_collections", "is_starred")
    readonly_fields = ("date_created", "date_modified", "auto_tags", "auto_related")
    filter_horizontal = ("tags", "collections")
    autocomplete_fields = ("origin", "source")

    def _tags(self, obj):
        return ", ".join([str(t) for t in obj.tags.all()])

    def _collections(self, obj):
        return ", ".join([str(c) for c in obj.collections.all()])
