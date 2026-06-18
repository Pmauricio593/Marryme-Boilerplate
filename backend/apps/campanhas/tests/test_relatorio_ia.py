from datetime import date
from unittest.mock import patch

import pytest

from apps.campanhas.models import MetricaMeta, RelatorioIA
from apps.campanhas.services import RelatorioIAService


@pytest.mark.django_db
@patch("integrations.claude_ai.ClaudeClient.chat")
def test_relatorio_ia_service_popula_dados_json(mock_chat, prestador_factory):
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

    RelatorioIAService().gerar_analise(relatorio)
    relatorio.refresh_from_db()

    assert relatorio.dados_json["analise"] == "Campanha estável."
    assert relatorio.dados_json["pauta_reuniao"] == ["Revisar criativo"]
    assert relatorio.dados_json["metricas_resumo"]["leads"] == 10
    assert relatorio.tokens_usados > 0
