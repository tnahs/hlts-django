from django import forms
from django.utils.text import slugify

from .models import Passage, Source, Author, Origin, Tag, Collection


class PassageForm(forms.ModelForm):

    class Meta:
        model = Passage
        exclude = ['uuid', 'created', 'modified', 'pinged']

    # body = forms.CharField(widget=forms.Textarea)
    # tags = forms.CharField(required=False)
    # collections = forms.CharField(required=False)
    # notes = forms.CharField(widget=forms.Textarea, required=False)
    # origin = forms.CharField(required=False)
    # is_starred = forms.BooleanField(required=False)
    # in_trash = forms.BooleanField(required=False)
    # is_refreshable = forms.BooleanField(required=False)

    # source = forms.CharField(required=False)
    # author = forms.CharField(required=False)
    # title = forms.CharField(required=False)
    # publication = forms.CharField(required=False)
    # chapter = forms.CharField(required=False)
    # date = forms.DateField(required=False)
    # website = forms.URLField(required=False)
    # notes = forms.CharField(widget=forms.Textarea, required=False)

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    #     instance = getattr(self, 'instance', None)

    #     if instance and instance.pk:

    #         self.initial['tags'] = ' '.join(
    #             [tag.name for tag in self.instance.tags.all()])
    #         self.initial['collections'] = ' '.join(
    #             [collection.name for collection in self.instance.collections.all()])
    #         self.initial['origin'] = self.instance.origin.name

    #         # Make the source read-only. This is later toggled with javascript.
    #         for field in ['source', 'author', 'title', 'publication', 'chapter',
    #                       'date', 'website', 'notes']:
    #             self.fields[field].widget.attrs['readonly'] = True

    #         # Manually attach the Source.
    #         self.initial['source'] = self.instance.source.name
    #         self.initial['author'] = self.instance.source.author.name
    #         self.initial['title'] = self.instance.source.title
    #         self.initial['publication'] = self.instance.source.publication
    #         self.initial['chapter'] = self.instance.source.chapter
    #         self.initial['date'] = self.instance.source.date
    #         self.initial['website'] = self.instance.source.website
    #         self.initial['notes'] = self.instance.source.notes

    # def clean(self):
    #     super().clean()

    #     # print(self.data)
    #     # form.data.get('field_name', None)

    #     source_data = {
    #         'name': self.cleaned_data.get('source'),
    #         'author': self.cleaned_data.get('author'),
    #         'title': self.cleaned_data.get('title'),
    #         'publication': self.cleaned_data.get('publication'),
    #         'chapter': self.cleaned_data.get('chapter'),
    #         'date': self.cleaned_data.get('date'),
    #         'website': self.cleaned_data.get('website'),
    #         'notes': self.cleaned_data.get('notes'),
    #     }

    #     # FIXME: This doesn't work. If any information from the source has
    #     # changed it doesn't save it. It will only check if theres a new source
    #     # or not. The DB model is bad. We need to have a way to have a source
    #     # and have it contain different types of data that all connect to the
    #     # same Source thats attached to the Passage.
    #     # FIXME: This also prevents us from having multiple "Unknown" sources.

    #     source_slug = slugify(source_data['name'])
    #     author_slug = slugify(source_data['author'])

    #     try:
    #         source = Source.objects.get(slug=source_slug)
    #     except Source.DoesNotExist:

    #         try:
    #             author = Author.objects.get(slug=author_slug)
    #         except Author.DoesNotExist:
    #             author = Author(name=source_data['author'])
    #             author.save()

    #         source_data['author'] = author

    #         source = Source(**source_data)
    #         source.save()

    #     self.instance.source = source

    # def clean_tags(self):
    #     # TODO: Move this method to the Passage model.

    #     tag_names = self.cleaned_data.get('tags').split(' ')

    #     if tag_names:

    #         tags = []

    #         for tag_name in tag_names:

    #             tag_slug = slugify(tag_name)

    #             try:
    #                 tag = Tag.objects.get(slug=tag_slug)
    #             except Tag.DoesNotExist:
    #                 tag = Tag(name=tag_name)
    #                 tag.save()

    #             tags.append(tag)

    #     return tags

    # def clean_collections(self):
    #     # TODO: Move this method to the Passage model.

    #     collection_names = self.cleaned_data.get('collections').split(' ')

    #     if collection_names:

    #         collections = []

    #         for collection_name in collection_names:

    #             collection_slug = slugify(collection_name)

    #             try:
    #                 collection = Collection.objects.get(slug=collection_slug)
    #             except Collection.DoesNotExist:
    #                 collection = Collection(name=collection_name)
    #                 collection.save()

    #             collections.append(collection)

    #     return collections

    # def clean_origin(self):
    #     # TODO: Move this method to the Passage model.

    #     origin_name = self.cleaned_data.get('origin')
    #     origin_slug = slugify(origin_name)

    #     try:
    #         origin = Origin.objects.get(slug=origin_slug)
    #     except Origin.DoesNotExist:
    #         origin = Origin(name=origin_name)
    #         origin.save()

    #     return origin


"""
class SourceForm(forms.ModelForm):
    class Meta:
        model = Source
        exclude = ['created', 'modified', 'pinged']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.initial['author'] = self.instance.author.name

    name = forms.CharField(required=False)
    author = forms.CharField(required=False)
    title = forms.CharField(required=False)
    publication = forms.CharField(required=False)
    chapter = forms.CharField(required=False)
    date = forms.DateField(required=False)
    website = forms.URLField(required=False)
    notes = forms.CharField(widget=forms.Textarea, required=False)
"""
