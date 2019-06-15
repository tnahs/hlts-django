from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import User


class UserCreationFormExtended(UserCreationForm):

    class Meta:
        model = User
        fields = "__all__"


class UserChangeFormExtended(UserChangeForm):

    class Meta:
        model = User
        fields = ("theme", )
