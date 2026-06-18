from unittest.mock import patch

import pytest

from apps.prestadores.factories import PrestadorFactory
from apps.prestadores.models import Prestador
from apps.prestadores.services import PrestadorService


@pytest.mark.django_db
def test_prestador_str():
    prestador = PrestadorFactory(nome_artistico="Airton Sax", categoria="musico")

    assert str(prestador) == "Airton Sax (musico)"


@pytest.mark.django_db
def test_atualizar_fase_altera_campo():
    prestador = PrestadorFactory(fase="growth")

    atualizado = PrestadorService().atualizar_fase(prestador, "voo_cruzeiro")

    assert atualizado.fase == "voo_cruzeiro"
    prestador.refresh_from_db()
    assert prestador.fase == "voo_cruzeiro"


@pytest.mark.django_db
@patch("apps.roteiros.tasks.pipeline_onboarding.delay")
@patch("apps.contas.services.convite_service.ConviteService.emitir_convite_titular")
def test_atualizar_fase_onboarding_para_planejamento_dispara_automacoes(
    mock_emitir_convite,
    mock_pipeline,
):
    mock_emitir_convite.return_value = "token-fake"
    prestador = PrestadorFactory(fase="onboarding")

    PrestadorService().atualizar_fase(prestador, "planejamento")

    prestador.refresh_from_db()
    assert prestador.fase == "planejamento"
    mock_emitir_convite.assert_called_once_with(prestador)
    mock_pipeline.assert_called_once_with(str(prestador.id))


@pytest.mark.django_db
def test_ordering_por_atualizado_em_desc():
    antigo = PrestadorFactory(nome_artistico="Antigo")
    recente = PrestadorFactory(nome_artistico="Recente")
    Prestador.objects.filter(pk=antigo.pk).update(fase="growth")

    ids = list(Prestador.objects.values_list("id", flat=True))

    assert ids[0] == recente.id
