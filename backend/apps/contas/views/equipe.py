from rest_framework_simplejwt.views import TokenObtainPairView

from apps.contas.serializers import MarryMeTokenSerializer


class MarryMeTokenView(TokenObtainPairView):
    """Login da equipe interna — retorna JWT com role e nivel_acesso."""

    serializer_class = MarryMeTokenSerializer
