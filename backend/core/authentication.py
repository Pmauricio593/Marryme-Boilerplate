import logging

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

logger = logging.getLogger("marryme.auth")


class MarryMeJWTAuthentication(JWTAuthentication):
    """
    Autenticação JWT customizada da MarryMe.
    Loga tentativas inválidas e enriquece o usuário com role.
    """

    def authenticate(self, request):
        try:
            result = super().authenticate(request)
            if result:
                user, token = result
                logger.info(f"Auth OK: {user.username} ({user.role})")
            return result
        except (InvalidToken, TokenError) as e:
            logger.warning(f"Auth falhou: {str(e)}")
            raise
