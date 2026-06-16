import logging

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.contas.models import ConviteAcesso
from apps.contas.permissions import IsCS
from apps.contas.serializers import (
    ConviteAcessoSerializer,
    EmitirConviteSerializer,
    VinculoPrestadorSerializer,
)
from apps.contas.services.convite_service import ConviteService
from apps.contas.services.membro_portal_service import MembroPortalService
from apps.prestadores.models import Prestador

logger = logging.getLogger('marryme.contas')


class ConviteListCreateView(APIView):
    permission_classes = [IsCS]

    def get(self, request, prestador_id):
        prestador = get_object_or_404(Prestador, id=prestador_id)
        convites = ConviteAcesso.objects.filter(prestador=prestador)
        return Response(ConviteAcessoSerializer(convites, many=True).data)

    def post(self, request, prestador_id):
        prestador = get_object_or_404(Prestador, id=prestador_id)
        serializer = EmitirConviteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            convite, _ = ConviteService().emitir(
                prestador=prestador,
                email=serializer.validated_data['email'],
                tipo=serializer.validated_data['tipo'],
                permissoes=serializer.validated_data.get('permissoes_portal'),
                criado_por=request.user,
            )
        except Exception as e:
            detail = getattr(e, 'detail', str(e))
            if isinstance(detail, list):
                detail = detail[0]
            return Response({'erro': str(detail)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            ConviteAcessoSerializer(convite).data,
            status=status.HTTP_201_CREATED,
        )


class ConviteReenviarView(APIView):
    permission_classes = [IsCS]

    def post(self, request, prestador_id, convite_id):
        prestador = get_object_or_404(Prestador, id=prestador_id)
        convite = get_object_or_404(
            ConviteAcesso, id=convite_id, prestador=prestador
        )

        try:
            novo_convite, _ = ConviteService().reenviar(convite, criado_por=request.user)
        except Exception as e:
            detail = getattr(e, 'detail', str(e))
            if isinstance(detail, list):
                detail = detail[0]
            return Response({'erro': str(detail)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ConviteAcessoSerializer(novo_convite).data)


class ConviteRevogarView(APIView):
    permission_classes = [IsCS]

    def delete(self, request, prestador_id, convite_id):
        prestador = get_object_or_404(Prestador, id=prestador_id)
        convite = get_object_or_404(
            ConviteAcesso, id=convite_id, prestador=prestador
        )

        try:
            ConviteService().revogar(convite)
        except Exception as e:
            detail = getattr(e, 'detail', str(e))
            if isinstance(detail, list):
                detail = detail[0]
            return Response({'erro': str(detail)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)


class MembroListView(APIView):
    permission_classes = [IsCS]

    def get(self, request, prestador_id):
        prestador = get_object_or_404(Prestador, id=prestador_id)
        membros = MembroPortalService().listar_membros(prestador)
        return Response(VinculoPrestadorSerializer(membros, many=True).data)


class MembroRevogarView(APIView):
    permission_classes = [IsCS]

    def delete(self, request, prestador_id, usuario_id):
        prestador = get_object_or_404(Prestador, id=prestador_id)

        try:
            MembroPortalService().revogar_membro(prestador, usuario_id)
        except ValueError as e:
            return Response({'erro': str(e)}, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)
