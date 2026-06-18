import pytest
from rest_framework.test import APIClient

from apps.contas.services.convite_service import ConviteService
from apps.prestadores.factories import PrestadorFactory, UsuarioFactory


def _aceitar_convite_prestador(prestador, email: str, senha: str = "senha12345"):
    _, token = ConviteService().emitir(
        prestador=prestador,
        email=email,
        tipo="titular",
    )
    return ConviteService().aceitar(token=token, senha=senha, nome=prestador.nome_artistico)


@pytest.mark.django_db
def test_fluxo_convite_validar_aceitar_e_login_portal():
    prestador = PrestadorFactory(
        nome_artistico="Airton Sax",
        email="airton.portal@test.com",
    )
    _, token = ConviteService().emitir(
        prestador=prestador,
        email=prestador.email,
        tipo="titular",
    )

    client = APIClient()
    validar = client.get(f"/api/v1/portal/convites/validar/?token={token}")
    assert validar.status_code == 200
    assert validar.data["valido"] is True

    aceitar = client.post(
        "/api/v1/portal/convites/aceitar/",
        {"token": token, "senha": "senha12345", "nome": "Airton Sax"},
        format="json",
    )
    assert aceitar.status_code == 201
    assert "access" in aceitar.data

    login = client.post(
        "/api/v1/portal/auth/login/",
        {"email": prestador.email, "senha": "senha12345"},
        format="json",
    )
    assert login.status_code == 200
    assert login.data["nivel_acesso"] == "prestador"


@pytest.mark.django_db
def test_portal_prestador_ve_apenas_proprio_perfil():
    prestador_a = PrestadorFactory(
        nome_artistico="Prestador A",
        email="a.portal@test.com",
    )
    prestador_b = PrestadorFactory(
        nome_artistico="Prestador B",
        email="b.portal@test.com",
    )

    login_a = _aceitar_convite_prestador(prestador_a, prestador_a.email)
    login_b = _aceitar_convite_prestador(prestador_b, prestador_b.email)

    client_a = APIClient()
    client_a.credentials(HTTP_AUTHORIZATION=f"Bearer {login_a['access']}")
    perfil_a = client_a.get("/api/v1/portal/perfil/")
    assert perfil_a.status_code == 200
    assert perfil_a.data["nome_artistico"] == "Prestador A"

    client_b = APIClient()
    client_b.credentials(HTTP_AUTHORIZATION=f"Bearer {login_b['access']}")
    perfil_b = client_b.get("/api/v1/portal/perfil/")
    assert perfil_b.status_code == 200
    assert perfil_b.data["nome_artistico"] == "Prestador B"
    assert perfil_b.data["nome_artistico"] != perfil_a.data["nome_artistico"]


@pytest.mark.django_db
def test_assessoria_sem_permissao_roteiros_recebe_403():
    prestador = PrestadorFactory(email="assessoria@test.com")
    _, token = ConviteService().emitir(
        prestador=prestador,
        email="membro@assessoria.com",
        tipo="assessoria",
    )
    aceite = ConviteService().aceitar(
        token=token,
        senha="senha12345",
        nome="Assessoria Teste",
    )

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {aceite['access']}")
    response = client.get("/api/v1/portal/roteiros/")

    assert response.status_code == 403


@pytest.mark.django_db
def test_emitir_convite_requer_cs(api, prestador_factory):
    prestador = prestador_factory()
    usuario = UsuarioFactory(role="prestador")
    api.force_authenticate(user=usuario)

    response = api.post(
        f"/api/v1/prestadores/{prestador.id}/convites/",
        {
            "email": "novo@test.com",
            "tipo": "titular",
        },
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_prestador_a_nao_acessa_campanhas_de_b_via_portal():
    prestador_a = PrestadorFactory(email="a.camp@test.com")
    prestador_b = PrestadorFactory(email="b.camp@test.com")
    login_a = _aceitar_convite_prestador(prestador_a, prestador_a.email)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_a['access']}")

    response = client.get(f"/api/v1/portal/campanhas/?prestador_id={prestador_b.id}")
    assert response.status_code == 403


@pytest.mark.django_db
def test_prestador_a_nao_acessa_roteiros_de_b_via_portal():
    prestador_a = PrestadorFactory(email="a.rot@test.com")
    prestador_b = PrestadorFactory(email="b.rot@test.com")
    login_a = _aceitar_convite_prestador(prestador_a, prestador_a.email)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_a['access']}")

    response = client.get(f"/api/v1/portal/roteiros/?prestador_id={prestador_b.id}")
    assert response.status_code == 403


@pytest.mark.django_db
def test_prestador_nao_passa_prestador_id_arbitrario_no_perfil():
    prestador_a = PrestadorFactory(email="a.perf@test.com")
    PrestadorFactory(email="b.perf@test.com")
    login_a = _aceitar_convite_prestador(prestador_a, prestador_a.email)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_a['access']}")

    response = client.get(
        "/api/v1/portal/perfil/?prestador_id=00000000-0000-0000-0000-000000000099"
    )
    assert response.status_code == 403
