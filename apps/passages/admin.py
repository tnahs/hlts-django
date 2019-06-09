from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError

from .models import Origin, Medium, Author, Source, Tag, Collection, Passage


admin.site.unregister(Group)


class ModelAdminSaveMixin:
    """ Mixin to append the 'owner' to object. """

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        super().save_model(request, obj, form, change)


@admin.register(Origin)
class OriginAdmin(ModelAdminSaveMixin, admin.ModelAdmin):

    readonly_fields = ["owner", ]
    search_fields = ["name", ]


@admin.register(Medium)
class MediumAdmin(ModelAdminSaveMixin, admin.ModelAdmin):

    readonly_fields = ["owner", ]
    search_fields = ["name", ]


@admin.register(Author)
class AuthorAdmin(ModelAdminSaveMixin, admin.ModelAdmin):

    readonly_fields = ["owner", ]
    filter_horizontal = ["aka", ]
    search_fields = ["name", ]


class SourceAdminForm(forms.ModelForm):

    def clean_authors(self):

        source_pk = self.instance.pk
        source_name = self.cleaned_data.get("name")
        source_authors = self.cleaned_data.get("authors")

        try:
            Source.validate_authors(source_pk, source_name, source_authors)
        except ValidationError:
            raise

        return source_authors


@admin.register(Source)
class SourceAdmin(ModelAdminSaveMixin, admin.ModelAdmin):

    form = SourceAdminForm

    readonly_fields = ["owner", ]
    autocomplete_fields = ["medium", ]
    filter_horizontal = ["authors", ]
    search_fields = ["name", ]


@admin.register(Tag)
class TagAdmin(ModelAdminSaveMixin, admin.ModelAdmin):

    readonly_fields = ["owner", ]


@admin.register(Collection)
class CollectionAdmin(ModelAdminSaveMixin, admin.ModelAdmin):

    readonly_fields = ["owner", ]


@admin.register(Passage)
class PassageAdmin(ModelAdminSaveMixin, admin.ModelAdmin):

    list_display = ["__str__", "_source", "_tags", "_collections", "is_starred"]
    filter_horizontal = ["tags", "collections"]
    autocomplete_fields = ["source", "origin"]
    readonly_fields = [
        "owner", "uuid", "date_created", "date_modified", "topics", "related",
        "count_read", "count_query",
    ]
    fieldsets = [
        [
            None, {
                "fields": [
                    "uuid", "body", "notes", "source", "tags", "collections",
                    "origin", "is_starred", "in_trash", "is_refreshable",
                ],
            },
        ],
        [
            "Read-only", {
                "fields": [
                    "owner", "date_created", "date_modified", "topics",
                    "related", "count_read", "count_query",
                ],
            },
        ],
    ]

    def _source(self, obj):
        authors = ", ".join([author.name for author in obj.source.authors.all()])
        return f"{obj.source.name} - {authors}"

    def _tags(self, obj):
        return ", ".join([child.name for child in obj.tags.all()])

    def _collections(self, obj):
        return ", ".join([child.name for child in obj.collections.all()])