from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PrestadorViewSet,
    MarryMeTokenView,
    PortalLoginView,
    PrimeiroAcessoView,
    PortalPerfilView,
    PortalCampanhasView,
    PortalRoteirosView,
)

router = DefaultRouter()
router.register(r'prestadores', PrestadorViewSet)

urlpatterns = [
    path('', include(router.urls)),

    # Portal do cliente — auth
    path('portal/auth/login/',
         PortalLoginView.as_view(),    name='portal-login'),
    path('portal/auth/primeiro-acesso/',
         PrimeiroAcessoView.as_view(), name='portal-primeiro-acesso'),

    # Portal do cliente — dados
    path('portal/perfil/',      PortalPerfilView.as_view(),    name='portal-perfil'),
    path('portal/campanhas/',   PortalCampanhasView.as_view(),
         name='portal-campanhas'),
    path('portal/roteiros/',    PortalRoteirosView.as_view(),
         name='portal-roteiros'),
]
