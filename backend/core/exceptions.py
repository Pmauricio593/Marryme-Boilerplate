import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger("marryme.exceptions")


def custom_exception_handler(exc, context):
    """
    Handler centralizado de erros da API.
    Retorna respostas padronizadas em português.
    """
    response = exception_handler(exc, context)

    if response is not None:
        view = context.get("view", None)
        logger.warning(
            f"Erro API: {exc.__class__.__name__} | "
            f"view={view.__class__.__name__ if view else 'unknown'} | "
            f"status={response.status_code}"
        )

        # Padroniza o formato da resposta de erro
        response.data = {
            "erro": _traduzir_erro(response.status_code, response.data),
            "status": response.status_code,
        }
        return response

    # Erro inesperado — loga e retorna 500 genérico
    logger.error(f"Erro inesperado: {exc}", exc_info=True)
    return Response(
        {"erro": "Erro interno do servidor.", "status": 500},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def _traduzir_erro(status_code: int, data) -> str:
    MENSAGENS = {
        400: "Dados inválidos.",
        401: "Autenticação necessária.",
        403: "Você não tem permissão para esta ação.",
        404: "Recurso não encontrado.",
        405: "Método não permitido.",
        429: "Muitas requisições. Aguarde e tente novamente.",
        500: "Erro interno do servidor.",
    }
    # Se já tem mensagem específica, usa ela
    if isinstance(data, dict) and "detail" in data:
        return str(data["detail"])
    if isinstance(data, str):
        return data
    return MENSAGENS.get(status_code, "Erro desconhecido.")
