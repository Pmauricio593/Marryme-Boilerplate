import pytest


@pytest.mark.django_db
def test_listagem_prestadores_queries_nao_crescem_com_volume(
    api_cs, prestador_factory, django_assert_max_num_queries
):
    prestador_factory(nome_artistico="Artista 0")

    with django_assert_max_num_queries(4):
        response = api_cs.get("/api/v1/prestadores/")
    assert response.status_code == 200
    assert response.data["total"] == 1

    for i in range(1, 6):
        prestador_factory(nome_artistico=f"Artista {i}")

    with django_assert_max_num_queries(4):
        response = api_cs.get("/api/v1/prestadores/")
    assert response.status_code == 200
    assert response.data["total"] == 6
