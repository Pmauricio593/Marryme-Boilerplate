from decouple import config

from .base import *  # noqa: F403
from .base import configure_logging

DEBUG = False

ALLOWED_HOSTS = [
    host.strip() for host in config("ALLOWED_HOSTS", default="").split(",") if host.strip()
]

CORS_ALLOWED_ORIGINS = [
    "https://marryme.com.br",
]

CSRF_TRUSTED_ORIGINS = [
    "https://web-production-62d5c.up.railway.app",
    "https://marryme.com.br",
]

SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

LOGGING = configure_logging(debug=DEBUG)
