import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env first, then environment-specific overrides (.env.production, etc.)
load_dotenv(BASE_DIR / ".env")
environment_name = os.environ.get("DJANGO_ENV")
if environment_name:
    env_file = BASE_DIR / f".env.{environment_name.lower()}"
    if env_file.exists():
        load_dotenv(env_file, override=True)


def _split_csv(value: str | None, fallback: str = "") -> list[str]:
    raw = value if value is not None else fallback
    return [item.strip() for item in raw.split(",") if item.strip()]


SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise ImproperlyConfigured("SECRET_KEY is not set. Provide it via environment variables.")

DEBUG = os.environ.get("DEBUG", "0").lower() in {"1", "true", "yes"}

ALLOWED_HOSTS = _split_csv(os.environ.get("ALLOWED_HOSTS"), fallback="127.0.0.1,localhost")
CSRF_TRUSTED_ORIGINS = _split_csv(os.environ.get("CSRF_TRUSTED_ORIGINS"))

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "services",
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

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
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

WSGI_APPLICATION = "core.wsgi.application"

database_url = os.environ.get("DATABASE_URL", "").strip()
use_sqlite = os.environ.get("USE_SQLITE", "0").lower() in {"1", "true", "yes"}

if database_url:
    default_db = dj_database_url.parse(database_url, conn_max_age=600, ssl_require=False)
elif use_sqlite:
    default_db = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
else:
    raise ImproperlyConfigured(
        "DATABASE_URL is not set. Provide a Postgres URL or set USE_SQLITE=1 for local development."
    )

DATABASES = {"default": default_db}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise для статики в продакшене
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "services.User"

LOGIN_URL = "services:login"
LOGIN_REDIRECT_URL = "services:dashboard"
LOGOUT_REDIRECT_URL = "services:service_list"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
}

