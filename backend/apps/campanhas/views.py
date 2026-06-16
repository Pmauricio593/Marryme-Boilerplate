import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import MetricaMeta, HealthScore, RelatorioIA
from .serializers import (
    MetricaMetaSerializer,
    HealthScoreSerializer,
    RelatorioIASerializer,
)
from core.permissions import IsCS

logger = logging.getLogger('marryme.campanhas')


class MetricaMetaViewSet(viewsets.ReadOnlyModelViewSet):
    """Métricas brutas do Meta Ads por prestador."""
    serializer_class = MetricaMetaSerializer
    permission_classes = [IsCS]

    def get_queryset(self):
        prestador_id = self.request.query_params.get('prestador')
        if prestador_id:
            return MetricaMeta.objects.filter(
                prestador_id=prestador_id
            ).order_by('-data_referencia')
        return MetricaMeta.objects.all()


class HealthScoreViewSet(viewsets.ReadOnlyModelViewSet):
    """Health scores calculados por prestador."""
    serializer_class = HealthScoreSerializer
    permission_classes = [IsCS]

    def get_queryset(self):
        prestador_id = self.request.query_params.get('prestador')
        if prestador_id:
            return HealthScore.objects.filter(
                prestador_id=prestador_id
            ).order_by('-data_calculo')
        return HealthScore.objects.all()

    @action(detail=False, methods=['get'], url_path='ultimo')
    def ultimo(self, request):
        """Retorna o health score mais recente de um prestador."""
        prestador_id = request.query_params.get('prestador')
        if not prestador_id:
            return Response(
                {'erro': 'Parâmetro prestador é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        hs = HealthScore.objects.filter(
            prestador_id=prestador_id
        ).order_by('-data_calculo').first()

        if not hs:
            return Response(
                {'erro': 'Nenhum health score encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(HealthScoreSerializer(hs).data)


class RelatorioIAViewSet(viewsets.ModelViewSet):
    """Relatórios de análise IA por prestador."""
    serializer_class = RelatorioIASerializer
    permission_classes = [IsCS]

    def get_queryset(self):
        prestador_id = self.request.query_params.get('prestador')
        if prestador_id:
            return RelatorioIA.objects.filter(
                prestador_id=prestador_id
            ).order_by('-gerado_em')
        return RelatorioIA.objects.all()

    @action(detail=True, methods=['post'], url_path='gerar-analise')
    def gerar_analise(self, request, pk=None):
        """Gera análise IA do relatório via Claude em background."""
        relatorio = self.get_object()
        from apps.roteiros.tasks import gerar_analise_estrategica
        gerar_analise_estrategica.delay(str(relatorio.prestador_id))
        return Response({'status': 'enfileirado'})
