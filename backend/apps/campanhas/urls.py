from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MetricaMetaViewSet, HealthScoreViewSet, RelatorioIAViewSet

router = DefaultRouter()
router.register(r'metricas', MetricaMetaViewSet, basename='metricas')
router.register(r'health-scores', HealthScoreViewSet, basename='health-scores')
router.register(r'relatorios', RelatorioIAViewSet, basename='relatorios')

urlpatterns = [
    path('', include(router.urls)),
]
