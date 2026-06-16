import secrets
import logging
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger('marryme.prestadores')


def gerar_token_acesso(usuario) -> str:
    """
    Gera token de primeiro acesso para o prestador.
    Expira em 48h. Invalida tokens anteriores pendentes.
    """
    from .models import TokenPrimeiroAcesso

    # Invalida tokens anteriores não usados
    TokenPrimeiroAcesso.objects.filter(
        usuario=usuario,
        usado=False
    ).update(usado=True)

    token_str = secrets.token_urlsafe(32)

    TokenPrimeiroAcesso.objects.create(
        usuario=usuario,
        token=token_str,
        expira_em=timezone.now() + timedelta(hours=48)
    )

    logger.info(f"Token de acesso gerado: {usuario.email}")
    return token_str


def validar_token_acesso(token_str: str):
    """
    Valida e retorna o token se válido.
    Retorna None se inválido, expirado ou já usado.
    """
    from .models import TokenPrimeiroAcesso

    try:
        token = TokenPrimeiroAcesso.objects.select_related('usuario').get(
            token=token_str
        )
    except TokenPrimeiroAcesso.DoesNotExist:
        logger.warning(f"Token não encontrado: {token_str[:8]}...")
        return None

    if not token.valido:
        logger.warning(f"Token inválido/expirado: {token.usuario.email}")
        return None

    return token
