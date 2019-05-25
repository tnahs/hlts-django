from django import forms
from .models import Source, Author, Origin, Tag, Collection, Passage

"""
class PassageForm(forms.ModelForm):

    class Meta:
        model = Passage
        fields = ('uuid', 'body', 'tags', 'collections', 'notes', 'origin',
                  'is_starred', 'is_api_refreshable', 'in_trash', 'source', )
"""

class PassageForm(forms.Form):

    uuid = forms.UUIDField()
    body = forms.CharField(widget=forms.Textarea)
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all())
    collections = forms.ModelMultipleChoiceField(queryset=Collection.objects.all())
    notes  = forms.CharField(widget=forms.Textarea)
    created = forms.DateTimeField()
    modified = forms.DateTimeField()
    origin = forms.ModelChoiceField(queryset=Origin.objects.all())
    is_starred = forms.BooleanField()
    is_api_refreshable = forms.BooleanField()
    in_trash = forms.BooleanField()
    source = forms.ModelChoiceField(queryset=Source.objects.all())