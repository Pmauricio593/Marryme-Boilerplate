from django.contrib import admin
from .models import Prestador, Usuario


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'is_active']
    list_filter = ['role', 'is_active']


@admin.register(Prestador)
class PrestadorAdmin(admin.ModelAdmin):
    list_display = ['nome_artistico', 'categoria',
                    'fase', 'cidade', 'health_score', 'health_status']
    list_filter = ['categoria', 'fase', 'estado']
    search_fields = ['nome_artistico', 'nome_completo', 'instagram']
