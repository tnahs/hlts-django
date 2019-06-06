from django import forms

from .models import Passage


class PassageForm(forms.ModelForm):

    class Meta:
        model = Passage
        exclude = ["uuid", "created", "modified", "pinged"]
