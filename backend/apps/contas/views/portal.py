import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.contas.serializers import AceitarConviteSerializer, PortalLoginSerializer
from apps.contas.services.autenticacao_portal_service import AutenticacaoPortalService
from apps.contas.services.convite_service import ConviteService

logger = logging.getLogger('marryme.contas')


class ValidarConviteView(APIView):
    permission_classes = []

    def get(self, request):
        token = request.query_params.get('token', '').strip()
        if not token:
            return Response(
                {'erro': 'Token é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        dto = ConviteService().validar(token)
        return Response({
            'valido': dto.valido,
            'email_mascarado': dto.email_mascarado,
            'tipo': dto.tipo,
            'prestador_nome': dto.prestador_nome,
            'expira_em': dto.expira_em,
            'erro': dto.erro,
        })


class AceitarConviteView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = AceitarConviteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            resultado = ConviteService().aceitar(
                token=serializer.validated_data['token'],
                senha=serializer.validated_data['senha'],
                nome=serializer.validated_data.get('nome'),
            )
        except Exception as e:
            detail = getattr(e, 'detail', str(e))
            if isinstance(detail, list):
                detail = detail[0]
            return Response({'erro': str(detail)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(resultado, status=status.HTTP_201_CREATED)


class PortalLoginView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = PortalLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            resultado = AutenticacaoPortalService().login(
                email=serializer.validated_data['email'],
                senha=serializer.validated_data['senha'],
            )
        except Exception as e:
            detail = getattr(e, 'detail', str(e))
            if isinstance(detail, list):
                detail = detail[0]
            return Response({'erro': str(detail)}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(resultado)
