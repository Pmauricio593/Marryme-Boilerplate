import pytest

from apps.campanhas.services import HealthScoreService


@pytest.mark.parametrize(
    ("score", "status_esperado"),
    [
        (39, "em_risco"),
        (40, "atencao"),
        (69, "atencao"),
        (70, "saudavel"),
    ],
)
def test_classificar_status_nos_limiares(score, status_esperado):
    assert HealthScoreService.classificar_status(score) == status_esperado


@pytest.mark.django_db
def test_calcular_sem_impressoes_retorna_sem_dados():
    resultado = HealthScoreService().calcular({"impressions": 0})

    assert resultado["score"] == 0
    assert resultado["status"] == "sem_dados"
    assert resultado["breakdown"] == {}


def test_calcular_kpis_fortes_usa_classificacao():
    kpis = {
        "impressions": 10_000,
        "cost_per_result": 5,
        "frequency": 1.5,
        "link_ctr": 2.5,
        "video_3s": 3_000,
        "hook_rate": 30,
        "thruplay": 2_000,
    }

    resultado = HealthScoreService().calcular(kpis)

    assert resultado["score"] == 24
    assert resultado["status"] == HealthScoreService.classificar_status(24)
    assert resultado["status"] == "em_risco"


@pytest.mark.parametrize(
    ("cpm", "pontos"),
    [(5, 35), (20, 26), (40, 17), (80, 8), (150, 0)],
)
def test_score_cpm_benchmarks(cpm, pontos):
    assert HealthScoreService()._score_cpm({"cost_per_result": cpm}) == pontos


@pytest.mark.django_db
def test_salvar_persiste_health_score_no_prestador(prestador_factory):
    prestador = prestador_factory()
    kpis = {"impressions": 1000, "cost_per_result": 10, "frequency": 1.5, "link_ctr": 1.0}
    resultado = HealthScoreService().calcular(kpis)

    hs = HealthScoreService().salvar(prestador, resultado, kpis)

    prestador.refresh_from_db()
    assert hs.score == resultado["score"]
    assert prestador.health_score == resultado["score"]
    assert prestador.health_status == resultado["status"]
