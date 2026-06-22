from unittest.mock import patch

import pytest
from django.test import override_settings

from apps.campanhas.models import RelatorioIA


@pytest.mark.django_db
@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
@patch("integrations.claude_ai.ClaudeClient.chat")
def test_gerar_analise_via_api_popula_dados_json(mock_chat, api_cs, prestador_factory):
    from datetime import date

    from apps.campanhas.models import MetricaMeta

    mock_chat.return_value = (
        '{"analise": "Campanha estável.", '
        '"pauta_reuniao": ["Revisar criativo"], "acoes_cs": ["Agendar call"]}'
    )

    prestador = prestador_factory()
    MetricaMeta.objects.create(
        prestador=prestador,
        data_referencia=date(2026, 1, 15),
        campanha_id="1",
        campanha_nome="Teste",
        impressoes=1000,
        leads=10,
        gasto=500,
    )
    relatorio = RelatorioIA.objects.create(
        prestador=prestador,
        periodo_inicio=date(2026, 1, 1),
        periodo_fim=date(2026, 1, 31),
        dados_json={},
    )

    post_response = api_cs.post(f"/api/v1/relatorios/{relatorio.id}/gerar-analise/")
    assert post_response.status_code == 200
    assert post_response.data["status"] == "enfileirado"

    get_response = api_cs.get(f"/api/v1/relatorios/{relatorio.id}/")
    assert get_response.status_code == 200
    assert get_response.data["dados_json"]["analise"] == "Campanha estável."
    assert get_response.data["dados_json"]["pauta_reuniao"] == ["Revisar criativo"]
    assert get_response.data["dados_json"]["acoes_cs"] == ["Agendar call"]


@pytest.mark.django_db
def test_ultimo_health_score_exige_prestador(api_cs):
    response = api_cs.get("/api/v1/health-scores/ultimo/")

    assert response.status_code == 400
    assert "prestador" in response.data["erro"].lower()


@pytest.mark.django_db
def test_ultimo_health_score_retorna_404_quando_vazio(api_cs, prestador_factory):
    prestador = prestador_factory()

    response = api_cs.get(f"/api/v1/health-scores/ultimo/?prestador={prestador.id}")

    assert response.status_code == 404


@pytest.mark.django_db
def test_ultimo_health_score_retorna_mais_recente(api_cs, prestador_factory):
    from datetime import date, timedelta

    from apps.campanhas.models import HealthScore

    prestador = prestador_factory()
    HealthScore.objects.create(
        prestador=prestador,
        data_calculo=date.today() - timedelta(days=2),
        score=30,
        status="em_risco",
        score_cpl=0,
        score_orcamento=0,
        score_leads=0,
        score_ctr=0,
    )
    recente = HealthScore.objects.create(
        prestador=prestador,
        data_calculo=date.today(),
        score=55,
        status="atencao",
        score_cpl=0,
        score_orcamento=0,
        score_leads=0,
        score_ctr=0,
    )

    response = api_cs.get(f"/api/v1/health-scores/ultimo/?prestador={prestador.id}")

    assert response.status_code == 200
    assert response.data["id"] == str(recente.id)
    assert response.data["score"] == 55


@pytest.mark.django_db
@patch("apps.campanhas.tasks.gerar_analise_relatorio.delay")
def test_gerar_analise_enfileira_task(mock_delay, api_cs, prestador_factory):
    prestador = prestador_factory()
    relatorio = RelatorioIA.objects.create(
        prestador=prestador,
        periodo_inicio="2026-01-01",
        periodo_fim="2026-01-31",
        dados_json={},
    )

    response = api_cs.post(f"/api/v1/relatorios/{relatorio.id}/gerar-analise/")

    assert response.status_code == 200
    assert response.data["status"] == "enfileirado"
    mock_delay.assert_called_once_with(str(relatorio.id))
