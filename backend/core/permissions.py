from rest_framework.permissions import BasePermission


HIERARQUIA = ['dev', 'sdr', 'cs', 'admin']


def tem_role_minimo(usuario, role_minimo: str) -> bool:
    """Verifica se o usuário tem o nível mínimo de acesso."""
    try:
        return HIERARQUIA.index(usuario.role) >= HIERARQUIA.index(role_minimo)
    except ValueError:
        return False


class IsAdmin(BasePermission):
    """Apenas administradores."""

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'admin'
        )


class IsCS(BasePermission):
    """CS e acima (cs, admin)."""

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            tem_role_minimo(request.user, 'cs')
        )


class IsSDR(BasePermission):
    """SDR e acima (sdr, cs, admin)."""

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            tem_role_minimo(request.user, 'sdr')
        )


class IsAuthenticatedMarryMe(BasePermission):
    """
    Qualquer usuário autenticado da MarryMe.
    Usado como permissão base em todas as views.
    """
    message = 'Autenticação necessária.'

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsPrestador(BasePermission):
    """Apenas prestadores."""

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'prestador'
        )


class IsEquipeOuPrestadorVinculado(BasePermission):
    """
    Equipe interna (CS, admin) vê tudo.
    Prestador vê apenas os próprios dados.
    """

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if tem_role_minimo(request.user, 'cs'):
            return True

        if request.user.role == 'prestador':
            vinculado = getattr(request.user, 'prestador_vinculado', None)
            if vinculado is None:
                return False
            prestador_id = getattr(obj, 'id', None) or getattr(
                obj, 'prestador_id', None)
            return str(vinculado.id) == str(prestador_id)

        return False
