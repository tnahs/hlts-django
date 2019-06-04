from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import Origin, Medium, Author, Source, Tag, Collection, Passage


class ModelAdminSaveMixin:

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        super().save_model(request, obj, form, change)


@admin.register(Origin)
class AdminOrigin(ModelAdminSaveMixin, admin.ModelAdmin):

    readonly_fields = ["owner", ]
    search_fields = ["name", ]


@admin.register(Medium)
class AdminMedium(ModelAdminSaveMixin, admin.ModelAdmin):

    readonly_fields = ["owner", ]
    search_fields = ["name", ]


@admin.register(Author)
class AdminAuthor(ModelAdminSaveMixin, admin.ModelAdmin):

    readonly_fields = ["owner", ]
    filter_horizontal = ["aka", ]
    search_fields = ["name", ]


class AdminSourceForm(forms.ModelForm):

    def clean_authors(self):

        pk = self.instance.pk
        name = self.cleaned_data.get("name")
        authors = self.cleaned_data.get("authors")

        try:
            Source.validate_authors(pk, name, authors)
        except ValidationError:
            raise

        return authors


@admin.register(Source)
class AdminSource(ModelAdminSaveMixin, admin.ModelAdmin):

    form = AdminSourceForm

    readonly_fields = ["owner", ]
    autocomplete_fields = ["medium", ]
    filter_horizontal = ["authors", ]
    search_fields = ["name", ]


@admin.register(Tag)
class AdminTag(ModelAdminSaveMixin, admin.ModelAdmin):

    readonly_fields = ["owner", ]


@admin.register(Collection)
class AdminCollection(ModelAdminSaveMixin, admin.ModelAdmin):

    readonly_fields = ["owner", ]


@admin.register(Passage)
class AdminPassage(ModelAdminSaveMixin, admin.ModelAdmin):

    list_display = ["__str__", "source"]
    readonly_fields = ["owner", "uuid", "topics", "created", "modified", "pinged", ]
    filter_horizontal = ["tags", "collections"]
    autocomplete_fields = ["source", "origin"]
    fieldsets = [
        [
            "Passage", {
                "fields": ["body", "notes", "source", "tags", "collections",
                           "topics"]
            }
        ],
        [
            "Metadata", {
                "fields": ["owner", "uuid", "origin", "is_starred",
                           "is_refreshable", "in_trash", "created", "modified",
                           "pinged"],
            }
        ]
    ]
