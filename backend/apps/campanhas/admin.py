from django.contrib import admin
from .models import MetricaMeta, HealthScore, RelatorioIA, ConfiguracaoMeta


@admin.register(MetricaMeta)
class MetricaMetaAdmin(admin.ModelAdmin):
    list_display = ['prestador', 'campanha_nome',
                    'data_referencia', 'leads', 'gasto', 'cpl']
    list_filter = ['data_referencia']


@admin.register(HealthScore)
class HealthScoreAdmin(admin.ModelAdmin):
    list_display = ['prestador', 'score', 'status', 'data_calculo']
    list_filter = ['status', 'data_calculo']


@admin.register(RelatorioIA)
class RelatorioIAAdmin(admin.ModelAdmin):
    list_display = ['prestador', 'periodo_inicio',
                    'periodo_fim', 'health_score', 'gerado_em']


@admin.register(ConfiguracaoMeta)
class ConfiguracaoMetaAdmin(admin.ModelAdmin):
    list_display = ['chave', 'atualizado_em']
