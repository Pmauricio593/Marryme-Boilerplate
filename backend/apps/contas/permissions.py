from rest_framework.permissions import BasePermission

from apps.contas.constants import ROLES_PORTAL, eh_equipe_interna
from apps.contas.models import VinculoPrestador

HIERARQUIA = ["dev", "sdr", "cs", "admin"]


def tem_role_minimo(usuario, role_minimo: str) -> bool:
    try:
        return HIERARQUIA.index(usuario.role) >= HIERARQUIA.index(role_minimo)
    except ValueError:
        return False


def usuario_tem_permissao_portal(usuario, vinculo: VinculoPrestador, permissao: str) -> bool:
    if vinculo.tipo == "titular":
        return True
    return bool(vinculo.permissoes_efetivas().get(permissao, False))


def get_vinculo_ativo(usuario, prestador_id=None):
    qs = VinculoPrestador.objects.filter(
        usuario=usuario,
        ativo=True,
    ).select_related("prestador")

    if prestador_id:
        return qs.filter(prestador_id=prestador_id).first()

    titular = qs.filter(tipo="titular").first()
    return titular or qs.first()


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "admin")


class IsEquipe(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and eh_equipe_interna(request.user.role)
        )


class IsCS(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and tem_role_minimo(request.user, "cs")
        )


class IsSDR(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and tem_role_minimo(request.user, "sdr")
        )


class IsPrestador(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.role == "prestador"
        )


class IsAssessoria(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.role == "assessoria"
        )


class IsPortalUsuario(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.role in ROLES_PORTAL
        )


class HasPermissaoPortal(BasePermission):
    permissao_requerida = None

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if eh_equipe_interna(request.user.role) and tem_role_minimo(request.user, "cs"):
            return True

        if request.user.role not in ROLES_PORTAL:
            return False

        permissao = getattr(view, "permissao_portal", None) or self.permissao_requerida
        if not permissao:
            return True

        vinculo = get_vinculo_ativo(request.user)
        if not vinculo:
            return False

        return usuario_tem_permissao_portal(request.user, vinculo, permissao)


class IsEquipeOuPortalVinculado(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if tem_role_minimo(request.user, "cs"):
            return True

        if request.user.role in ROLES_PORTAL:
            vinculo = get_vinculo_ativo(request.user)
            if not vinculo:
                return False
            prestador_id = getattr(obj, "id", None) or getattr(obj, "prestador_id", None)
            return str(vinculo.prestador_id) == str(prestador_id)

        return False


class IsAuthenticatedMarryMe(BasePermission):
    message = "Autenticação necessária."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
