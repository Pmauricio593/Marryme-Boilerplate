import logging
from .models import Prestador

logger = logging.getLogger('marryme.prestadores')


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
        prestador.save(update_fields=['fase', 'atualizado_em'])

        logger.info(
            f"Fase atualizada: {prestador} | "
            f"{fase_anterior} → {nova_fase}"
        )

        if nova_fase == 'planejamento' and fase_anterior == 'onboarding':
            self.criar_acesso_portal(prestador)
            self._disparar_pipeline_onboarding(prestador)

        return prestador

    def criar_acesso_portal(self, prestador) -> str:
        """
        Cria usuário de acesso para o prestador e envia convite.
        Chamado automaticamente quando prestador avança para 'planejamento'.
        """
        from .models import Usuario
        from .tokens import gerar_token_acesso
        from .emails import enviar_convite_acesso

        if hasattr(prestador, 'usuario_acesso') and prestador.usuario_acesso:
            logger.info(f"Prestador já tem acesso: {prestador}")
            return None

        if not prestador.email:
            logger.warning(f"Prestador sem email, acesso portal não criado: {prestador}")
            return None

        usuario = Usuario(
            username=prestador.email,
            email=prestador.email,
            role='prestador',
            prestador_vinculado=prestador,
        )
        usuario.set_unusable_password()
        usuario.save()

        token = gerar_token_acesso(usuario)
        enviar_convite_acesso(usuario, token, prestador.nome_artistico)

        logger.info(f"Acesso portal criado: {prestador}")
        return token

    def _disparar_pipeline_onboarding(self, prestador: Prestador):
        """Enfileira tasks de geração de materiais para novo cliente."""
        from apps.roteiros.tasks import pipeline_onboarding
        pipeline_onboarding.delay(str(prestador.id))
        logger.info(f"Pipeline onboarding enfileirado: {prestador}")
