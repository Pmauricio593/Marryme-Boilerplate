from rest_framework import serializers
from .models import MetricaMeta, HealthScore, RelatorioIA


class MetricaMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetricaMeta
        fields = '__all__'
        read_only_fields = ['id', 'criado_em']


class HealthScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthScore
        fields = '__all__'
        read_only_fields = ['id', 'criado_em']


class HealthScoreResumoSerializer(serializers.ModelSerializer):
    """Versão resumida para exibir no card do prestador"""
    class Meta:
        model = HealthScore
        fields = ['score', 'status', 'data_calculo']


class RelatorioIASerializer(serializers.ModelSerializer):
    class Meta:
        model = RelatorioIA
        fields = '__all__'
        read_only_fields = ['id', 'gerado_em', 'tokens_usados']
