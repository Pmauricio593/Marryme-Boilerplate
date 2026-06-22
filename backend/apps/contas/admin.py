from django.contrib import admin

from apps.contas.models import ConviteAcesso, VinculoPrestador


@admin.register(ConviteAcesso)
class ConviteAcessoAdmin(admin.ModelAdmin):
    list_display = ["email", "prestador", "tipo", "status", "expira_em", "criado_em"]
    list_filter = ["tipo", "status"]
    search_fields = ["email", "prestador__nome_artistico"]
    autocomplete_fields = ["prestador", "criado_por", "usuario_criado"]
    readonly_fields = ["token_hash", "criado_em", "usado_em"]


@admin.register(VinculoPrestador)
class VinculoPrestadorAdmin(admin.ModelAdmin):
    list_display = ["usuario", "prestador", "tipo", "ativo", "criado_em"]
    list_filter = ["tipo", "ativo"]
    search_fields = ["usuario__email", "prestador__nome_artistico"]
    autocomplete_fields = ["usuario", "prestador"]
