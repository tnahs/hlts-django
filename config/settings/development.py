from .base import *

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(SITE_ROOT / "tmp" / "db.sqlite3"),
    }
}
