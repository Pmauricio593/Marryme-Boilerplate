import os

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenRefreshView

from apps.contas.views.equipe import MarryMeTokenView


def health(request):
    from django.urls import NoReverseMatch, reverse

    payload: dict[str, str | bool] = {"status": "ok"}

    commit = os.environ.get("RAILWAY_GIT_COMMIT_SHA", "")
    if commit:
        payload["commit"] = commit[:7]

    branch = os.environ.get("RAILWAY_GIT_BRANCH", "")
    if branch:
        payload["branch"] = branch

    try:
        import drf_spectacular  # noqa: F401

        payload["spectacular"] = True
    except ImportError:
        payload["spectacular"] = False

    try:
        reverse("schema")
        reverse("swagger-ui")
        payload["openapi"] = True
    except NoReverseMatch:
        payload["openapi"] = False

    return JsonResponse(payload)


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
