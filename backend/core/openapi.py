"""Schemas reutilizáveis para documentação OpenAPI."""

from drf_spectacular.utils import inline_serializer
from rest_framework import serializers

MensagemChatRequest = inline_serializer(
    name="MensagemChatRequest",
    fields={
        "mensagem": serializers.CharField(),
        "arquivos": serializers.ListField(
            child=serializers.DictField(),
            required=False,
            default=list,
        ),
    },
)

MensagemChatResponse = inline_serializer(
    name="MensagemChatResponse",
    fields={"resposta": serializers.CharField()},
)

AtualizarFaseRequest = inline_serializer(
    name="AtualizarFaseRequest",
    fields={"fase": serializers.CharField()},
)

StatusEnfileiradoResponse = inline_serializer(
    name="StatusEnfileiradoResponse",
    fields={"status": serializers.CharField(default="enfileirado")},
)

StatusSimplesResponse = inline_serializer(
    name="StatusSimplesResponse",
    fields={"status": serializers.CharField()},
)

FinalizarSessaoRequest = inline_serializer(
    name="FinalizarSessaoRequest",
    fields={"roteiro_final": serializers.CharField(required=False, allow_blank=True)},
)

PortalCampanhasResponse = inline_serializer(
    name="PortalCampanhasResponse",
    fields={
        "health_score": serializers.JSONField(allow_null=True),
        "metricas": serializers.ListField(child=serializers.JSONField()),
    },
)

PortalRoteirosResponse = inline_serializer(
    name="PortalRoteirosResponse",
    fields={
        "roteiros": serializers.ListField(child=serializers.JSONField()),
        "sessoes_recentes": serializers.ListField(child=serializers.JSONField()),
    },
)


def paginated_response_schema(name: str, item_serializer=None):
    fields = {
        "total": serializers.IntegerField(),
        "paginas": serializers.IntegerField(),
        "pagina_atual": serializers.IntegerField(),
        "proxima": serializers.URLField(allow_null=True, required=False),
        "anterior": serializers.URLField(allow_null=True, required=False),
        "resultados": serializers.ListField(child=serializers.JSONField()),
    }
    if item_serializer is not None:
        fields["resultados"] = serializers.ListField(child=item_serializer())
    return inline_serializer(name=name, fields=fields)
