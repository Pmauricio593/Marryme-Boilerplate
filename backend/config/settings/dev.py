from decouple import config

from .base import *  # noqa: F403
from .base import configure_logging

DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = [
    host.strip()
    for host in config("ALLOWED_HOSTS", default="localhost,127.0.0.1").split(",")
    if host.strip()
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://marryme.com.br",
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://marryme.com.br",
]

LOGGING = configure_logging(debug=DEBUG)
