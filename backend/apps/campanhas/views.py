import logging

from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.openapi import StatusEnfileiradoResponse
from core.permissions import IsCS

from .models import HealthScore, MetricaMeta, RelatorioIA
from .serializers import (
    HealthScoreSerializer,
    MetricaMetaSerializer,
    RelatorioIASerializer,
)

logger = logging.getLogger("marryme.campanhas")


@extend_schema_view(
    list=extend_schema(tags=["Campanhas"]),
    retrieve=extend_schema(tags=["Campanhas"]),
)
class MetricaMetaViewSet(viewsets.ReadOnlyModelViewSet):
    """Métricas brutas do Meta Ads por prestador."""

    serializer_class = MetricaMetaSerializer
    permission_classes = [IsCS]

    def get_queryset(self):
        prestador_id = self.request.query_params.get("prestador")
        qs = MetricaMeta.objects.select_related("prestador")
        if prestador_id:
            return qs.filter(prestador_id=prestador_id).order_by("-data_referencia")
        return qs.all()


@extend_schema_view(
    list=extend_schema(tags=["Campanhas"]),
    retrieve=extend_schema(tags=["Campanhas"]),
)
class HealthScoreViewSet(viewsets.ReadOnlyModelViewSet):
    """Health scores calculados por prestador."""

    serializer_class = HealthScoreSerializer
    permission_classes = [IsCS]

    def get_queryset(self):
        prestador_id = self.request.query_params.get("prestador")
        qs = HealthScore.objects.select_related("prestador")
        if prestador_id:
            return qs.filter(prestador_id=prestador_id).order_by("-data_calculo")
        return qs.all()

    @extend_schema(
        tags=["Campanhas"],
        parameters=[
            OpenApiParameter(
                name="prestador",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=True,
            )
        ],
        responses=HealthScoreSerializer,
        summary="Health score mais recente do prestador",
    )
    @action(detail=False, methods=["get"], url_path="ultimo")
    def ultimo(self, request):
        """Retorna o health score mais recente de um prestador."""
        prestador_id = request.query_params.get("prestador")
        if not prestador_id:
            return Response(
                {"erro": "Parâmetro prestador é obrigatório."}, status=status.HTTP_400_BAD_REQUEST
            )
        hs = HealthScore.objects.filter(prestador_id=prestador_id).order_by("-data_calculo").first()

        if not hs:
            return Response(
                {"erro": "Nenhum health score encontrado."}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(HealthScoreSerializer(hs).data)


@extend_schema_view(
    list=extend_schema(tags=["Campanhas"]),
    create=extend_schema(tags=["Campanhas"]),
    retrieve=extend_schema(tags=["Campanhas"]),
    update=extend_schema(tags=["Campanhas"]),
    partial_update=extend_schema(tags=["Campanhas"]),
    destroy=extend_schema(tags=["Campanhas"]),
)
class RelatorioIAViewSet(viewsets.ModelViewSet):
    """Relatórios de análise IA por prestador."""

    serializer_class = RelatorioIASerializer
    permission_classes = [IsCS]

    def get_queryset(self):
        prestador_id = self.request.query_params.get("prestador")
        qs = RelatorioIA.objects.select_related("prestador")
        if prestador_id:
            return qs.filter(prestador_id=prestador_id).order_by("-gerado_em")
        return qs.all()

    @extend_schema(
        tags=["Campanhas"],
        responses=StatusEnfileiradoResponse,
        summary="Enfileira geração de análise IA via Claude",
    )
    @action(detail=True, methods=["post"], url_path="gerar-analise")
    def gerar_analise(self, request, pk=None):
        """Gera análise IA do relatório via Claude em background."""
        relatorio = self.get_object()
        from apps.campanhas.tasks import gerar_analise_relatorio

        gerar_analise_relatorio.delay(str(relatorio.id))
        return Response({"status": "enfileirado", "relatorio_id": str(relatorio.id)})
