from unittest.mock import patch

import pytest

from apps.prestadores.factories import UsuarioFactory


def _payload(**overrides):
    data = {
        "nome_artistico": "Airton Sax",
        "nome_completo": "Airton Silva",
        "categoria": "musico",
        "cidade": "São Paulo",
        "estado": "SP",
        "whatsapp": "11999999999",
        "email": "airton@test.com",
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
def test_cs_lista_prestadores(api_cs, prestador_factory):
    prestador_factory.create_batch(3)

    response = api_cs.get("/api/v1/prestadores/")

    assert response.status_code == 200
    assert response.data["total"] == 3
    assert len(response.data["resultados"]) == 3


@pytest.mark.django_db
def test_cs_cria_prestador(api_cs, usuario_cs):
    response = api_cs.post("/api/v1/prestadores/", _payload(), format="json")

    assert response.status_code == 201
    assert response.data["nome_artistico"] == "Airton Sax"
    assert response.data["responsavel"] == usuario_cs.id


@pytest.mark.django_db
def test_cs_retrieve_e_atualiza_prestador(api_cs, prestador_factory):
    prestador = prestador_factory(nome_artistico="Antes")

    detail = api_cs.get(f"/api/v1/prestadores/{prestador.id}/")
    assert detail.status_code == 200
    assert detail.data["nome_artistico"] == "Antes"

    update = api_cs.patch(
        f"/api/v1/prestadores/{prestador.id}/",
        {"cidade": "Campinas"},
        format="json",
    )
    assert update.status_code == 200
    assert update.data["cidade"] == "Campinas"


@pytest.mark.django_db
def test_cs_filtra_por_fase(api_cs, prestador_factory):
    prestador_factory(fase="onboarding")
    prestador_factory(fase="growth")

    response = api_cs.get("/api/v1/prestadores/", {"fase": "growth"})

    assert response.status_code == 200
    assert response.data["total"] == 1
    assert response.data["resultados"][0]["fase"] == "growth"


@pytest.mark.django_db
def test_cs_filtra_por_categoria(api_cs, prestador_factory):
    prestador_factory(categoria="musico")
    prestador_factory(categoria="dj")

    response = api_cs.get("/api/v1/prestadores/", {"categoria": "dj"})

    assert response.status_code == 200
    assert response.data["total"] == 1
    assert response.data["resultados"][0]["categoria"] == "dj"


@pytest.mark.django_db
def test_cs_filtra_por_busca(api_cs, prestador_factory):
    prestador_factory(nome_artistico="Banda Eclipse")
    prestador_factory(cidade="Curitiba")

    response = api_cs.get("/api/v1/prestadores/", {"busca": "Eclipse"})

    assert response.status_code == 200
    assert response.data["total"] == 1


@pytest.mark.django_db
@patch("apps.campanhas.tasks.sincronizar_todos_clientes.delay")
def test_cs_sync_todos_enfileira(mock_delay, api_cs):
    response = api_cs.post("/api/v1/prestadores/sync-todos/")

    assert response.status_code == 200
    assert response.data["status"] == "enfileirado"
    mock_delay.assert_called_once()


@pytest.mark.django_db
def test_cs_atualizar_fase_ok(api_cs, prestador_factory):
    prestador = prestador_factory(fase="onboarding")

    response = api_cs.post(
        f"/api/v1/prestadores/{prestador.id}/atualizar-fase/",
        {"fase": "planejamento"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["fase"] == "planejamento"


@pytest.mark.django_db
def test_cs_atualizar_fase_sem_campo_retorna_400(api_cs, prestador_factory):
    prestador = prestador_factory()

    response = api_cs.post(
        f"/api/v1/prestadores/{prestador.id}/atualizar-fase/",
        {},
        format="json",
    )

    assert response.status_code == 400
    assert "fase" in response.data["erro"].lower()


@pytest.mark.django_db
def test_cs_atualizar_fase_invalida_retorna_400(api_cs, prestador_factory):
    prestador = prestador_factory()

    response = api_cs.post(
        f"/api/v1/prestadores/{prestador.id}/atualizar-fase/",
        {"fase": "fase_inexistente"},
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
@patch("apps.campanhas.tasks.sincronizar_meta_ads.delay")
def test_cs_sync_meta_enfileira_task(mock_delay, api_cs, prestador_factory):
    prestador = prestador_factory(meta_ad_account_id="act_123")

    response = api_cs.post(f"/api/v1/prestadores/{prestador.id}/sync-meta/")

    assert response.status_code == 200
    assert response.data["status"] == "enfileirado"
    mock_delay.assert_called_once_with(str(prestador.id))


@pytest.mark.django_db
def test_cs_sync_meta_sem_conta_meta_retorna_400(api_cs, prestador_factory):
    prestador = prestador_factory(meta_ad_account_id="")

    response = api_cs.post(f"/api/v1/prestadores/{prestador.id}/sync-meta/")

    assert response.status_code == 400
    assert "Meta" in response.data["erro"]


@pytest.mark.django_db
def test_prestador_nao_acessa_crud_equipe(api, prestador_factory):
    usuario = UsuarioFactory(role="prestador")
    api.force_authenticate(user=usuario)
    alvo = prestador_factory()

    listagem = api.get("/api/v1/prestadores/")
    assert listagem.status_code == 403

    detalhe = api.get(f"/api/v1/prestadores/{alvo.id}/")
    assert detalhe.status_code == 403


@pytest.mark.django_db
def test_cs_nao_pode_excluir_prestador(api_cs, prestador_factory):
    prestador = prestador_factory()

    response = api_cs.delete(f"/api/v1/prestadores/{prestador.id}/")

    assert response.status_code == 403


@pytest.mark.django_db
def test_admin_pode_excluir_prestador(api_admin, prestador_factory):
    prestador = prestador_factory()

    response = api_admin.delete(f"/api/v1/prestadores/{prestador.id}/")

    assert response.status_code == 204
