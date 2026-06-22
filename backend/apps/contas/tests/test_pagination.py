import pytest

from apps.contas.services.convite_service import ConviteService


@pytest.mark.django_db
def test_listagem_convites_retorna_formato_paginado(api_cs, prestador_factory):
    prestador = prestador_factory()
    ConviteService().emitir(
        prestador=prestador,
        email="a@test.com",
        tipo="titular",
    )
    ConviteService().emitir(
        prestador=prestador,
        email="b@test.com",
        tipo="assessoria",
    )

    response = api_cs.get(f"/api/v1/prestadores/{prestador.id}/convites/")

    assert response.status_code == 200
    assert "resultados" in response.data
    assert response.data["total"] == 2
    assert len(response.data["resultados"]) == 2
    assert response.data["pagina_atual"] == 1


@pytest.mark.django_db
def test_listagem_membros_retorna_formato_paginado(api_cs, prestador_factory):
    prestador = prestador_factory(email="membro@test.com")
    ConviteService().emitir(
        prestador=prestador,
        email=prestador.email,
        tipo="titular",
    )
    _, token = ConviteService().emitir(
        prestador=prestador,
        email="assessoria@test.com",
        tipo="assessoria",
    )
    ConviteService().aceitar(token=token, senha="senha12345", nome="Assessoria")

    response = api_cs.get(f"/api/v1/prestadores/{prestador.id}/membros/")

    assert response.status_code == 200
    assert "resultados" in response.data
    assert response.data["total"] >= 1
    assert isinstance(response.data["resultados"], list)
