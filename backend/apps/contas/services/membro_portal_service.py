import logging

from apps.contas.models import VinculoPrestador

logger = logging.getLogger('marryme.contas')


class MembroPortalService:

    def listar_membros(self, prestador) -> list[VinculoPrestador]:
        return list(
            VinculoPrestador.objects.filter(
                prestador=prestador,
                ativo=True,
            ).select_related('usuario').order_by('tipo', '-criado_em')
        )

    def revogar_membro(self, prestador, usuario_id) -> None:
        vinculo = VinculoPrestador.objects.filter(
            prestador=prestador,
            usuario_id=usuario_id,
            ativo=True,
        ).select_related('usuario').first()

        if not vinculo:
            raise ValueError('Membro não encontrado.')

        vinculo.ativo = False
        vinculo.save(update_fields=['ativo'])

        outros_vinculos = VinculoPrestador.objects.filter(
            usuario=vinculo.usuario,
            ativo=True,
        ).exists()

        if not outros_vinculos:
            vinculo.usuario.is_active = False
            vinculo.usuario.save(update_fields=['is_active'])

        logger.info(f'Membro revogado: {vinculo.usuario.email} → {prestador}')
