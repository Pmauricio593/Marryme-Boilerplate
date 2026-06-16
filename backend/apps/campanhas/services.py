import logging
from datetime import date, datetime
from django.conf import settings
from apps.prestadores.models import Prestador
from integrations.meta_ads import MetaAdsClient
from .models import MetricaMeta, HealthScore, ConfiguracaoMeta

logger = logging.getLogger('marryme.campanhas')

SETE_DIAS = 7 * 86400

MESSAGE_TYPES = [
    "onsite_conversion.messaging_conversation_started_7d",
    "messaging_conversation_started_7d",
    "lead",
    "offsite_conversion.fb_pixel_lead",
    "onsite_conversion.lead_grouped",
]


class TokenService:
    """
    Gerencia ciclo de vida do token Meta.
    Lê do banco → verifica expiração → renova se necessário.
    Token permanente (expires_at=0) nunca é renovado.
    """

    def get_token_ativo(self) -> str:
        token = ConfiguracaoMeta.get(
            'meta_access_token') or settings.META_ACCESS_TOKEN
        if not token:
            raise ValueError("META_ACCESS_TOKEN não configurado.")

        client = MetaAdsClient(token=token)
        info = client.verificar_token()
        expira_em = info.get('expira_em')
        valido = info.get('valido', True)

        if expira_em == 0:
            return token  # token permanente — nunca renova

        agora = int(datetime.now().timestamp())
        expirado = not valido and expira_em is not None
        expirando = expira_em and expira_em > 0 and (
            expira_em - agora) < SETE_DIAS

        if expirado or expirando:
            logger.warning(
                f"Token {'expirado' if expirado else 'expirando'} — renovando...")
            try:
                novo_token = client.renovar_token()
                ConfiguracaoMeta.set('meta_access_token', novo_token)
                logger.info("Token renovado e salvo no banco.")
                return novo_token
            except Exception as e:
                if expirado:
                    raise
                logger.warning(f"Falha ao renovar (ainda válido): {e}")

        return token


