import logging
from django.conf import settings

logger = logging.getLogger('marryme.prestadores')


def enviar_convite_acesso(usuario, token: str, nome_prestador: str):
    """
    Envia link de primeiro acesso para o prestador.
    Por enquanto loga o link — integração de email/WhatsApp vem depois.
    """
    base_url = getattr(settings, 'FRONTEND_URL', 'https://marryme.com.br')
    link = f"{base_url}/portal/primeiro-acesso?token={token}"

    # Log do link para uso imediato (antes de integrar envio real)
    logger.info(
        f"CONVITE GERADO\n"
        f"Prestador: {nome_prestador}\n"
        f"Email: {usuario.email}\n"
        f"Link: {link}\n"
        f"Expira em: 48h"
    )

    # TODO: integrar WhatsApp Business API
    # TODO: integrar serviço de email (SendGrid, Resend)

    return link
