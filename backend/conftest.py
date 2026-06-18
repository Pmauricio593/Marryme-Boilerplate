import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api():
    return APIClient()


@pytest.fixture
def usuario_cs(db):
    from apps.prestadores.factories import UsuarioFactory

    return UsuarioFactory(role="cs")


@pytest.fixture
def usuario_admin(db):
    from apps.prestadores.factories import UsuarioFactory

    return UsuarioFactory(role="admin")


@pytest.fixture
def api_cs(api, usuario_cs):
    api.force_authenticate(user=usuario_cs)
    return api


@pytest.fixture
def api_admin(api, usuario_admin):
    api.force_authenticate(user=usuario_admin)
    return api


@pytest.fixture
def prestador_factory():
    from apps.prestadores.factories import PrestadorFactory

    return PrestadorFactory
