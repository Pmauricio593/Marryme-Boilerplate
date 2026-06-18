import logging

from django.http import StreamingHttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.permissions import IsCS

from .models import ChatMensagem, ChatSessao, RoteiroFinal
from .serializers import (
    ChatMensagemSerializer,
    ChatSessaoListSerializer,
    ChatSessaoSerializer,
    RoteiroFinalSerializer,
)
from .services import ChatService

logger = logging.getLogger("marryme.roteiros")


class ChatSessaoViewSet(viewsets.ModelViewSet):
    """
    Sessões de chat por prestador.
    Listagem usa serializer resumido — detalhe usa completo.
    """

    permission_classes = [IsCS]

    def get_serializer_class(self):
        if self.action == "list":
            return ChatSessaoListSerializer
        return ChatSessaoSerializer

    def get_queryset(self):
        prestador_id = self.request.query_params.get("prestador")
        if prestador_id:
            return ChatSessao.objects.filter(prestador_id=prestador_id).order_by("-atualizado_em")
        return ChatSessao.objects.all()

    @action(detail=True, methods=["post"], url_path="mensagem")
    def mensagem(self, request, pk=None):
        """Processa mensagem e retorna resposta completa da IA."""
        sessao = self.get_object()
        texto = request.data.get("mensagem", "").strip()
        arquivos = request.data.get("arquivos", [])

        if not texto:
            return Response(
                {"erro": "Mensagem não pode ser vazia."}, status=status.HTTP_400_BAD_REQUEST
            )

        resposta = ChatService().processar_mensagem(sessao, texto, arquivos)
        return Response({"resposta": resposta})

    @action(detail=True, methods=["post"], url_path="stream")
    def stream(self, request, pk=None):
        """
        Processa mensagem com streaming via Server-Sent Events.
        Frontend recebe chunks em tempo real conforme IA responde.
        """
        sessao = self.get_object()
        texto = request.data.get("mensagem", "").strip()
        arquivos = request.data.get("arquivos", [])

        if not texto:
            return Response(
                {"erro": "Mensagem não pode ser vazia."}, status=status.HTTP_400_BAD_REQUEST
            )

        def gerar_chunks():
            for chunk in ChatService().processar_stream(sessao, texto, arquivos):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingHttpResponse(
            gerar_chunks(),
            content_type="text/event-stream",
        )

    @action(detail=True, methods=["post"], url_path="arquivar")
    def arquivar(self, request, pk=None):
        sessao = self.get_object()
        sessao.status = "arquivada"
        sessao.save(update_fields=["status", "atualizado_em"])
        logger.info(f"Sessão arquivada: {sessao.id}")
        return Response({"status": "arquivada"})

    @action(detail=True, methods=["post"], url_path="finalizar")
    def finalizar(self, request, pk=None):
        sessao = self.get_object()
        sessao.status = "finalizada"
        sessao.roteiro_final = request.data.get("roteiro_final")
        sessao.save(update_fields=["status", "roteiro_final", "atualizado_em"])
        logger.info(f"Sessão finalizada: {sessao.id}")
        return Response({"status": "finalizada"})


class ChatMensagemViewSet(viewsets.ReadOnlyModelViewSet):
    """Mensagens de uma sessão — somente leitura."""

    serializer_class = ChatMensagemSerializer
    permission_classes = [IsCS]

    def get_queryset(self):
        sessao_id = self.request.query_params.get("sessao")
        if sessao_id:
            return ChatMensagem.objects.filter(sessao_id=sessao_id).order_by("criado_em")
        return ChatMensagem.objects.none()


class RoteiroFinalViewSet(viewsets.ModelViewSet):
    """Roteiros finalizados e aprovados por prestador."""

    serializer_class = RoteiroFinalSerializer
    permission_classes = [IsCS]

    def get_queryset(self):
        prestador_id = self.request.query_params.get("prestador")
        if prestador_id:
            return RoteiroFinal.objects.filter(prestador_id=prestador_id).order_by("-criado_em")
        return RoteiroFinal.objects.all()

    @action(detail=True, methods=["post"], url_path="aprovar")
    def aprovar(self, request, pk=None):
        """Aprova o roteiro — entra no pool de few-shot."""
        roteiro = self.get_object()
        roteiro.aprovado = True
        roteiro.save(update_fields=["aprovado"])
        logger.info(f"Roteiro aprovado: {roteiro.id} ({roteiro.tipo})")
        return Response({"status": "aprovado"})
