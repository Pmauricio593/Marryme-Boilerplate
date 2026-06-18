from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.contas.serializers import MarryMeTokenSerializer


@extend_schema(tags=["Auth"], summary="Login da equipe interna")
class MarryMeTokenView(TokenObtainPairView):
    """Login da equipe interna — retorna JWT com role e nivel_acesso."""

    serializer_class = MarryMeTokenSerializer
