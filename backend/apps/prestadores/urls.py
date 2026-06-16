from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PrestadorViewSet,
    PortalPerfilView,
    PortalCampanhasView,
    PortalRoteirosView,
)

router = DefaultRouter()
router.register(r'prestadores', PrestadorViewSet)

urlpatterns = [
    path('', include(router.urls)),

    # Portal do cliente — dados
    path('portal/perfil/', PortalPerfilView.as_view({'get': 'list'}), name='portal-perfil'),
    path('portal/campanhas/', PortalCampanhasView.as_view({'get': 'list'}), name='portal-campanhas'),
    path('portal/roteiros/', PortalRoteirosView.as_view({'get': 'list'}), name='portal-roteiros'),
]
