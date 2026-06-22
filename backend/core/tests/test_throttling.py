import pytest
from django.test import override_settings
from rest_framework.test import APIClient


@pytest.mark.django_db
@override_settings(
    REST_FRAMEWORK={
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "core.authentication.MarryMeJWTAuthentication",
        ],
        "DEFAULT_PERMISSION_CLASSES": [
            "core.permissions.IsAuthenticatedMarryMe",
        ],
        "DEFAULT_THROTTLE_CLASSES": [
            "rest_framework.throttling.AnonRateThrottle",
        ],
        "DEFAULT_THROTTLE_RATES": {
            "anon": "2/min",
        },
        "EXCEPTION_HANDLER": "core.exceptions.custom_exception_handler",
    }
)
def test_rate_limit_retorna_429_em_portugues():
    client = APIClient()

    for _ in range(2):
        response = client.get("/api/v1/schema/")
        assert response.status_code == 200

    response = client.get("/api/v1/schema/")
    assert response.status_code == 429
    assert response.data["erro"] == "Muitas requisições. Aguarde e tente novamente."
    assert response.data["status"] == 429
