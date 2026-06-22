from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.contas.models import ConviteAcesso, VinculoPrestador
from apps.campanhas.models import HealthScore

from .models import Prestador, Usuario


class ConviteAcessoInline(admin.TabularInline):
    model = ConviteAcesso
    extra = 0
    can_delete = False
    show_change_link = True
    readonly_fields = ["email", "tipo", "status", "expira_em", "criado_em"]
    fields = readonly_fields

    def has_add_permission(self, request, obj=None):
        return False


class VinculoPrestadorInline(admin.TabularInline):
    model = VinculoPrestador
    extra = 0
    can_delete = False
    show_change_link = True
    readonly_fields = ["usuario", "tipo", "ativo", "criado_em"]
    fields = readonly_fields

    def has_add_permission(self, request, obj=None):
        return False


class HealthScoreInline(admin.TabularInline):
    model = HealthScore
    extra = 0
    can_delete = False
    max_num = 5
    ordering = ["-data_calculo"]
    readonly_fields = ["data_calculo", "score", "status", "cpl_real", "leads_real"]
    fields = readonly_fields

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Usuario)
class UsuarioAdmin(DjangoUserAdmin):
    list_display = ["username", "email", "role", "is_staff", "is_active"]
    list_filter = ["role", "is_staff", "is_active", "is_superuser"]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering = ["email"]

    fieldsets = DjangoUserAdmin.fieldsets + (
        ("MarryMe", {"fields": ("role",)}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ("MarryMe", {"fields": ("role",)}),
    )


@admin.register(Prestador)
class PrestadorAdmin(admin.ModelAdmin):
    list_display = [
        "nome_artistico",
        "categoria",
        "fase",
        "cidade",
        "health_score",
        "health_status",
        "responsavel",
    ]
    list_filter = ["categoria", "fase", "estado"]
    search_fields = ["nome_artistico", "nome_completo", "instagram", "email"]
    readonly_fields = [
        "health_score",
        "health_status",
        "meta_ultima_sync",
        "criado_em",
        "atualizado_em",
    ]
    autocomplete_fields = ["responsavel"]
    inlines = [HealthScoreInline, VinculoPrestadorInline, ConviteAcessoInline]