class HealthScoreService:
    """
    Calcula health score baseado na fórmula oficial MarryMe.

    Pesos:
      Custo por Mensagem Iniciada  35 pts
      Hook Rate                    25 pts
      Retenção (ThruPlay/3s views) 20 pts — redistribuído se indisponível
      Frequência                   10 pts
      CTR botão de mensagem        10 pts

    Campanhas de Mensagens não retornam ThruPlay via API Meta —
    quando indisponível os 20 pts são redistribuídos para Hook Rate.
    Score máximo sem vídeo: normalizado de 55pts para escala 0-100.
    """

    def calcular(self, kpis: dict) -> dict:
        impressoes = kpis.get('impressions', 0)
        if not impressoes:
            return {'score': 0, 'status': 'sem_dados', 'breakdown': {}}

        tem_video = kpis.get('video_3s', 0) > 0
        tem_thruplay = tem_video and kpis.get('thruplay', 0) > 0

        scores = {
            'cpm':        self._score_cpm(kpis),
            'hook_rate':  self._score_hook_rate(kpis.get('hook_rate', 0)),
            'retencao':   self._score_retencao(kpis) if tem_thruplay else None,
            'frequencia': self._score_frequencia(kpis.get('frequency', 0)),
            'ctr':        self._score_ctr(kpis),
        }

        if not tem_video:
            # Sem vídeo: peso máximo = 55pts → normaliza para 0-100
            score_bruto = (
                scores['cpm'] * 0.35 +
                scores['frequencia'] * 0.10 +
                scores['ctr'] * 0.10
            )
            score_final = min(100, round((score_bruto / 55) * 100))

        elif not tem_thruplay:
            # Com vídeo mas sem ThruPlay: redistribui 20pts para hook_rate
            score_final = min(100, round(
                scores['cpm'] * 0.35 +
                scores['hook_rate'] * 0.45 +
                scores['frequencia'] * 0.10 +
                scores['ctr'] * 0.10
            ))

        else:
            # Fórmula completa com todos os componentes
            score_final = min(100, round(
                scores['cpm'] * 0.35 +
                scores['hook_rate'] * 0.25 +
                scores['retencao'] * 0.20 +
                scores['frequencia'] * 0.10 +
                scores['ctr'] * 0.10
            ))

        score_final = max(0, score_final)

        if score_final >= 70:
            status = 'saudavel'
        elif score_final >= 40:
            status = 'atencao'
        else:
            status = 'em_risco'

        logger.info(
            f"HS calculado → {score_final} ({status}) | "
            f"vídeo={tem_video} | thruplay={tem_thruplay}"
        )

        return {
            'score': score_final,
            'status': status,
            'tem_video': tem_video,
            'tem_thruplay': tem_thruplay,
            'breakdown': {k: v for k, v in scores.items() if v is not None},
        }

    def salvar(self, prestador: Prestador, resultado: dict, kpis: dict) -> HealthScore:
        hs = HealthScore.objects.create(
            prestador=prestador,
            data_calculo=date.today(),
            score=resultado['score'],
            status=resultado['status'],
            score_cpl=resultado['breakdown'].get('cpm', 0),
            score_orcamento=resultado['breakdown'].get('hook_rate', 0),
            score_leads=resultado['breakdown'].get('retencao', 0),
            score_ctr=resultado['breakdown'].get('ctr', 0),
            cpl_real=kpis.get('cost_per_result'),
            gasto_real=kpis.get('spend'),
            leads_real=kpis.get('results'),
        )
        prestador.health_score = resultado['score']
        prestador.health_status = resultado['status']
        prestador.save(
            update_fields=['health_score', 'health_status', 'atualizado_em'])
        logger.info(
            f"HS salvo: {prestador} → {resultado['score']} ({resultado['status']})")
        return hs

    # ── Componentes de score ──────────────────────────────────────

    def _score_cpm(self, kpis: dict) -> int:
        """Custo por mensagem iniciada. Benchmarks BR para casamentos."""
        cpm = kpis.get('cost_per_result', 0)
        if not cpm:
            return 0
        if cpm <= 10:
            return 35
        if cpm <= 25:
            return 26
        if cpm <= 50:
            return 17
        if cpm <= 100:
            return 8
        return 0

    def _score_hook_rate(self, hook_rate: float) -> int:
        """% que assistiu os primeiros 3s. Média BR feed ~10-15%."""
        if hook_rate >= 30:
            return 25
        if hook_rate >= 18:
            return 19
        if hook_rate >= 10:
            return 12
        if hook_rate >= 4:
            return 6
        return 0

    def _score_retencao(self, kpis: dict) -> int:
        """
        Retenção = ThruPlay / views 3s.
        Mede qual % de quem começou chegou ao fim (ThruPlay = 15s ou 100%).
        Indisponível em campanhas de Mensagens — campo fica None.
        """
        thruplay = kpis.get('thruplay', 0)
        video_3s = kpis.get('video_3s', 0)
        if not thruplay or not video_3s:
            return 0
        ret = (thruplay / video_3s) * 100
        if ret >= 60:
            return 20
        if ret >= 40:
            return 15
        if ret >= 25:
            return 10
        if ret >= 10:
            return 5
        return 0

    def _score_frequencia(self, freq: float) -> int:
        """Ideal 1-2 impressões por pessoa. Acima de 6 = audiência saturada."""
        if 1.0 <= freq <= 2.0:
            return 10
        if 2.0 < freq <= 3.0:
            return 7
        if 3.0 < freq <= 4.0:
            return 4
        if 4.0 < freq <= 6.0:
            return 1
        return 0

    def _score_ctr(self, kpis: dict) -> int:
        """CTR do botão de mensagem. Usa link_ctr com fallback para ctr."""
        ctr = kpis.get('link_ctr') or kpis.get('ctr', 0)
        if ctr >= 2.0:
            return 10
        if ctr >= 1.0:
            return 7
        if ctr >= 0.5:
            return 4
        if ctr >= 0.2:
            return 1
        return 0


