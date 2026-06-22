from decouple import config

from .base import *  # noqa: F403
from .base import configure_logging

DEBUG = False

ALLOWED_HOSTS = [
    host.strip() for host in config("ALLOWED_HOSTS", default="").split(",") if host.strip()
]

# Healthcheck interno do Railway usa Host: healthcheck.railway.app
if "healthcheck.railway.app" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append("healthcheck.railway.app")

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in config("CORS_ALLOWED_ORIGINS", default="https://marryme.com.br").split(",")
    if origin.strip()
]

_frontend_url = config("FRONTEND_URL", default="").rstrip("/")
if _frontend_url and _frontend_url not in CORS_ALLOWED_ORIGINS:
    CORS_ALLOWED_ORIGINS.append(_frontend_url)

_csrf_from_hosts = [f"https://{host}" for host in ALLOWED_HOSTS if host]
CSRF_TRUSTED_ORIGINS = list(
    dict.fromkeys(
        CORS_ALLOWED_ORIGINS
        + _csrf_from_hosts
        + [
            origin.strip()
            for origin in config("CSRF_TRUSTED_ORIGINS", default="").split(",")
            if origin.strip()
        ]
    )
)

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
