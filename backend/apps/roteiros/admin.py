from django.contrib import admin

from .models import ChatMensagem, ChatSessao, RoteiroFinal


class ChatMensagemInline(admin.TabularInline):
    model = ChatMensagem
    extra = 0
    can_delete = False
    max_num = 10
    ordering = ["criado_em"]
    readonly_fields = ["role", "conteudo_resumo", "criado_em"]
    fields = readonly_fields

    @admin.display(description="Conteúdo")
    def conteudo_resumo(self, obj):
        texto = obj.content or ""
        return texto if len(texto) <= 120 else f"{texto[:120]}…"

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ChatSessao)
class ChatSessaoAdmin(admin.ModelAdmin):
    list_display = ["prestador", "titulo", "tipo", "status", "atualizado_em"]
    list_filter = ["tipo", "status"]
    search_fields = ["prestador__nome_artistico", "titulo"]
    autocomplete_fields = ["prestador"]
    readonly_fields = ["criado_em", "atualizado_em", "tokens_usados"]
    inlines = [ChatMensagemInline]


@admin.register(ChatMensagem)
class ChatMensagemAdmin(admin.ModelAdmin):
    list_display = ["sessao", "role", "conteudo_resumo", "criado_em"]
    list_filter = ["role"]
    search_fields = ["sessao__prestador__nome_artistico", "content"]
    readonly_fields = ["criado_em"]

    @admin.display(description="Conteúdo")
    def conteudo_resumo(self, obj):
        texto = obj.content or ""
        return texto if len(texto) <= 80 else f"{texto[:80]}…"


@admin.register(RoteiroFinal)
class RoteiroFinalAdmin(admin.ModelAdmin):
    list_display = ["prestador", "tipo", "aprovado", "criado_em"]
    list_filter = ["tipo", "aprovado"]
    search_fields = ["prestador__nome_artistico", "tipo"]
    autocomplete_fields = ["prestador"]
    readonly_fields = ["criado_em"]
