from django.contrib import admin

from core.admin_utils import format_html_list, format_json_block

from .models import ConfiguracaoMeta, HealthScore, MetricaMeta, RelatorioIA


@admin.register(MetricaMeta)
class MetricaMetaAdmin(admin.ModelAdmin):
    list_display = ["prestador", "campanha_nome", "data_referencia", "leads", "gasto", "cpl"]
    list_filter = ["data_referencia"]
    search_fields = ["prestador__nome_artistico", "campanha_nome"]
    autocomplete_fields = ["prestador"]
    readonly_fields = ["criado_em"]


@admin.register(HealthScore)
class HealthScoreAdmin(admin.ModelAdmin):
    list_display = ["prestador", "score", "status", "data_calculo"]
    list_filter = ["status", "data_calculo"]
    search_fields = ["prestador__nome_artistico"]
    autocomplete_fields = ["prestador"]
    readonly_fields = ["criado_em"]


@admin.register(RelatorioIA)
class RelatorioIAAdmin(admin.ModelAdmin):
    list_display = [
        "prestador",
        "periodo_inicio",
        "periodo_fim",
        "health_score",
        "tem_pauta",
        "gerado_em",
    ]
    list_filter = ["gerado_em"]
    search_fields = ["prestador__nome_artistico"]
    autocomplete_fields = ["prestador"]
    readonly_fields = [
        "id",
        "gerado_em",
        "tokens_usados",
        "dados_json",
        "resumo_analise",
        "resumo_pauta",
        "resumo_acoes",
        "resumo_metricas",
    ]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "prestador",
                    "periodo_inicio",
                    "periodo_fim",
                    "health_score",
                    "tokens_usados",
                    "gerado_em",
                )
            },
        ),
        (
            "Conteúdo para CS",
            {"fields": ("resumo_analise", "resumo_pauta", "resumo_acoes", "resumo_metricas")},
        ),
        ("JSON bruto", {"fields": ("dados_json",), "classes": ("collapse",)}),
    )

    @admin.display(boolean=True, description="Pauta")
    def tem_pauta(self, obj):
        return bool((obj.dados_json or {}).get("pauta_reuniao"))

    @admin.display(description="Análise")
    def resumo_analise(self, obj):
        analise = (obj.dados_json or {}).get("analise")
        return analise or "—"

    @admin.display(description="Pauta de reunião")
    def resumo_pauta(self, obj):
        return format_html_list((obj.dados_json or {}).get("pauta_reuniao") or [])

    @admin.display(description="Ações CS")
    def resumo_acoes(self, obj):
        return format_html_list((obj.dados_json or {}).get("acoes_cs") or [])

    @admin.display(description="Métricas resumo")
    def resumo_metricas(self, obj):
        return format_json_block((obj.dados_json or {}).get("metricas_resumo"))


@admin.register(ConfiguracaoMeta)
class ConfiguracaoMetaAdmin(admin.ModelAdmin):
    list_display = ["chave", "valor_resumo", "atualizado_em"]
    search_fields = ["chave"]
    readonly_fields = ["atualizado_em", "valor_resumo"]

    @admin.display(description="Valor")
    def valor_resumo(self, obj):
        chave = obj.chave.lower()
        if any(termo in chave for termo in ("token", "secret", "key", "password")):
            if len(obj.valor) <= 8:
                return "••••••••"
            return f"{obj.valor[:4]}…{obj.valor[-4:]}"
        if len(obj.valor) > 80:
            return f"{obj.valor[:80]}…"
        return obj.valor

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if obj and any(
            termo in obj.chave.lower() for termo in ("token", "secret", "key", "password")
        ):
            fields.append("valor")
        return fields
