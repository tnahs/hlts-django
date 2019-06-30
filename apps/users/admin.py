from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UserAdminBase

from .models import User


@admin.register(User)
class UserAdmin(UserAdminBase):
    """ https://docs.djangoproject.com/en/2.2/ref/contrib/admin/ """

    fieldsets = (
        (None, {"fields": ("email", "password", "first_name", "last_name")}),
        ("Preferences", {"fields": ("theme",)}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Misc", {"fields": ("last_login",)}),
    )

    add_fieldsets = ((None, {"fields": ("email", "password1", "password2")}),)

    ordering = ("email",)
    search_fields = ()
    list_filter = ()
    list_display = ("__str__", "is_active", "is_staff", "is_superuser", "last_login")
    readonly_fields = ("last_login",)
    filter_horizontal = ("groups", "user_permissions")
