import logging
from datetime import date, timedelta

from celery import shared_task

logger = logging.getLogger("marryme.campanhas")


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def sincronizar_meta_ads(self, prestador_id: str):
    """
    Sincroniza métricas do Meta Ads para um prestador.
    Calcula health score e salva no banco automaticamente.
    Retry automático 3x com delay de 60s em caso de falha.
    """
    try:
        from apps.prestadores.models import Prestador

        from .services import MetaSyncService

        prestador = Prestador.objects.get(id=prestador_id)

        if not prestador.meta_ad_account_id:
            logger.warning(f"Prestador {prestador_id} sem ad_account_id")
            return {"status": "ignorado", "motivo": "sem ad_account_id"}

        fim = date.today().isoformat()
        inicio = (date.today() - timedelta(days=30)).isoformat()

        resultado = MetaSyncService().sincronizar(prestador, inicio, fim)

        logger.info(f"Sync OK: {prestador} | " f"HS {resultado['health_score']['score']}")
        return {"status": "ok", "resultado": resultado["health_score"]}

    except Exception as exc:
        logger.error(f"Erro sync {prestador_id}: {exc}")
        raise self.retry(exc=exc) from exc


@shared_task
def sincronizar_todos_clientes():
    """
    Enfileira sync do Meta Ads para todos os clientes ativos.
    Roda toda segunda às 8h via Celery Beat.
    """
    from apps.prestadores.models import Prestador

    prestadores = Prestador.objects.exclude(meta_ad_account_id="").filter(
        fase__in=["growth", "voo_cruzeiro", "planejamento"]
    )

    for prestador in prestadores:
        sincronizar_meta_ads.delay(str(prestador.id))

    logger.info(f"{prestadores.count()} clientes enfileirados")
    return {"status": "ok", "total": prestadores.count()}


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def calcular_health_score(self, prestador_id: str):
    """
    Recalcula o health score com as métricas já salvas no banco.
    Útil para recalcular sem nova sync do Meta.
    """
    try:
        from apps.prestadores.models import Prestador

        from .models import MetricaMeta
        from .services import HealthScoreService

        prestador = Prestador.objects.get(id=prestador_id)
        metricas = (
            MetricaMeta.objects.filter(prestador=prestador).order_by("-data_referencia").first()
        )

        if not metricas:
            logger.warning(f"Sem métricas para {prestador_id}")
            return {"status": "ignorado", "motivo": "sem métricas"}

        kpis = {
            "impressions": metricas.impressoes,
            "spend": float(metricas.gasto),
            "results": metricas.leads,
            "cost_per_result": float(metricas.cpl),
            "ctr": float(metricas.ctr),
            "frequency": 0,
            "video_3s": 0,
            "hook_rate": 0,
            "thruplay": 0,
        }

        resultado = HealthScoreService().calcular(kpis)
        HealthScoreService().salvar(prestador, resultado, kpis)

        return {"status": "ok", "score": resultado["score"]}

    except Exception as exc:
        logger.error(f"Erro HS {prestador_id}: {exc}")
        raise self.retry(exc=exc) from exc


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def gerar_analise_relatorio(self, relatorio_id: str):
    """Gera análise IA e pauta de reunião para um RelatorioIA."""
    try:
        from .models import RelatorioIA
        from .services import RelatorioIAService

        relatorio = RelatorioIA.objects.select_related("prestador").get(id=relatorio_id)
        RelatorioIAService().gerar_analise(relatorio)

        logger.info(f"Análise IA concluída: relatório {relatorio_id}")
        return {"status": "ok", "relatorio_id": relatorio_id}

    except Exception as exc:
        logger.error(f"Erro análise relatório {relatorio_id}: {exc}")
        raise self.retry(exc=exc) from exc
