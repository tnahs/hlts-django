from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Notification, Task
from .forms import UserCreationFormExtended, UserChangeFormExtended


@admin.register(User)
class UserAdminExtended(UserAdmin):

    model = User
    form = UserChangeFormExtended
    add_form = UserCreationFormExtended

    list_display = ("username", "email")
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("theme",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Permissions", {"fields": ("is_staff", "is_active")}),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    pass


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass
