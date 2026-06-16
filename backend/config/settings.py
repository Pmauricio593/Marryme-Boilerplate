import os
from pathlib import Path
from decouple import config
import dj_database_url
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_beat',
    'django_celery_results',
    # Terceiros
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    # MarryMe — core primeiro, depois os apps
    'core',
    'apps.prestadores',
    'apps.campanhas',
    'apps.roteiros',
]
AUTH_USER_MODEL = 'prestadores.Usuario'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Sobrescreve o banco com a DATABASE_URL se existir
DATABASE_URL = config('DATABASE_URL', default=None)
if DATABASE_URL:
    DATABASES['default'] = dj_database_url.parse(DATABASE_URL)

REDIS_URL = config('REDIS_URL', default='redis://localhost:6379/0')
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://marryme.com.br",
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'core.authentication.MarryMeJWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'core.permissions.IsAuthenticatedMarryMe',
    ],
    'DEFAULT_PAGINATION_CLASS': 'core.pagination.MarryMePagination',
    'PAGE_SIZE': 20,
    'EXCEPTION_HANDLER': 'core.exceptions.custom_exception_handler',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME':  timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS':  True,
    'TOKEN_OBTAIN_SERIALIZER': 'apps.prestadores.serializers.MarryMeTokenSerializer',
}
ANTHROPIC_API_KEY = config('ANTHROPIC_API_KEY', default='')
META_ACCESS_TOKEN = config('META_ACCESS_TOKEN', default='')
META_APP_ID = config('META_APP_ID', default='')
META_APP_SECRET = config('META_APP_SECRET', default='')
APIFY_API_TOKEN = config('APIFY_API_TOKEN', default='')
CLAUDE_MODEL = config('CLAUDE_MODEL', default='claude-sonnet-4-6')

# Celery — broker Redis; resultados persistidos no Postgres via django-celery-results
CELERY_BROKER_URL = config('REDIS_URL', default='redis://redis:6379/0')
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Sao_Paulo'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutos máximo por task
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

FRONTEND_URL = config('FRONTEND_URL', default='https://marryme.com.br')
CSRF_TRUSTED_ORIGINS = [
    'https://web-production-62d5c.up.railway.app',
    'https://marryme.com.br',
]
