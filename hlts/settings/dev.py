from .base import *


DEBUG = True

# INSTALLED_APPS += [
#     "debug_toolbar",
# ]

# MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware', ]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(SITE_ROOT / "db.sqlite3"),
    }
}