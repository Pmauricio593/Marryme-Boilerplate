from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.contas.views.convites import (
    ConviteListCreateView,
    ConviteReenviarView,
    ConviteRevogarView,
    MembroListView,
    MembroRevogarView,
)
from apps.contas.views.portal import (
    AceitarConviteView,
    PortalLoginView,
    ValidarConviteView,
)

urlpatterns = [
    # Portal — convite e login
    path('portal/convites/validar/', ValidarConviteView.as_view(), name='portal-convite-validar'),
    path('portal/convites/aceitar/', AceitarConviteView.as_view(), name='portal-convite-aceitar'),
    path('portal/auth/login/', PortalLoginView.as_view(), name='portal-login'),
    path('portal/auth/refresh/', TokenRefreshView.as_view(), name='portal-refresh'),

    # CS — convites e membros por prestador
    path(
        'prestadores/<uuid:prestador_id>/convites/',
        ConviteListCreateView.as_view(),
        name='prestador-convites',
    ),
    path(
        'prestadores/<uuid:prestador_id>/convites/<uuid:convite_id>/reenviar/',
        ConviteReenviarView.as_view(),
        name='prestador-convite-reenviar',
    ),
    path(
        'prestadores/<uuid:prestador_id>/convites/<uuid:convite_id>/',
        ConviteRevogarView.as_view(),
        name='prestador-convite-revogar',
    ),
    path(
        'prestadores/<uuid:prestador_id>/membros/',
        MembroListView.as_view(),
        name='prestador-membros',
    ),
    path(
        'prestadores/<uuid:prestador_id>/membros/<uuid:usuario_id>/',
        MembroRevogarView.as_view(),
        name='prestador-membro-revogar',
    ),
]
