from django.contrib import admin
from .models import ChatSessao, ChatMensagem, RoteiroFinal


@admin.register(ChatSessao)
class ChatSessaoAdmin(admin.ModelAdmin):
    list_display = ['prestador', 'titulo', 'tipo', 'status', 'atualizado_em']
    list_filter = ['tipo', 'status']


@admin.register(ChatMensagem)
class ChatMensagemAdmin(admin.ModelAdmin):
    list_display = ['sessao', 'role', 'criado_em']
    list_filter = ['role']


@admin.register(RoteiroFinal)
class RoteiroFinalAdmin(admin.ModelAdmin):
    list_display = ['prestador', 'tipo', 'aprovado', 'criado_em']
    list_filter = ['tipo', 'aprovado']
