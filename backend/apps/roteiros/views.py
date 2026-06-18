import logging

from django.http import StreamingHttpResponse
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.openapi import (
    FinalizarSessaoRequest,
    MensagemChatRequest,
    MensagemChatResponse,
    StatusSimplesResponse,
)
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


@extend_schema_view(
    list=extend_schema(tags=["Roteiros"]),
    create=extend_schema(tags=["Roteiros"]),
    retrieve=extend_schema(tags=["Roteiros"]),
    update=extend_schema(tags=["Roteiros"]),
    partial_update=extend_schema(tags=["Roteiros"]),
    destroy=extend_schema(tags=["Roteiros"]),
)
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

    @extend_schema(
        tags=["Roteiros"],
        request=MensagemChatRequest,
        responses=MensagemChatResponse,
        summary="Envia mensagem e retorna resposta completa da IA",
    )
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

    @extend_schema(
        tags=["Roteiros"],
        request=MensagemChatRequest,
        responses={
            (200, "text/event-stream"): OpenApiResponse(
                description="Stream SSE com chunks da resposta da IA"
            )
        },
        summary="Envia mensagem com resposta em streaming (SSE)",
    )
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

    @extend_schema(
        tags=["Roteiros"],
        responses=StatusSimplesResponse,
        summary="Arquiva sessão de chat",
    )
    @action(detail=True, methods=["post"], url_path="arquivar")
    def arquivar(self, request, pk=None):
        sessao = self.get_object()
        sessao.status = "arquivada"
        sessao.save(update_fields=["status", "atualizado_em"])
        logger.info(f"Sessão arquivada: {sessao.id}")
        return Response({"status": "arquivada"})

    @extend_schema(
        tags=["Roteiros"],
        request=FinalizarSessaoRequest,
        responses=StatusSimplesResponse,
        summary="Finaliza sessão com roteiro gerado",
    )
    @action(detail=True, methods=["post"], url_path="finalizar")
    def finalizar(self, request, pk=None):
        sessao = self.get_object()
        roteiro = ChatService().finalizar_sessao(sessao, request.data.get("roteiro_final"))
        return Response(
            {
                "status": "finalizada",
                "roteiro_final_id": str(roteiro.id),
            }
        )


@extend_schema_view(
    list=extend_schema(tags=["Roteiros"]),
    retrieve=extend_schema(tags=["Roteiros"]),
)
class ChatMensagemViewSet(viewsets.ReadOnlyModelViewSet):
    """Mensagens de uma sessão — somente leitura."""

    serializer_class = ChatMensagemSerializer
    permission_classes = [IsCS]

    def get_queryset(self):
        sessao_id = self.request.query_params.get("sessao")
        if sessao_id:
            return ChatMensagem.objects.filter(sessao_id=sessao_id).order_by("criado_em")
        return ChatMensagem.objects.none()


@extend_schema_view(
    list=extend_schema(tags=["Roteiros"]),
    create=extend_schema(tags=["Roteiros"]),
    retrieve=extend_schema(tags=["Roteiros"]),
    update=extend_schema(tags=["Roteiros"]),
    partial_update=extend_schema(tags=["Roteiros"]),
    destroy=extend_schema(tags=["Roteiros"]),
)
class RoteiroFinalViewSet(viewsets.ModelViewSet):
    """Roteiros finalizados e aprovados por prestador."""

    serializer_class = RoteiroFinalSerializer
    permission_classes = [IsCS]

    def get_queryset(self):
        prestador_id = self.request.query_params.get("prestador")
        if prestador_id:
            return RoteiroFinal.objects.filter(prestador_id=prestador_id).order_by("-criado_em")
        return RoteiroFinal.objects.all()

    @extend_schema(
        tags=["Roteiros"],
        responses=StatusSimplesResponse,
        summary="Aprova roteiro para pool de few-shot",
    )
    @action(detail=True, methods=["post"], url_path="aprovar")
    def aprovar(self, request, pk=None):
        """Aprova o roteiro — entra no pool de few-shot."""
        roteiro = self.get_object()
        roteiro.aprovado = True
        roteiro.save(update_fields=["aprovado"])
        logger.info(f"Roteiro aprovado: {roteiro.id} ({roteiro.tipo})")
        return Response({"status": "aprovado"})
