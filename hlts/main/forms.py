from django.forms import ModelForm
from .models import Passage

class PassageForm(ModelForm):
    class Meta:
        model = Passage
        fields = ('body', 'notes', 'tags', 'modified', 'origin', 'in_trash',
                  'is_starred', 'is_refreshable', 'source', )