from django.contrib import admin

from .models import Source, Author, Origin, Tag, Collection, Passage


class AuthorAdmin(admin.ModelAdmin):
    list_populated = ('name', 'slug', )
    prepopulated_fields = {'slug': ('name', )}

admin.site.register(Author, AuthorAdmin)


class SourceAdmin(admin.ModelAdmin):
    list_populated = ('name', 'slug', 'author', )
    prepopulated_fields = {'slug': ('name', )}

admin.site.register(Source, SourceAdmin)


class OriginAdmin(admin.ModelAdmin):
    list_populated = ('name', 'slug', )
    prepopulated_fields = {'slug': ('name', )}

admin.site.register(Origin, OriginAdmin)


class TagAdmin(admin.ModelAdmin):
    list_populated = ('name', 'slug', )
    prepopulated_fields = {'slug': ('name', )}

admin.site.register(Tag, TagAdmin)


class CollectionAdmin(admin.ModelAdmin):
    list_populated = ('name', 'slug', )
    prepopulated_fields = {'slug': ('name', )}

admin.site.register(Collection, CollectionAdmin)


admin.site.register(Passage)