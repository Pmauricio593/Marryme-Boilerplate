from datetime import timedelta
from pathlib import Path

import dj_database_url
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config("SECRET_KEY")
ALLOWED_HOSTS: list[str] = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_celery_beat",
    "django_celery_results",
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "core",
    "apps.contas",
    "apps.prestadores",
    "apps.campanhas",
    "apps.roteiros",
]
AUTH_USER_MODEL = "prestadores.Usuario"

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
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
        "DIRS": [],
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
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

DATABASE_URL = config("DATABASE_URL", default=None)
if DATABASE_URL:
    DATABASES["default"] = dj_database_url.parse(DATABASE_URL)

REDIS_URL = config("REDIS_URL", default="redis://localhost:6379/0")
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOWED_ORIGINS: list[str] = []

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "core.authentication.MarryMeJWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "core.permissions.IsAuthenticatedMarryMe",
    ],
    "DEFAULT_PAGINATION_CLASS": "core.pagination.MarryMePagination",
    "PAGE_SIZE": 20,
    "EXCEPTION_HANDLER": "core.exceptions.custom_exception_handler",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=8),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "TOKEN_OBTAIN_SERIALIZER": "apps.contas.serializers.MarryMeTokenSerializer",
}
CONVITE_EXPIRACAO_HORAS = config("CONVITE_EXPIRACAO_HORAS", default=48, cast=int)

LOG_LEVEL = config("LOG_LEVEL", default="INFO")

ANTHROPIC_API_KEY = config("ANTHROPIC_API_KEY", default="")
META_ACCESS_TOKEN = config("META_ACCESS_TOKEN", default="")
META_APP_ID = config("META_APP_ID", default="")
META_APP_SECRET = config("META_APP_SECRET", default="")
APIFY_API_TOKEN = config("APIFY_API_TOKEN", default="")
CLAUDE_MODEL = config("CLAUDE_MODEL", default="claude-sonnet-4-6")

CELERY_BROKER_URL = config("REDIS_URL", default="redis://redis:6379/0")
CELERY_RESULT_BACKEND = "django-db"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "America/Sao_Paulo"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

FRONTEND_URL = config("FRONTEND_URL", default="https://marryme.com.br")
CSRF_TRUSTED_ORIGINS: list[str] = []

DEBUG = False
LOGGING: dict = {}


def configure_logging(*, debug: bool) -> dict:
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "{asctime} {levelname} {name} {message}",
                "style": "{",
            },
            "json": {
                "format": '{"ts":"%(asctime)s","level":"%(levelname)s",'
                '"logger":"%(name)s","msg":"%(message)s"}',
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "verbose" if debug else "json",
            },
        },
        "root": {"handlers": ["console"], "level": "WARNING"},
        "loggers": {
            "marryme": {
                "handlers": ["console"],
                "level": LOG_LEVEL,
                "propagate": False,
            },
            "django.request": {
                "handlers": ["console"],
                "level": "ERROR",
                "propagate": False,
            },
        },
    }
