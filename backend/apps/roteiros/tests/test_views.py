from unittest.mock import patch

import pytest

from apps.roteiros.models import ChatSessao
from apps.roteiros.services import ChatService


@pytest.mark.django_db
def test_cs_cria_sessao_chat(api_cs, prestador_factory):
    prestador = prestador_factory()

    response = api_cs.post(
        "/api/v1/sessoes/",
        {"prestador": str(prestador.id), "titulo": "Roteiro CTA", "tipo": "cta"},
        format="json",
    )

    assert response.status_code == 201
    assert response.data["titulo"] == "Roteiro CTA"
    assert ChatSessao.objects.filter(prestador=prestador).count() == 1


@pytest.mark.django_db
@patch.object(ChatService, "processar_mensagem", return_value="Resposta mock da IA")
def test_mensagem_com_claude_mockado(mock_processar, api_cs, chat_sessao_factory):
    sessao = chat_sessao_factory()

    response = api_cs.post(
        f"/api/v1/sessoes/{sessao.id}/mensagem/",
        {"mensagem": "Escreva um gancho emocional"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["resposta"] == "Resposta mock da IA"
    mock_processar.assert_called_once()


@pytest.mark.django_db
def test_mensagem_vazia_retorna_400(api_cs, chat_sessao_factory):
    sessao = chat_sessao_factory()

    response = api_cs.post(
        f"/api/v1/sessoes/{sessao.id}/mensagem/",
        {"mensagem": "   "},
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
@patch.object(ChatService, "processar_stream", return_value=iter(["Olá", " mundo"]))
def test_stream_retorna_sse_com_done(mock_stream, api_cs, chat_sessao_factory):
    sessao = chat_sessao_factory()

    response = api_cs.post(
        f"/api/v1/sessoes/{sessao.id}/stream/",
        {"mensagem": "Stream teste"},
        format="json",
    )

    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/event-stream")
    body = b"".join(response.streaming_content).decode()
    assert "data: Olá" in body
    assert "data:  mundo" in body
    assert "data: [DONE]" in body
    mock_stream.assert_called_once()


@pytest.mark.django_db
def test_arquivar_sessao(api_cs, chat_sessao_factory):
    sessao = chat_sessao_factory(status="ativa")

    response = api_cs.post(f"/api/v1/sessoes/{sessao.id}/arquivar/")

    assert response.status_code == 200
    sessao.refresh_from_db()
    assert sessao.status == "arquivada"


@pytest.mark.django_db
def test_finalizar_sessao(api_cs, chat_sessao_factory):
    from apps.roteiros.models import RoteiroFinal

    sessao = chat_sessao_factory()
    roteiro = {"titulo": "CTA final", "corpo": "Texto aprovado"}

    response = api_cs.post(
        f"/api/v1/sessoes/{sessao.id}/finalizar/",
        {"roteiro_final": roteiro},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["status"] == "finalizada"
    assert "roteiro_final_id" in response.data
    sessao.refresh_from_db()
    assert sessao.status == "finalizada"
    assert sessao.roteiro_final == roteiro
    assert RoteiroFinal.objects.filter(sessao=sessao, aprovado=False).exists()


@pytest.mark.django_db
def test_aprovar_roteiro_final(api_cs, roteiro_final_factory):
    roteiro = roteiro_final_factory(aprovado=False)

    response = api_cs.post(f"/api/v1/roteiros-finais/{roteiro.id}/aprovar/")

    assert response.status_code == 200
    roteiro.refresh_from_db()
    assert roteiro.aprovado is True


@pytest.mark.django_db
def test_prestador_nao_acessa_sessoes(api, prestador_factory, chat_sessao_factory):
    from apps.prestadores.factories import UsuarioFactory

    usuario = UsuarioFactory(role="prestador")
    api.force_authenticate(user=usuario)
    chat_sessao_factory()

    response = api.get("/api/v1/sessoes/")

    assert response.status_code == 403
