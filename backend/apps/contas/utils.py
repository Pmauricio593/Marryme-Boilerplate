from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from apps.contas.constants import ROLES_PORTAL
from apps.contas.permissions import (
    get_vinculo_ativo,
    tem_role_minimo,
    usuario_tem_permissao_portal,
)
from apps.prestadores.models import Prestador


def resolver_prestador_portal(request, permissao: str | None = None):
    user = request.user

    if tem_role_minimo(user, 'cs'):
        prestador_id = request.query_params.get('prestador_id')
        if not prestador_id:
            raise ValidationError('Parâmetro prestador_id é obrigatório.')
        prestador = get_object_or_404(Prestador, id=prestador_id)
        return prestador, None

    if user.role not in ROLES_PORTAL:
        raise PermissionDenied('Acesso negado.')

    vinculo = get_vinculo_ativo(user)
    if not vinculo:
        raise NotFound('Nenhum prestador vinculado.')

    if permissao and not usuario_tem_permissao_portal(user, vinculo, permissao):
        raise PermissionDenied(f'Sem permissão para: {permissao}.')

    return vinculo.prestador, vinculo
