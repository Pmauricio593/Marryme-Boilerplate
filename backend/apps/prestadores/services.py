import logging

from .models import Prestador

logger = logging.getLogger("marryme.prestadores")


class PrestadorService:
    """
    Lógica de negócio do módulo de prestadores.
    Operações síncronas — sem chamadas a APIs externas.
    """

    def atualizar_fase(self, prestador: Prestador, nova_fase: str) -> Prestador:
        """
        Atualiza fase do prestador e dispara pipelines automáticos
        quando necessário.
        """
        fase_anterior = prestador.fase
        prestador.fase = nova_fase
        prestador.save(update_fields=["fase", "atualizado_em"])

        logger.info(f"Fase atualizada: {prestador} | " f"{fase_anterior} → {nova_fase}")

        if nova_fase == "planejamento" and fase_anterior == "onboarding":
            self.criar_acesso_portal(prestador)
            self._disparar_pipeline_onboarding(prestador)

        return prestador

    def criar_acesso_portal(self, prestador) -> str | None:
        """
        Emite convite de acesso titular — usuário só é criado após aceitar o link.
        Chamado automaticamente quando prestador avança para 'planejamento'.
        """
        from apps.contas.services.convite_service import ConviteService

        return ConviteService().emitir_convite_titular(prestador)

    def _disparar_pipeline_onboarding(self, prestador: Prestador):
        """Enfileira tasks de geração de materiais para novo cliente."""
        from apps.roteiros.tasks import pipeline_onboarding

        pipeline_onboarding.delay(str(prestador.id))
        logger.info(f"Pipeline onboarding enfileirado: {prestador}")
