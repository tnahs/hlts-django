from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import User


class MainUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = User
        fields = "__all__"
        # fields = UserCreationForm.Meta.fields + ("custom_field",)


class MainUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = "__all__"
