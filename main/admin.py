from django.contrib import admin

from .models import Origin, Medium, Author, Source, Tag, Collection, Topic, Passage


@admin.register(Origin)
class AdminOrigin(admin.ModelAdmin):

    search_fields = ["name", ]


@admin.register(Medium)
class AdminMedium(admin.ModelAdmin):

    search_fields = ["name", ]


@admin.register(Author)
class AdminAuthor(admin.ModelAdmin):

    filter_horizontal = ["aka"]
    search_fields = ["name", ]


@admin.register(Source)
class AdminSource(admin.ModelAdmin):

    autocomplete_fields = ["medium", ]
    filter_horizontal = ["authors", ]
    search_fields = ["name", ]


@admin.register(Tag)
class AdminTag(admin.ModelAdmin):
    pass


@admin.register(Collection)
class AdminCollection(admin.ModelAdmin):
    pass


@admin.register(Topic)
class AdminTopic(admin.ModelAdmin):
    pass

@admin.register(Passage)
class AdminPassage(admin.ModelAdmin):

    list_display = ["__str__", "source"]
    readonly_fields = ["uuid", "topics", "created", "modified", "pinged", ]
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
                "fields": ["uuid", "origin", "is_starred", "is_refreshable",
                           "in_trash", "created", "modified", "pinged"],
            }
        ]
    ]
