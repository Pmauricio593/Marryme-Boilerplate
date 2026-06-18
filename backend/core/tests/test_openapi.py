from io import StringIO

import pytest
import yaml
from django.core.management import call_command


@pytest.mark.django_db
def test_schema_endpoint_lista_recursos_principais(api):
    response = api.get("/api/v1/schema/")
    assert response.status_code == 200

    schema = yaml.safe_load(response.content)
    paths = schema.get("paths", {})

    for path in (
        "/api/v1/prestadores/",
        "/api/v1/prestadores/{prestador_id}/convites/",
        "/api/v1/health-scores/ultimo/",
        "/api/v1/sessoes/{id}/stream/",
        "/api/v1/portal/perfil/",
    ):
        assert path in paths, f"Endpoint ausente no schema: {path}"


def test_schema_gerado_sem_warnings():
    out = StringIO()
    call_command("spectacular", "--validate", "--fail-on-warn", stdout=out)
