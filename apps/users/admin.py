from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import AppUser, Notification, Task
from .forms import AppUserCreationForm, AppUserChangeForm


@admin.register(AppUser)
class AppUserAdmin(UserAdmin):

    model = AppUser
    add_form = AppUserCreationForm
    form = AppUserChangeForm

    list_display = ["username", "email"]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    pass


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass
