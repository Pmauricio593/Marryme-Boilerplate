import hashlib
import logging
import secrets
from dataclasses import dataclass
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.contas.constants import PERMISSOES_ASSESSORIA_DEFAULT, PERMISSOES_TITULAR
from apps.contas.emails import enviar_convite_acesso
from apps.contas.models import ConviteAcesso, VinculoPrestador
from apps.contas.services.autenticacao_portal_service import AutenticacaoPortalService
from apps.prestadores.models import Prestador, Usuario

logger = logging.getLogger('marryme.contas')


@dataclass
class ConviteValidacaoDTO:
    valido: bool
    email_mascarado: str
    tipo: str
    prestador_nome: str
    expira_em: str | None
    erro: str | None = None


class ConviteService:

    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    def _expiracao_horas(self) -> int:
        return int(getattr(settings, 'CONVITE_EXPIRACAO_HORAS', 48))

    def _mascarar_email(self, email: str) -> str:
        local, _, domain = email.partition('@')
        if len(local) <= 2:
            masked = local[0] + '***'
        else:
            masked = local[0] + '***' + local[-1]
        return f'{masked}@{domain}'

    def emitir(
        self,
        prestador: Prestador,
        email: str,
        tipo: str,
        permissoes: dict | None = None,
        criado_por: Usuario | None = None,
        enviar: bool = True,
    ) -> tuple[ConviteAcesso, str]:
        email = email.strip().lower()

        if tipo == 'titular':
            if VinculoPrestador.objects.filter(
                prestador=prestador, tipo='titular', ativo=True
            ).exists():
                raise ValidationError('Prestador já possui titular ativo.')

            ConviteAcesso.objects.filter(
                prestador=prestador,
                tipo='titular',
                status='pendente',
            ).update(status='revogado')

        token_raw = secrets.token_urlsafe(32)
        permissoes_efetivas = (
            PERMISSOES_TITULAR if tipo == 'titular'
            else (permissoes or PERMISSOES_ASSESSORIA_DEFAULT)
        )

        convite = ConviteAcesso.objects.create(
            prestador=prestador,
            email=email,
            tipo=tipo,
            permissoes_portal=permissoes_efetivas,
            token_hash=self._hash_token(token_raw),
            expira_em=timezone.now() + timedelta(hours=self._expiracao_horas()),
            criado_por=criado_por,
        )

        if enviar:
            enviar_convite_acesso(
                email=email,
                token=token_raw,
                nome_prestador=prestador.nome_artistico,
                tipo=tipo,
            )

        logger.info(f'Convite emitido: {email} → {prestador} ({tipo})')
        return convite, token_raw

    def emitir_convite_titular(
        self,
        prestador: Prestador,
        criado_por: Usuario | None = None,
    ) -> str | None:
        if not prestador.email:
            logger.warning(f'Prestador sem email: {prestador}')
            return None

        if VinculoPrestador.objects.filter(
            prestador=prestador, tipo='titular', ativo=True
        ).exists():
            logger.info(f'Titular já ativo: {prestador}')
            return None

        if ConviteAcesso.objects.filter(
            prestador=prestador, tipo='titular', status='pendente'
        ).exists():
            logger.info(f'Convite titular pendente: {prestador}')
            return None

        _, token = self.emitir(
            prestador=prestador,
            email=prestador.email,
            tipo='titular',
            criado_por=criado_por,
        )
        return token

    def _buscar_por_token(self, token: str) -> ConviteAcesso | None:
        token_hash = self._hash_token(token.strip())
        try:
            return ConviteAcesso.objects.select_related('prestador').get(
                token_hash=token_hash
            )
        except ConviteAcesso.DoesNotExist:
            return None

    def validar(self, token: str) -> ConviteValidacaoDTO:
        convite = self._buscar_por_token(token)

        if not convite:
            return ConviteValidacaoDTO(
                valido=False,
                email_mascarado='',
                tipo='',
                prestador_nome='',
                expira_em=None,
                erro='Token inválido.',
            )

        if convite.status != 'pendente':
            return ConviteValidacaoDTO(
                valido=False,
                email_mascarado=self._mascarar_email(convite.email),
                tipo=convite.tipo,
                prestador_nome=convite.prestador.nome_artistico,
                expira_em=convite.expira_em.isoformat(),
                erro='Convite já utilizado ou revogado.',
            )

        if convite.expirado:
            convite.status = 'expirado'
            convite.save(update_fields=['status'])
            return ConviteValidacaoDTO(
                valido=False,
                email_mascarado=self._mascarar_email(convite.email),
                tipo=convite.tipo,
                prestador_nome=convite.prestador.nome_artistico,
                expira_em=convite.expira_em.isoformat(),
                erro='Convite expirado.',
            )

        return ConviteValidacaoDTO(
            valido=True,
            email_mascarado=self._mascarar_email(convite.email),
            tipo=convite.tipo,
            prestador_nome=convite.prestador.nome_artistico,
            expira_em=convite.expira_em.isoformat(),
        )

    @transaction.atomic
    def aceitar(self, token: str, senha: str, nome: str | None = None) -> dict:
        if len(senha) < 8:
            raise ValidationError('Senha deve ter no mínimo 8 caracteres.')

        validacao = self.validar(token)
        if not validacao.valido:
            raise ValidationError(validacao.erro or 'Convite inválido.')

        convite = self._buscar_por_token(token)
        if not convite:
            raise ValidationError('Token inválido.')

        role = 'prestador' if convite.tipo == 'titular' else 'assessoria'
        usuario = Usuario.objects.filter(email=convite.email).first()

        if usuario:
            if convite.tipo == 'titular':
                raise ValidationError('Email já cadastrado.')
            if VinculoPrestador.objects.filter(
                usuario=usuario, prestador=convite.prestador
            ).exists():
                raise ValidationError('Usuário já vinculado a este prestador.')
        else:
            usuario = Usuario(
                username=convite.email,
                email=convite.email,
                role=role,
            )
            if nome:
                partes = nome.strip().split(' ', 1)
                usuario.first_name = partes[0]
                if len(partes) > 1:
                    usuario.last_name = partes[1]

        usuario.set_password(senha)
        usuario.save()

        VinculoPrestador.objects.create(
            usuario=usuario,
            prestador=convite.prestador,
            tipo=convite.tipo,
            permissoes_portal=convite.permissoes_efetivas(),
        )

        convite.status = 'usado'
        convite.usado_em = timezone.now()
        convite.usuario_criado = usuario
        convite.save(update_fields=['status', 'usado_em', 'usuario_criado'])

        vinculo = VinculoPrestador.objects.get(usuario=usuario, prestador=convite.prestador)
        logger.info(f'Convite aceito: {usuario.email} → {convite.prestador}')

        return AutenticacaoPortalService().gerar_resposta_login(usuario, vinculo)

    def reenviar(self, convite: ConviteAcesso, criado_por: Usuario | None = None) -> tuple[ConviteAcesso, str]:
        if convite.status != 'pendente':
            raise ValidationError('Apenas convites pendentes podem ser reenviados.')

        convite.status = 'revogado'
        convite.save(update_fields=['status'])

        return self.emitir(
            prestador=convite.prestador,
            email=convite.email,
            tipo=convite.tipo,
            permissoes=convite.permissoes_portal,
            criado_por=criado_por,
        )

    def revogar(self, convite: ConviteAcesso) -> None:
        if convite.status != 'pendente':
            raise ValidationError('Apenas convites pendentes podem ser revogados.')

        convite.status = 'revogado'
        convite.save(update_fields=['status'])
        logger.info(f'Convite revogado: {convite.email} → {convite.prestador}')
