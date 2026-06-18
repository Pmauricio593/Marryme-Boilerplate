from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import Prestador


class PrestadorListSerializer(serializers.ModelSerializer):
    """Versão resumida para listagem no dashboard"""

    responsavel_nome = serializers.CharField(source="responsavel.get_full_name", read_only=True)

    class Meta:
        model = Prestador
        fields = [
            "id",
            "nome_artistico",
            "categoria",
            "fase",
            "cidade",
            "estado",
            "health_score",
            "health_status",
            "responsavel_nome",
            "atualizado_em",
        ]


class PrestadorSerializer(serializers.ModelSerializer):
    """Versão completa para detalhe do prestador"""

    responsavel_nome = serializers.CharField(source="responsavel.get_full_name", read_only=True)

    class Meta:
        model = Prestador
        fields = "__all__"
        read_only_fields = ["id", "criado_em", "atualizado_em", "health_score", "health_status"]

    def validate_whatsapp(self, value):
        digits = "".join(filter(str.isdigit, value))
        if len(digits) < 10 or len(digits) > 13:
            raise serializers.ValidationError("WhatsApp inválido.")
        return value

    def validate_estado(self, value):
        if len(value) != 2:
            raise serializers.ValidationError("Estado deve ter 2 letras (ex: SP).")
        return value.upper()


class PortalPrestadorSerializer(serializers.ModelSerializer):
    health_score_atual = serializers.SerializerMethodField()
    total_sessoes = serializers.SerializerMethodField()
    roteiros_aprovados = serializers.SerializerMethodField()

    class Meta:
        model = Prestador
        fields = [
            "id",
            "nome_artistico",
            "categoria",
            "fase",
            "cidade",
            "estado",
            "instagram",
            "health_score",
            "health_status",
            "health_score_atual",
            "total_sessoes",
            "roteiros_aprovados",
            "atualizado_em",
        ]
        read_only_fields = fields

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_health_score_atual(self, obj):
        from apps.campanhas.models import HealthScore

        hs = HealthScore.objects.filter(prestador=obj).order_by("-data_calculo").first()
        if not hs:
            return None
        return {
            "score": hs.score,
            "status": hs.status,
            "data": hs.data_calculo,
            "breakdown": {
                "cpm": hs.score_cpl,
                "hook_rate": hs.score_orcamento,
                "retencao": hs.score_leads,
                "ctr": hs.score_ctr,
            },
        }

    def get_total_sessoes(self, obj) -> int:
        return obj.sessoes_chat.filter(status__in=["ativa", "finalizada"]).count()

    def get_roteiros_aprovados(self, obj) -> int:
        return obj.roteiros.filter(aprovado=True).count()
