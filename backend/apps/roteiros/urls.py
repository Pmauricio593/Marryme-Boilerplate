from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ChatMensagemViewSet, ChatSessaoViewSet, RoteiroFinalViewSet

router = DefaultRouter()
router.register(r"sessoes", ChatSessaoViewSet, basename="sessoes")
router.register(r"mensagens", ChatMensagemViewSet, basename="mensagens")
router.register(r"roteiros-finais", RoteiroFinalViewSet, basename="roteiros-finais")

urlpatterns = [
    path("", include(router.urls)),
]
