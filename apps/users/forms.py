from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import AppUser


class AppUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = AppUser
        fields = "__all__"
        # fields = UserCreationForm.Meta.fields + ("custom_fields",)


class AppUserChangeForm(UserChangeForm):

    class Meta:
        model = AppUser
        fields = "__all__"
