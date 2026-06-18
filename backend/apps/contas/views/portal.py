import logging

from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.contas.serializers import AceitarConviteSerializer, PortalLoginSerializer
from apps.contas.services.autenticacao_portal_service import AutenticacaoPortalService
from apps.contas.services.convite_service import ConviteService

logger = logging.getLogger("marryme.contas")

ValidarConviteResponse = inline_serializer(
    name="ValidarConviteResponse",
    fields={
        "valido": serializers.BooleanField(),
        "email_mascarado": serializers.CharField(allow_null=True),
        "tipo": serializers.CharField(allow_null=True),
        "prestador_nome": serializers.CharField(allow_null=True),
        "expira_em": serializers.DateTimeField(allow_null=True),
        "erro": serializers.CharField(allow_null=True),
    },
)

PortalLoginResponse = inline_serializer(
    name="PortalLoginResponse",
    fields={
        "access": serializers.CharField(),
        "refresh": serializers.CharField(),
        "role": serializers.CharField(),
        "nivel_acesso": serializers.CharField(),
        "nome": serializers.CharField(),
        "prestador_id": serializers.UUIDField(required=False),
        "permissoes": serializers.JSONField(required=False),
    },
)


@extend_schema(
    tags=["Portal"],
    parameters=[
        OpenApiParameter(
            name="token",
            type=str,
            location=OpenApiParameter.QUERY,
            required=True,
        )
    ],
    responses=ValidarConviteResponse,
    summary="Valida token de convite antes do cadastro",
)
class ValidarConviteView(APIView):
    permission_classes = []

    def get(self, request):
        token = request.query_params.get("token", "").strip()
        if not token:
            return Response(
                {"erro": "Token é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        dto = ConviteService().validar(token)
        return Response(
            {
                "valido": dto.valido,
                "email_mascarado": dto.email_mascarado,
                "tipo": dto.tipo,
                "prestador_nome": dto.prestador_nome,
                "expira_em": dto.expira_em,
                "erro": dto.erro,
            }
        )


@extend_schema(
    tags=["Portal"],
    request=AceitarConviteSerializer,
    responses={201: PortalLoginResponse},
    summary="Aceita convite e cria usuário do portal",
)
class AceitarConviteView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = AceitarConviteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            resultado = ConviteService().aceitar(
                token=serializer.validated_data["token"],
                senha=serializer.validated_data["senha"],
                nome=serializer.validated_data.get("nome"),
            )
        except Exception as e:
            detail = getattr(e, "detail", str(e))
            if isinstance(detail, list):
                detail = detail[0]
            return Response({"erro": str(detail)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(resultado, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=["Portal"],
    request=PortalLoginSerializer,
    responses=PortalLoginResponse,
    summary="Login do portal (prestador ou assessoria)",
)
class PortalLoginView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = PortalLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            resultado = AutenticacaoPortalService().login(
                email=serializer.validated_data["email"],
                senha=serializer.validated_data["senha"],
            )
        except Exception as e:
            detail = getattr(e, "detail", str(e))
            if isinstance(detail, list):
                detail = detail[0]
            return Response({"erro": str(detail)}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(resultado)
