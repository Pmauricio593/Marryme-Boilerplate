from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenRefreshView

from apps.contas.views.equipe import MarryMeTokenView


def health(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("", health),
    path("health/", health),
    path("admin/", admin.site.urls),
    # Auth equipe
    path("api/v1/auth/login/", MarryMeTokenView.as_view(), name="login"),
    path("api/v1/auth/refresh/", TokenRefreshView.as_view(), name="refresh"),
    # OpenAPI
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/v1/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # Apps
    path("api/v1/", include("apps.contas.urls")),
    path("api/v1/", include("apps.prestadores.urls")),
    path("api/v1/", include("apps.campanhas.urls")),
    path("api/v1/", include("apps.roteiros.urls")),
]
