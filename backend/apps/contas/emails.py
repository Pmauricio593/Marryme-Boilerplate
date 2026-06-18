import logging

from django.conf import settings

logger = logging.getLogger("marryme.contas")


def enviar_convite_acesso(email: str, token: str, nome_prestador: str, tipo: str):
    base_url = getattr(settings, "FRONTEND_URL", "https://marryme.com.br")
    link = f"{base_url}/portal/convite?token={token}"

    logger.info(
        f"CONVITE GERADO\n"
        f"Prestador: {nome_prestador}\n"
        f"Email: {email}\n"
        f"Tipo: {tipo}\n"
        f"Link: {link}\n"
        f'Expira em: {getattr(settings, "CONVITE_EXPIRACAO_HORAS", 48)}h'
    )

    return link
