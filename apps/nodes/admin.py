from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError

from .models import Origin, Individual, Source, Tag, Collection, Node


admin.site.unregister(Group)


class ModelAdminUserMixin:
    """ Mixin to append the 'user' to object. """

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)

    def get_form(self, request, *args, **kwargs):
        form = super().get_form(request, *args, **kwargs)
        form.user = request.user
        return form


@admin.register(Origin)
class OriginAdmin(ModelAdminUserMixin, admin.ModelAdmin):

    readonly_fields = ("user", )
    search_fields = ("name", )


@admin.register(Individual)
class IndividualAdmin(ModelAdminUserMixin, admin.ModelAdmin):

    # FIXME: Admin page doesnt handle unique-together validation when "user"
    # is a read-only field. Need to find a way to hide this field but also
    # run the unique-together validation method. This also applies to any other
    # fields with the same basic configuration.

    readonly_fields = ("user", )
    filter_horizontal = ("aka", )
    search_fields = ("name", )


class SourceAdminForm(forms.ModelForm):

    def clean(self):
        """ See Source model in nodes.models for notes. """

        pk = self.instance.pk
        name = self.cleaned_data.get("name")
        individuals = self.cleaned_data.get("individuals")

        if not name and not individuals:
            error = forms.ValidationError(
                "Either 'name' or 'individuals' must be defined."
            )
            self.add_error("name", error)
            self.add_error("individuals", error)

        try:
            Source.validate_unique_together(
                self.user, name, individuals, source_pk=pk
            )
        except ValidationError as error:
            raise forms.ValidationError(error.message)

        return self.cleaned_data


@admin.register(Source)
class SourceAdmin(ModelAdminUserMixin, admin.ModelAdmin):

    form = SourceAdminForm

    readonly_fields = ("user", )
    filter_horizontal = ("individuals", )
    search_fields = ("name", )


@admin.register(Tag)
class TagAdmin(ModelAdminUserMixin, admin.ModelAdmin):

    readonly_fields = ("user", )


@admin.register(Collection)
class CollectionAdmin(ModelAdminUserMixin, admin.ModelAdmin):

    readonly_fields = ("user", )


@admin.register(Node)
class NodeAdmin(ModelAdminUserMixin, admin.ModelAdmin):

    list_display = ("__str__", "source", "_tags", "_collections", "is_starred")
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
                    "uuid", "body", "file", "source", "notes", "tags",
                    "collections", "origin", "is_starred", "in_trash",
                    "related"
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

    def _tags(self, obj):
        return ", ".join([t.name for t in obj.tags.all()])

    def _collections(self, obj):
        return ", ".join([c.name for c in obj.collections.all()])
