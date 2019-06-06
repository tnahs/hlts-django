from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User
from .forms import MainUserCreationForm, MainUserChangeForm


@admin.register(User)
class MainUserAdmin(UserAdmin):

    model = User
    add_form = MainUserCreationForm
    form = MainUserChangeForm

    list_display = ["username", "email"]