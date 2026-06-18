import logging

import requests
from django.conf import settings

logger = logging.getLogger("marryme.integrations.meta")

META_VERSION = "v18.0"
META_BASE = f"https://graph.facebook.com/{META_VERSION}"

INSIGHT_FIELDS = ",".join(
    [
        "impressions",
        "reach",
        "frequency",
        "spend",
        "cpm",
        "inline_link_clicks",
        "inline_link_click_ctr",
        "cost_per_inline_link_click",
        "clicks",
        "ctr",
        "actions",
        "cost_per_action_type",
        "video_thruplay_watched_actions",
        "video_p25_watched_actions",
        "video_p50_watched_actions",
        "video_p75_watched_actions",
        "video_p95_watched_actions",
    ]
)

MESSAGE_TYPES = [
    "onsite_conversion.messaging_conversation_started_7d",
    "messaging_conversation_started_7d",
    "lead",
    "offsite_conversion.fb_pixel_lead",
    "onsite_conversion.lead_grouped",
]


class MetaAdsClient:
    def __init__(self, token: str = None):
        self.token = token or settings.META_ACCESS_TOKEN
        self.app_id = settings.META_APP_ID
        self.app_secret = settings.META_APP_SECRET

    # ── Request base ─────────────────────────────────────────────

    def _get(self, path: str, params: dict) -> dict:
        params["access_token"] = self.token
        try:
            res = requests.get(f"{META_BASE}{path}", params=params, timeout=30)
            data = res.json()
            if not res.ok or "error" in data:
                msg = data.get("error", {}).get("message", str(res.status_code))
                logger.error(f"Meta API erro: {msg}")
                raise MetaAPIError(msg)
            return data
        except requests.Timeout:
            logger.error(f"Timeout Meta: {path}")
            raise

    # ── Token management ─────────────────────────────────────────

    def verificar_token(self) -> dict:
        """Verifica expiração via /debug_token"""
        try:
            app_token = f"{self.app_id}|{self.app_secret}"
            res = requests.get(
                f"{META_BASE}/debug_token",
                params={
                    "input_token": self.token,
                    "access_token": app_token,
                },
                timeout=15,
            )
            data = res.json().get("data", {})
            return {
                "valido": data.get("is_valid", True),
                "expira_em": data.get("expires_at", None),
                # 0 = token permanente (Usuário do Sistema)
            }
        except Exception as e:
            logger.warning(f"Não foi possível verificar token: {e}")
            return {"valido": True, "expira_em": None}

    def renovar_token(self) -> str:
        """Troca token atual por long-lived (~60 dias)"""
        res = requests.get(
            f"{META_BASE}/oauth/access_token",
            params={
                "grant_type": "fb_exchange_token",
                "client_id": self.app_id,
                "client_secret": self.app_secret,
                "fb_exchange_token": self.token,
            },
            timeout=15,
        )
        data = res.json()
        if not res.ok or "access_token" not in data:
            raise MetaAPIError(f"Falha ao renovar token: {data.get('error', {}).get('message')}")
        return data["access_token"]

    # ── Insights ─────────────────────────────────────────────────

    def get_insights_conta(self, account_id: str, time_range: dict) -> dict:
        """KPIs consolidados da conta com fallback para date_preset"""
        params = {
            "fields": INSIGHT_FIELDS,
            "time_range": str(time_range).replace("'", '"'),
        }
        data = self._get(f"/act_{account_id}/insights", params)

        if not data.get("data"):
            logger.warning("time_range sem dados — usando date_preset=last_30d")
            params.pop("time_range")
            params["date_preset"] = "last_30d"
            data = self._get(f"/act_{account_id}/insights", params)

        return data.get("data", [{}])[0]

    def get_insights_campanhas(self, account_id: str, time_range: dict) -> list:
        """Insights por campanha"""
        params = {
            "fields": f"campaign_id,campaign_name,{INSIGHT_FIELDS}",
            "level": "campaign",
            "time_range": str(time_range).replace("'", '"'),
        }
        data = self._get(f"/act_{account_id}/insights", params)

        if not data.get("data"):
            params.pop("time_range")
            params["date_preset"] = "last_30d"
            data = self._get(f"/act_{account_id}/insights", params)

        return data.get("data", [])

    def get_insights_anuncios(self, account_id: str, time_range: dict) -> list:
        """
        Nível de anúncio — fallback para video_p* quando
        conta/campanha não retornam dados de retenção.
        """
        VIDEO_FIELDS = ",".join(
            [
                "campaign_id",
                "video_p25_watched_actions",
                "video_p50_watched_actions",
                "video_p75_watched_actions",
                "video_p95_watched_actions",
            ]
        )
        params = {
            "fields": VIDEO_FIELDS,
            "level": "ad",
            "time_range": str(time_range).replace("'", '"'),
        }
        data = self._get(f"/act_{account_id}/insights", params)

        if not data.get("data"):
            params.pop("time_range")
            params["date_preset"] = "last_30d"
            data = self._get(f"/act_{account_id}/insights", params)

        return data.get("data", [])

    def get_retencao_video(self, account_id: str) -> dict:
        """
        Fallback final — curva de retenção real via Video Insights API.
        Usa total_video_retention_graph do primeiro vídeo com dados válidos.
        """
        try:
            ads = self._get(
                f"/act_{account_id}/ads",
                {"fields": "id,campaign_id,creative{video_id}", "limit": "25"},
            )
            video_ids = list(
                {
                    ad.get("creative", {}).get("video_id")
                    for ad in ads.get("data", [])
                    if ad.get("creative", {}).get("video_id")
                }
            )

            for video_id in video_ids:
                try:
                    res = self._get(
                        f"/{video_id}/video_insights",
                        {"fields": "total_video_retention_graph", "period": "lifetime"},
                    )
                    entry = next(
                        (
                            d
                            for d in res.get("data", [])
                            if d.get("name") == "total_video_retention_graph"
                        ),
                        None,
                    )
                    graph = entry.get("values", [{}])[0].get("value", {}) if entry else {}
                    if graph:
                        logger.info(f"Retenção via Video Insights: {video_id}")
                        return {"video_id": video_id, "graph": graph}
                except Exception:
                    continue
        except Exception as e:
            logger.warning(f"Video Insights indisponível: {e}")

        return {}

    def get_conta_info(self, account_id: str) -> dict:
        """Saldo e método de pagamento da conta"""
        try:
            return self._get(
                f"/act_{account_id}",
                {"fields": "balance,spend_cap,amount_spent,funding_source_details"},
            )
        except Exception as e:
            logger.warning(f"Info da conta indisponível: {e}")
            return {}


class MetaAPIError(Exception):
    pass