class MetaSyncService:
    """
    Orquestra a sincronização completa de um prestador.

    Fluxo:
      1. Busca KPIs consolidados da conta
      2. Busca insights por campanha
      3. Fallback nível anúncio para video_p* (quando conta não retorna)
      4. Fallback Video Insights API (curva de retenção real)
      5. Calcula health score
      6. Salva métricas e score no banco
    """

    def __init__(self):
        self.hs = HealthScoreService()

    def sincronizar(self, prestador: Prestador, inicio: str, fim: str) -> dict:
        token = TokenService().get_token_ativo()
        client = MetaAdsClient(token=token)
        account_id = prestador.meta_ad_account_id.replace('act_', '')
        time_range = {'since': inicio, 'until': fim}

        # 1. KPIs da conta
        kpis_raw = client.get_insights_conta(account_id, time_range)
        kpis = self._extrair_kpis(kpis_raw)

        # 2. Campanhas
        campanhas_raw = client.get_insights_campanhas(account_id, time_range)

        # 3. Fallback anúncio para video_p*
        if kpis.get('thruplay', 0) > 0 and not kpis.get('video_p25'):
            logger.info(f"{prestador} — fallback nível anúncio para video_p*")
            ads_raw = client.get_insights_anuncios(account_id, time_range)
            kpis.update(self._agregar_video_ads(ads_raw))

        # 4. Fallback Video Insights (curva de retenção real)
        if kpis.get('thruplay', 0) > 0 and not kpis.get('video_p25'):
            logger.info(f"{prestador} — fallback Video Insights API")
            retencao = client.get_retencao_video(account_id)
            if retencao.get('graph'):
                kpis.update(
                    self._calcular_retencao_do_graph(
                        retencao['graph'],
                        kpis.get('video_3s', 0)
                    )
                )

        # 5. Calcula e salva HS
        resultado_hs = self.hs.calcular(kpis)
        self._salvar_metricas(prestador, campanhas_raw)
        self.hs.salvar(prestador, resultado_hs, kpis)

        logger.info(
            f"Sync OK: {prestador} | HS {resultado_hs['score']} "
            f"| {kpis.get('results', 0)} msgs | R${kpis.get('spend', 0):.2f}"
        )
        return {'kpis': kpis, 'health_score': resultado_hs}

    # ── Extração e helpers ───────────────────────────────────────

    def _extrair_kpis(self, raw: dict) -> dict:
        impressions = float(raw.get('impressions', 0))
        spend = float(raw.get('spend', 0))
        thruplay = self._video_val(raw.get('video_thruplay_watched_actions'))
        video_3s = self._action_val(raw.get('actions', []), ['video_view'])
        results = self._action_val(raw.get('actions', []), MESSAGE_TYPES)
        cost_per_result = self._action_val(
            raw.get('cost_per_action_type', []), MESSAGE_TYPES)

        return {
            'impressions':    impressions,
            'reach':          float(raw.get('reach', 0)),
            'frequency':      float(raw.get('frequency', 0)),
            'spend':          spend,
            'cpm':            float(raw.get('cpm', 0)),
            'clicks':         float(raw.get('clicks', 0)),
            'ctr':            float(raw.get('ctr', 0)),
            'link_clicks':    float(raw.get('inline_link_clicks', 0)),
            'link_ctr':       float(raw.get('inline_link_click_ctr', 0)),
            'results':        results,
            'cost_per_result': cost_per_result or (spend / results if results else 0),
            'thruplay':       thruplay,
            'video_3s':       video_3s,
            'hook_rate':      (video_3s / impressions * 100) if impressions else 0,
            'video_p25':      self._video_val(raw.get('video_p25_watched_actions')),
            'video_p50':      self._video_val(raw.get('video_p50_watched_actions')),
            'video_p75':      self._video_val(raw.get('video_p75_watched_actions')),
            'video_p100':     self._video_val(raw.get('video_p95_watched_actions')),
        }

    def _agregar_video_ads(self, ads: list) -> dict:
        """Agrega video_p* de todos os anúncios por conta."""
        totais = {'video_p25': 0, 'video_p50': 0,
                  'video_p75': 0, 'video_p100': 0}
        for ad in ads:
            totais['video_p25'] += self._video_val(
                ad.get('video_p25_watched_actions'))
            totais['video_p50'] += self._video_val(
                ad.get('video_p50_watched_actions'))
            totais['video_p75'] += self._video_val(
                ad.get('video_p75_watched_actions'))
            totais['video_p100'] += self._video_val(
                ad.get('video_p95_watched_actions'))
        return totais

    def _calcular_retencao_do_graph(self, graph: dict, video_3s: int) -> dict:
        """
        Converte curva de retenção do Video Insights em video_p*.
        Graph indexado por % (0-100) ou segundos (0-N) — detecta automaticamente.
        """
        if not graph or not video_3s:
            return {}

        keys = sorted(int(k) for k in graph.keys())
        max_key = keys[-1]
        base = graph.get(str(keys[0]), 100) or 100

        def ret(pct: int) -> float:
            idx = pct if max_key <= 100 else round(max_key * pct / 100)
            if str(idx) in graph:
                return (graph[str(idx)] or 0) / base
            lo = next((k for k in reversed(keys) if k < idx), None)
            hi = next((k for k in keys if k > idx), None)
            if lo is None or hi is None:
                return 0
            t = (idx - lo) / (hi - lo)
            return ((graph[str(lo)] or 0) * (1 - t) + (graph[str(hi)] or 0) * t) / base

        return {
            'video_p25':  round(video_3s * ret(25)),
            'video_p50':  round(video_3s * ret(50)),
            'video_p75':  round(video_3s * ret(75)),
            'video_p100': round(video_3s * ret(95)),
        }

    def _salvar_metricas(self, prestador: Prestador, campanhas: list):
        for c in campanhas:
            spend = float(c.get('spend', 0))
            results = self._action_val(c.get('actions', []), MESSAGE_TYPES)
            MetricaMeta.objects.update_or_create(
                prestador=prestador,
                campanha_id=c.get('campaign_id', ''),
                data_referencia=date.today(),
                defaults={
                    'campanha_nome': c.get('campaign_name', ''),
                    'impressoes':   int(float(c.get('impressions', 0))),
                    'cliques':      int(float(c.get('clicks', 0))),
                    'ctr':          float(c.get('ctr', 0)),
                    'leads':        results,
                    'gasto':        spend,
                    'cpl':          round(spend / results, 2) if results else 0,
                }
            )

    def _action_val(self, actions: list, tipos: list) -> float:
        for tipo in tipos:
            hit = next((a for a in actions if a.get(
                'action_type') == tipo), None)
            if hit:
                return float(hit.get('value', 0))
        return 0

    def _video_val(self, arr) -> float:
        if not arr or not isinstance(arr, list):
            return 0
        return float(arr[0].get('value', 0))
