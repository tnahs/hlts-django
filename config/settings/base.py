
import os
import pathlib


SITE_ROOT = pathlib.Path(__file__).parent.parent.parent
SECRET_KEY = os.getenv("SECRET_KEY")

STATIC_ROOT = SITE_ROOT / "static"
STATIC_URL = "/static/"

MEDIA_ROOT = SITE_ROOT / "media"
MEDIA_URL = "/media/"

FIXTURE_DIRS = [
    SITE_ROOT / "fixtures",
]

WSGI_APPLICATION = "config.wsgi.application"
ROOT_URLCONF = "config.urls"

ALLOWED_HOSTS = ["*"]

AUTH_USER_MODEL = "users.User"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # local apps
    "apps.api.apps.ApiConfig",
    "apps.users.apps.UsersConfig",
    "apps.nodes.apps.NodesConfig",

    # installed apps
    "rest_framework",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "DIRS": [SITE_ROOT / "templates", ],
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}
