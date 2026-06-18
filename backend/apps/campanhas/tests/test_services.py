from unittest.mock import MagicMock, patch

import pytest

from apps.campanhas.services import MetaSyncService, TokenService


@pytest.mark.django_db
@patch("apps.campanhas.services.MetaAdsClient")
@patch.object(TokenService, "get_token_ativo", return_value="token-fake")
def test_sincronizar_meta_mockado_calcula_e_salva_hs(
    mock_token, mock_client_cls, prestador_factory
):
    prestador = prestador_factory(meta_ad_account_id="act_123456")
    client = MagicMock()
    mock_client_cls.return_value = client
    client.get_insights_conta.return_value = {
        "impressions": "10000",
        "spend": "500",
        "frequency": "1.5",
        "ctr": "1.2",
        "inline_link_click_ctr": "1.5",
        "reach": "8000",
        "cpm": "50",
        "clicks": "120",
        "inline_link_clicks": "90",
        "actions": [
            {"action_type": "onsite_conversion.messaging_conversation_started_7d", "value": "20"}
        ],
        "cost_per_action_type": [
            {"action_type": "onsite_conversion.messaging_conversation_started_7d", "value": "25"}
        ],
    }
    client.get_insights_campanhas.return_value = [
        {
            "campaign_id": "1",
            "campaign_name": "Campanha Teste",
            "impressions": "10000",
            "clicks": "120",
            "ctr": "1.2",
            "spend": "500",
            "actions": [
                {
                    "action_type": "onsite_conversion.messaging_conversation_started_7d",
                    "value": "20",
                }
            ],
        }
    ]

    resultado = MetaSyncService().sincronizar(prestador, "2026-01-01", "2026-01-31")

    prestador.refresh_from_db()
    assert "health_score" in resultado
    assert prestador.health_score is not None
    assert prestador.health_status is not None
    client.get_insights_conta.assert_called_once()
    mock_token.assert_called_once()


@patch("apps.campanhas.services.MetaAdsClient")
@patch("apps.campanhas.services.settings.META_ACCESS_TOKEN", "token-env")
@patch("apps.campanhas.services.ConfiguracaoMeta.get", return_value=None)
def test_token_permanente_nao_renova(mock_get, mock_client_cls):
    client = MagicMock()
    mock_client_cls.return_value = client
    client.verificar_token.return_value = {"valido": True, "expira_em": 0}
    client.renovar_token.return_value = "novo-token"

    token = TokenService().get_token_ativo()

    assert token == "token-env"
    client.renovar_token.assert_not_called()
