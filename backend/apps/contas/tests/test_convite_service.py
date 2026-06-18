import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.contas.models import ConviteAcesso, VinculoPrestador
from apps.contas.services.convite_service import ConviteService
from apps.prestadores.factories import PrestadorFactory, UsuarioFactory

Usuario = get_user_model()


@pytest.mark.django_db
def test_emitir_convite_titular_sem_criar_usuario():
    prestador = PrestadorFactory(email="airton@test.com")
    admin = UsuarioFactory(role="admin", username="admin@test.com", email="admin@test.com")

    _, token = ConviteService().emitir(
        prestador=prestador,
        email=prestador.email,
        tipo="titular",
        criado_por=admin,
    )

    assert not Usuario.objects.filter(email=prestador.email).exists()
    assert ConviteAcesso.objects.count() == 1
    assert token


@pytest.mark.django_db
def test_aceitar_convite_cria_usuario_e_vinculo():
    prestador = PrestadorFactory(email="airton@test.com")

    _, token = ConviteService().emitir(
        prestador=prestador,
        email=prestador.email,
        tipo="titular",
    )

    resultado = ConviteService().aceitar(
        token=token,
        senha="senha12345",
        nome="Airton Sax",
    )

    assert Usuario.objects.filter(email=prestador.email, role="prestador").exists()
    assert VinculoPrestador.objects.count() == 1
    assert "access" in resultado
    assert resultado["nivel_acesso"] == "prestador"


@pytest.mark.django_db
def test_login_equipe_bloqueia_portal():
    prestador = PrestadorFactory(email="airton@test.com")

    _, token = ConviteService().emitir(
        prestador=prestador,
        email=prestador.email,
        tipo="titular",
    )
    ConviteService().aceitar(token=token, senha="senha12345")

    client = APIClient()
    response = client.post(
        "/api/v1/auth/login/",
        {"username": prestador.email, "password": "senha12345"},
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_validar_convite():
    prestador = PrestadorFactory(email="airton@test.com")

    _, token = ConviteService().emitir(
        prestador=prestador,
        email=prestador.email,
        tipo="titular",
    )

    client = APIClient()
    response = client.get(f"/api/v1/portal/convites/validar/?token={token}")

    assert response.status_code == 200
    assert response.data["valido"] is True
    assert "***" in response.data["email_mascarado"]
