import logging
from collections.abc import Generator

import anthropic
from django.conf import settings

logger = logging.getLogger("marryme.integrations.claude")


class ClaudeClient:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.CLAUDE_MODEL

    def chat(self, system: str, messages: list, max_tokens: int = 2048) -> str:
        """
        Chamada simples — retorna resposta completa.
        Usar para análises, roteiros e processamento em background.
        """
        logger.info(f"Claude chat — {len(messages)} mensagens")
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                messages=messages,
            )
            tokens = response.usage.input_tokens + response.usage.output_tokens
            logger.info(f"Claude respondeu — {tokens} tokens usados")
            return response.content[0].text
        except Exception as e:
            logger.error(f"Erro Claude API: {e}")
            raise

    def chat_stream(
        self, system: str, messages: list, max_tokens: int = 2048
    ) -> Generator[str, None, None]:
        """
        Chamada com streaming — retorna gerador de chunks.
        Usar para o chat de roteiros em tempo real.
        """
        logger.info(f"Claude stream — {len(messages)} mensagens")
        try:
            with self.client.messages.stream(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                messages=messages,
            ) as stream:
                yield from stream.text_stream
        except Exception as e:
            logger.error(f"Erro Claude stream: {e}")
            raise

    def analisar_pdf(
        self, system: str, mensagem: str, pdf_base64: str, max_tokens: int = 4096
    ) -> str:
        """
        Analisa PDF enviado como base64.
        Requer header anthropic-beta: pdfs-2024-09-25.
        """
        logger.info("Claude analisando PDF")
        try:
            response = self.client.beta.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "document",
                                "source": {
                                    "type": "base64",
                                    "media_type": "application/pdf",
                                    "data": pdf_base64,
                                },
                            },
                            {"type": "text", "text": mensagem},
                        ],
                    }
                ],
                betas=["pdfs-2024-09-25"],
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Erro Claude PDF: {e}")
            raise
