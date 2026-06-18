from rest_framework import serializers

from .models import ChatMensagem, ChatSessao, RoteiroFinal


class ChatMensagemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMensagem
        fields = "__all__"
        read_only_fields = ["id", "criado_em"]


class ChatSessaoSerializer(serializers.ModelSerializer):
    mensagens = ChatMensagemSerializer(many=True, read_only=True)
    total_mensagens = serializers.SerializerMethodField()

    class Meta:
        model = ChatSessao
        fields = "__all__"
        read_only_fields = ["id", "criado_em", "atualizado_em", "tokens_usados"]

    def get_total_mensagens(self, obj) -> int:
        return obj.mensagens.count()


class ChatSessaoListSerializer(serializers.ModelSerializer):
    """Versão resumida para listar sessões no sidebar do chat"""

    total_mensagens = serializers.SerializerMethodField()

    class Meta:
        model = ChatSessao
        fields = ["id", "titulo", "tipo", "status", "total_mensagens", "atualizado_em"]

    def get_total_mensagens(self, obj) -> int:
        return obj.mensagens.count()


class RoteiroFinalSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoteiroFinal
        fields = "__all__"
        read_only_fields = ["id", "criado_em"]
