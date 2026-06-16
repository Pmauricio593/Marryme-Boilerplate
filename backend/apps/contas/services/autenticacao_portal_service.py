import logging

from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.contas.constants import ROLES_PORTAL, role_para_nivel
from apps.contas.models import VinculoPrestador
from apps.contas.permissions import get_vinculo_ativo
from apps.prestadores.models import Usuario

logger = logging.getLogger('marryme.contas')


class AutenticacaoPortalService:

    def login(self, email: str, senha: str) -> dict:
        email = email.strip().lower()

        try:
            usuario = Usuario.objects.get(email=email, role__in=ROLES_PORTAL)
        except Usuario.DoesNotExist:
            raise ValidationError('Credenciais inválidas.')

        if not usuario.check_password(senha):
            raise ValidationError('Credenciais inválidas.')

        if not usuario.is_active:
            raise ValidationError('Acesso inativo. Entre em contato com a MarryMe.')

        vinculo = get_vinculo_ativo(usuario)
        if not vinculo:
            raise ValidationError('Nenhum prestador vinculado.')

        logger.info(f'Login portal: {usuario.email}')
        return self.gerar_resposta_login(usuario, vinculo)

    def gerar_resposta_login(self, usuario: Usuario, vinculo: VinculoPrestador) -> dict:
        refresh = RefreshToken.for_user(usuario)
        permissoes = vinculo.permissoes_efetivas()
        nome = vinculo.prestador.nome_artistico

        refresh['role'] = usuario.role
        refresh['nivel_acesso'] = role_para_nivel(usuario.role)
        refresh['nome'] = nome
        refresh['tipo_portal'] = vinculo.tipo
        refresh['prestador_id'] = str(vinculo.prestador_id)
        refresh['permissoes_portal'] = permissoes

        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'role': usuario.role,
            'nivel_acesso': role_para_nivel(usuario.role),
            'tipo_portal': vinculo.tipo,
            'prestador_id': str(vinculo.prestador_id),
            'permissoes_portal': permissoes,
            'nome': nome,
        }
