import logging
from celery import shared_task

logger = logging.getLogger('marryme.roteiros')


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def gerar_analise_estrategica(self, prestador_id: str):
    """
    Gera análise estratégica completa via Claude.
    Cria uma sessão de chat do tipo 'analise' e processa automaticamente.
    """
    try:
        from apps.prestadores.models import Prestador
        from apps.roteiros.models import ChatSessao
        from apps.roteiros.services import ChatService

        prestador = Prestador.objects.get(id=prestador_id)

        sessao = ChatSessao.objects.create(
            prestador=prestador,
            titulo='Análise Estratégica — gerada automaticamente',
            tipo='analise',
        )

        prompt = (
            "Faça uma análise estratégica completa do prestador com base "
            "nos dados da entrevista. Apresente: posicionamento sugerido, "
            "público-alvo, principais diferenciais, tom de comunicação e "
            "recomendações para a campanha Meta Ads."
        )

        resposta = ChatService().processar_mensagem(sessao, prompt)

        # Salva análise no prestador para consulta rápida
        prestador.analise_estrategica = {'conteudo': resposta}
        prestador.save(update_fields=['analise_estrategica', 'atualizado_em'])

        logger.info(f"Análise gerada: {prestador}")
        return {'status': 'ok', 'sessao_id': str(sessao.id)}

    except Exception as exc:
        logger.error(f"Erro análise {prestador_id}: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2)
def pipeline_onboarding(self, prestador_id: str):
    """
    Pipeline automático para novo cliente.
    Disparado quando prestador avança para fase 'planejamento'.
    Encadeia: análise estratégica → notifica equipe.
    """
    try:
        from apps.prestadores.models import Prestador
        prestador = Prestador.objects.get(id=prestador_id)

        logger.info(f"Pipeline onboarding iniciado: {prestador}")

        # Enfileira análise estratégica
        gerar_analise_estrategica.delay(prestador_id)

        # Próximas tasks encadeadas virão aqui:
        # gerar_roteiro_base.delay(prestador_id)
        # gerar_ctas_base.delay(prestador_id)

        return {'status': 'ok', 'prestador': str(prestador)}

    except Exception as exc:
        logger.error(f"Erro pipeline {prestador_id}: {exc}")
        raise self.retry(exc=exc)
