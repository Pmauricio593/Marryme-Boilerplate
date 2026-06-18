import logging

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.contas.permissions import IsAdmin, IsCS, IsEquipeOuPortalVinculado
from apps.contas.utils import resolver_prestador_portal
from core.openapi import (
    AtualizarFaseRequest,
    PortalCampanhasResponse,
    PortalRoteirosResponse,
    StatusEnfileiradoResponse,
)

from .models import Prestador
from .serializers import (
    PortalPrestadorSerializer,
    PrestadorListSerializer,
    PrestadorSerializer,
)
from .services import PrestadorService

logger = logging.getLogger("marryme.prestadores")


@extend_schema_view(
    list=extend_schema(tags=["Prestadores"]),
    create=extend_schema(tags=["Prestadores"]),
    retrieve=extend_schema(tags=["Prestadores"]),
    update=extend_schema(tags=["Prestadores"]),
    partial_update=extend_schema(tags=["Prestadores"]),
    destroy=extend_schema(tags=["Prestadores"]),
)
class PrestadorViewSet(viewsets.ModelViewSet):
    queryset = Prestador.objects.select_related("responsavel").all()

    def get_serializer_class(self):
        if self.action == "list":
            return PrestadorListSerializer
        return PrestadorSerializer

    def get_permissions(self):
        if self.action == "destroy":
            return [IsAdmin()]
        return [IsCS()]

    def get_queryset(self):
        queryset = super().get_queryset()
        fase = self.request.query_params.get("fase")
        categoria = self.request.query_params.get("categoria")
        busca = self.request.query_params.get("busca")

        if fase:
            queryset = queryset.filter(fase=fase)
        if categoria:
            queryset = queryset.filter(categoria=categoria)
        if busca:
            queryset = queryset.filter(nome_artistico__icontains=busca) | queryset.filter(
                cidade__icontains=busca
            )
        return queryset

    def perform_create(self, serializer):
        serializer.save(responsavel=self.request.user)
        logger.info(f"Prestador criado: {serializer.instance}")

    @extend_schema(
        tags=["Prestadores"],
        request=AtualizarFaseRequest,
        responses=PrestadorSerializer,
        summary="Atualiza fase do pipeline",
    )
    @action(detail=True, methods=["post"], url_path="atualizar-fase")
    def atualizar_fase(self, request, pk=None):
        prestador = self.get_object()
        nova_fase = request.data.get("fase")

        if not nova_fase:
            return Response(
                {"erro": "Campo fase é obrigatório."}, status=status.HTTP_400_BAD_REQUEST
            )

        if nova_fase not in dict(Prestador.FASES):
            return Response(
                {"erro": f"Fase inválida: {nova_fase}"}, status=status.HTTP_400_BAD_REQUEST
            )

        prestador = PrestadorService().atualizar_fase(prestador, nova_fase)
        return Response(PrestadorSerializer(prestador).data)

    @extend_schema(
        tags=["Prestadores"],
        responses=StatusEnfileiradoResponse,
        summary="Enfileira sync Meta Ads do prestador",
    )
    @action(detail=True, methods=["post"], url_path="sync-meta")
    def sync_meta(self, request, pk=None):
        prestador = self.get_object()

        if not prestador.meta_ad_account_id:
            return Response(
                {"erro": "Conta Meta não configurada."}, status=status.HTTP_400_BAD_REQUEST
            )

        from apps.campanhas.tasks import sincronizar_meta_ads

        sincronizar_meta_ads.delay(str(prestador.id))

        logger.info(f"Sync Meta enfileirado: {prestador}")
        return Response({"status": "enfileirado"})

    @extend_schema(
        tags=["Prestadores"],
        responses=StatusEnfileiradoResponse,
        summary="Enfileira sync Meta Ads de todos os clientes",
    )
    @action(detail=False, methods=["post"], url_path="sync-todos")
    def sync_todos(self, request, pk=None):
        from apps.campanhas.tasks import sincronizar_todos_clientes

        sincronizar_todos_clientes.delay()
        return Response({"status": "enfileirado"})


@extend_schema_view(
    list=extend_schema(
        tags=["Portal"],
        responses=PortalPrestadorSerializer,
        summary="Perfil do prestador vinculado ao usuário",
    )
)
class PortalPerfilView(viewsets.ViewSet):
    permission_classes = [IsEquipeOuPortalVinculado]

    def list(self, request):
        prestador, _ = resolver_prestador_portal(request, permissao="perfil")
        return Response(PortalPrestadorSerializer(prestador).data)


@extend_schema_view(
    list=extend_schema(
        tags=["Portal"],
        responses=PortalCampanhasResponse,
        summary="Health score e métricas recentes do prestador vinculado",
    )
)
class PortalCampanhasView(viewsets.ViewSet):
    permission_classes = [IsEquipeOuPortalVinculado]

    def list(self, request):
        from apps.campanhas.models import HealthScore, MetricaMeta
        from apps.campanhas.serializers import HealthScoreSerializer, MetricaMetaSerializer

        prestador, _ = resolver_prestador_portal(request, permissao="campanhas")

        hs = HealthScore.objects.filter(prestador=prestador).order_by("-data_calculo").first()

        metricas = MetricaMeta.objects.filter(prestador=prestador).order_by("-data_referencia")[:30]

        return Response(
            {
                "health_score": HealthScoreSerializer(hs).data if hs else None,
                "metricas": MetricaMetaSerializer(metricas, many=True).data,
            }
        )


@extend_schema_view(
    list=extend_schema(
        tags=["Portal"],
        responses=PortalRoteirosResponse,
        summary="Roteiros aprovados e sessões recentes do prestador vinculado",
    )
)
class PortalRoteirosView(viewsets.ViewSet):
    permission_classes = [IsEquipeOuPortalVinculado]
    permissao_portal = "roteiros"

    def list(self, request):
        from apps.roteiros.models import ChatSessao, RoteiroFinal
        from apps.roteiros.serializers import ChatSessaoListSerializer, RoteiroFinalSerializer

        prestador, _ = resolver_prestador_portal(request, permissao="roteiros")

        roteiros = RoteiroFinal.objects.filter(prestador=prestador, aprovado=True).order_by(
            "-criado_em"
        )

        sessoes = ChatSessao.objects.filter(prestador=prestador, status="finalizada").order_by(
            "-atualizado_em"
        )[:5]

        return Response(
            {
                "roteiros": RoteiroFinalSerializer(roteiros, many=True).data,
                "sessoes_recentes": ChatSessaoListSerializer(sessoes, many=True).data,
            }
        )
