from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.contas.constants import PERMISSOES_ASSESSORIA_DEFAULT, ROLES_PORTAL, role_para_nivel
from apps.contas.models import ConviteAcesso, VinculoPrestador


class MarryMeTokenSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["nivel_acesso"] = role_para_nivel(user.role)
        token["nome"] = user.get_full_name() or user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        if self.user.role in ROLES_PORTAL:
            raise ValidationError("Use o login do portal para acessar.")

        data["role"] = self.user.role
        data["nivel_acesso"] = role_para_nivel(self.user.role)
        data["nome"] = self.user.get_full_name() or self.user.username
        return data


class ConviteAcessoSerializer(serializers.ModelSerializer):
    prestador_nome = serializers.CharField(source="prestador.nome_artistico", read_only=True)
    criado_por_nome = serializers.CharField(source="criado_por.get_full_name", read_only=True)

    class Meta:
        model = ConviteAcesso
        fields = [
            "id",
            "prestador",
            "prestador_nome",
            "email",
            "tipo",
            "permissoes_portal",
            "status",
            "criado_por",
            "criado_por_nome",
            "criado_em",
            "expira_em",
            "usado_em",
        ]
        read_only_fields = [
            "id",
            "status",
            "criado_em",
            "expira_em",
            "usado_em",
            "prestador_nome",
            "criado_por_nome",
        ]


class EmitirConviteSerializer(serializers.Serializer):
    email = serializers.EmailField()
    tipo = serializers.ChoiceField(choices=["titular", "assessoria"])
    permissoes_portal = serializers.JSONField(required=False, default=PERMISSOES_ASSESSORIA_DEFAULT)


class AceitarConviteSerializer(serializers.Serializer):
    token = serializers.CharField()
    senha = serializers.CharField(min_length=8)
    nome = serializers.CharField(required=False, allow_blank=True)


class PortalLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    senha = serializers.CharField()


class VinculoPrestadorSerializer(serializers.ModelSerializer):
    usuario_email = serializers.EmailField(source="usuario.email", read_only=True)
    usuario_nome = serializers.CharField(source="usuario.get_full_name", read_only=True)
    prestador_nome = serializers.CharField(source="prestador.nome_artistico", read_only=True)

    class Meta:
        model = VinculoPrestador
        fields = [
            "id",
            "usuario",
            "usuario_email",
            "usuario_nome",
            "prestador",
            "prestador_nome",
            "tipo",
            "permissoes_portal",
            "ativo",
            "criado_em",
        ]
        read_only_fields = fields
