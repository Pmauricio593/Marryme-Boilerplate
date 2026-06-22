import logging

from django.conf import settings
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view
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
from core.openapi import paginated_response_schema
from core.pagination import MarryMePagination

logger = logging.getLogger("marryme.contas")

PaginatedConviteResponse = paginated_response_schema(
    "PaginatedConviteResponse", ConviteAcessoSerializer
)
PaginatedMembroResponse = paginated_response_schema(
    "PaginatedMembroResponse", VinculoPrestadorSerializer
)


@extend_schema_view(
    get=extend_schema(
        tags=["Contas"],
        responses=PaginatedConviteResponse,
        summary="Lista convites do prestador",
    ),
    post=extend_schema(
        tags=["Contas"],
        request=EmitirConviteSerializer,
        responses={201: ConviteAcessoSerializer},
        summary="Emite convite de acesso ao portal",
    ),
)
class ConviteListCreateView(APIView):
    permission_classes = [IsCS]

    def get(self, request, prestador_id):
        prestador = get_object_or_404(Prestador, id=prestador_id)
        convites = (
            ConviteAcesso.objects.filter(prestador=prestador)
            .select_related("prestador", "criado_por")
            .order_by("-criado_em")
        )
        paginator = MarryMePagination()
        page = paginator.paginate_queryset(convites, request)
        serializer = ConviteAcessoSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, prestador_id):
        prestador = get_object_or_404(Prestador, id=prestador_id)
        serializer = EmitirConviteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            convite, token_raw = ConviteService().emitir(
                prestador=prestador,
                email=serializer.validated_data["email"],
                tipo=serializer.validated_data["tipo"],
                permissoes=serializer.validated_data.get("permissoes_portal"),
                criado_por=request.user,
            )
        except Exception as e:
            detail = getattr(e, "detail", str(e))
            if isinstance(detail, list):
                detail = detail[0]
            return Response({"erro": str(detail)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                **ConviteAcessoSerializer(convite).data,
                "link_portal": f"{settings.FRONTEND_URL}/portal/convite?token={token_raw}",
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    tags=["Contas"],
    request=None,
    responses=ConviteAcessoSerializer,
    summary="Reenvia convite pendente",
)
class ConviteReenviarView(APIView):
    permission_classes = [IsCS]

    def post(self, request, prestador_id, convite_id):
        prestador = get_object_or_404(Prestador, id=prestador_id)
        convite = get_object_or_404(ConviteAcesso, id=convite_id, prestador=prestador)

        try:
            novo_convite, token_raw = ConviteService().reenviar(convite, criado_por=request.user)
        except Exception as e:
            detail = getattr(e, "detail", str(e))
            if isinstance(detail, list):
                detail = detail[0]
            return Response({"erro": str(detail)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                **ConviteAcessoSerializer(novo_convite).data,
                "link_portal": f"{settings.FRONTEND_URL}/portal/convite?token={token_raw}",
            }
        )


@extend_schema(
    tags=["Contas"],
    request=None,
    responses={204: None},
    summary="Revoga convite pendente",
)
class ConviteRevogarView(APIView):
    permission_classes = [IsCS]

    def delete(self, request, prestador_id, convite_id):
        prestador = get_object_or_404(Prestador, id=prestador_id)
        convite = get_object_or_404(ConviteAcesso, id=convite_id, prestador=prestador)

        try:
            ConviteService().revogar(convite)
        except Exception as e:
            detail = getattr(e, "detail", str(e))
            if isinstance(detail, list):
                detail = detail[0]
            return Response({"erro": str(detail)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    tags=["Contas"],
    responses=PaginatedMembroResponse,
    summary="Lista membros com acesso ao portal",
)
class MembroListView(APIView):
    permission_classes = [IsCS]

    def get(self, request, prestador_id):
        prestador = get_object_or_404(Prestador, id=prestador_id)
        membros = MembroPortalService().listar_membros(prestador)
        paginator = MarryMePagination()
        page = paginator.paginate_queryset(membros, request)
        serializer = VinculoPrestadorSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


@extend_schema(
    tags=["Contas"],
    request=None,
    responses={204: None},
    summary="Revoga acesso de membro ao portal",
)
class MembroRevogarView(APIView):
    permission_classes = [IsCS]

    def delete(self, request, prestador_id, usuario_id):
        prestador = get_object_or_404(Prestador, id=prestador_id)

        try:
            MembroPortalService().revogar_membro(prestador, usuario_id)
        except ValueError as e:
            return Response({"erro": str(e)}, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)
