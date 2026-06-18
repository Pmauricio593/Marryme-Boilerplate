import logging

from apps.prestadores.models import Prestador
from integrations.claude_ai import ClaudeClient

from .models import ChatMensagem, ChatSessao, RoteiroFinal

logger = logging.getLogger("marryme.roteiros")


class FewShotService:
    """
    Busca exemplos aprovados para injetar no prompt como few-shot.
    Melhora qualidade e consistência dos roteiros gerados.
    """

    def buscar_exemplos(self, categoria: str, tipo: str, limite: int = 3) -> list:
        """
        Retorna até 3 roteiros aprovados da mesma categoria e tipo.
        Ordena pelos mais recentes para usar os mais atuais como referência.
        """
        roteiros = (
            RoteiroFinal.objects.filter(
                aprovado=True,
                tipo=tipo,
                prestador__categoria=categoria,
            )
            .select_related("prestador")
            .order_by("-criado_em")[:limite]
        )

        return [
            {
                "prestador": r.prestador.nome_artistico,
                "categoria": r.prestador.get_categoria_display(),
                "conteudo": r.conteudo_json,
            }
            for r in roteiros
        ]

    def formatar_exemplos(self, exemplos: list) -> str:
        """Formata os exemplos para injeção no system prompt."""
        if not exemplos:
            return ""

        linhas = [
            "\n## EXEMPLOS DE ROTEIROS APROVADOS\n"
            "Use esses exemplos como referência de tom, "
            "estrutura e qualidade — adapte para o prestador atual.\n"
        ]

        for i, ex in enumerate(exemplos, 1):
            linhas.append(
                f"\n### Exemplo {i} — {ex['prestador']} ({ex['categoria']})\n" f"{ex['conteudo']}\n"
            )

        return "\n".join(linhas)


class ChatService:
    """
    Gerencia o ciclo completo de uma sessão de chat com IA.
    Monta contexto do prestador, injeta few-shot e chama Claude.
    """

    def __init__(self):
        self.claude = ClaudeClient()
        self.few_shot = FewShotService()

    def montar_system_prompt(self, prestador: Prestador, tipo: str = "geral") -> str:
        """
        Combina dados do prestador + few-shot de exemplos aprovados.
        Um único prompt por sessão, montado em tempo real.
        """
        dados = prestador.dados_entrevista or {}
        analise = prestador.analise_estrategica or {}

        # Busca exemplos aprovados da mesma categoria e tipo
        exemplos = self.few_shot.buscar_exemplos(prestador.categoria, tipo)
        bloco_fewshot = self.few_shot.formatar_exemplos(exemplos)

        return f"""
## PRESTADOR ATIVO NESTA CONVERSA

Nome: {prestador.nome_artistico}
Categoria: {prestador.get_categoria_display()}
Fase: {prestador.get_fase_display()}
Cidade: {prestador.cidade} / {prestador.estado}
Ticket médio estimado: R$ {prestador.ticket_medio_estimado}
Instagram: {prestador.instagram or 'não informado'}
Health Score atual: {prestador.health_score or 'não calculado'}

## DADOS DA ENTREVISTA
{self._formatar_dict(dados)}

## ANÁLISE ESTRATÉGICA
{self._formatar_dict(analise) if analise else 'Ainda não gerada.'}

## INSTRUÇÕES
- Use os dados reais acima. Nunca invente informações.
- Construa o conteúdo em diálogo, validando cada seção.
- Tom: humano, elegante, sem jargões corporativos.
- Se receber arquivos, analise antes de prosseguir.
{bloco_fewshot}
""".strip()

    def processar_mensagem(self, sessao: ChatSessao, mensagem: str, arquivos: list = None) -> str:
        """Processa mensagem e retorna resposta completa."""
        arquivos = arquivos or []
        ChatMensagem.objects.create(
            sessao=sessao,
            role="user",
            content=mensagem,
            arquivos=arquivos,
        )

        historico = self._montar_historico(sessao)
        system = self.montar_system_prompt(sessao.prestador, sessao.tipo)
        mensagem_enriquecida = self._enriquecer_mensagem_com_arquivos(mensagem, arquivos, system)

        if historico and historico[-1]["role"] == "user":
            historico[-1]["content"] = mensagem_enriquecida
        else:
            historico.append({"role": "user", "content": mensagem_enriquecida})

        resposta = self.claude.chat(
            system=system,
            messages=historico,
            max_tokens=2048,
        )

        ChatMensagem.objects.create(
            sessao=sessao,
            role="assistant",
            content=resposta,
        )

        sessao.tokens_usados += len(mensagem.split()) + len(resposta.split())
        sessao.save(update_fields=["tokens_usados", "atualizado_em"])

        logger.info(
            f"Chat processado: {sessao.prestador} / " f"sessão {sessao.id} / tipo {sessao.tipo}"
        )
        return resposta

    def processar_stream(self, sessao: ChatSessao, mensagem: str, arquivos: list = None):
        """Streaming via Server-Sent Events — chunks em tempo real."""
        arquivos = arquivos or []
        ChatMensagem.objects.create(
            sessao=sessao,
            role="user",
            content=mensagem,
            arquivos=arquivos,
        )

        historico = self._montar_historico(sessao)
        system = self.montar_system_prompt(sessao.prestador, sessao.tipo)
        mensagem_enriquecida = self._enriquecer_mensagem_com_arquivos(mensagem, arquivos, system)

        if historico and historico[-1]["role"] == "user":
            historico[-1]["content"] = mensagem_enriquecida
        else:
            historico.append({"role": "user", "content": mensagem_enriquecida})

        resposta_completa = []
        for chunk in self.claude.chat_stream(system=system, messages=historico):
            resposta_completa.append(chunk)
            yield chunk

        texto_final = "".join(resposta_completa)
        ChatMensagem.objects.create(
            sessao=sessao,
            role="assistant",
            content=texto_final,
        )
        sessao.save(update_fields=["atualizado_em"])
        logger.info(f"Stream concluído: {sessao.prestador} / sessão {sessao.id}")

    TIPO_ROTEIRO_MAP = {
        "geral": "video",
        "video": "video",
        "cta": "cta",
        "direcao": "direcao",
        "analise": "analise",
    }

    def finalizar_sessao(self, sessao: ChatSessao, roteiro_final) -> RoteiroFinal:
        """Finaliza sessão e cria RoteiroFinal em rascunho para aprovação."""
        sessao.status = "finalizada"
        sessao.roteiro_final = roteiro_final
        sessao.save(update_fields=["status", "roteiro_final", "atualizado_em"])

        if isinstance(roteiro_final, dict):
            conteudo = roteiro_final
        elif roteiro_final:
            conteudo = {"texto": roteiro_final}
        else:
            ultima = sessao.mensagens.filter(role="assistant").order_by("-criado_em").first()
            conteudo = {"texto": ultima.content if ultima else ""}

        tipo = self.TIPO_ROTEIRO_MAP.get(sessao.tipo, "video")
        roteiro, _ = RoteiroFinal.objects.update_or_create(
            sessao=sessao,
            defaults={
                "prestador": sessao.prestador,
                "tipo": tipo,
                "conteudo_json": conteudo,
                "aprovado": False,
            },
        )

        logger.info(f"Sessão finalizada: {sessao.id} — roteiro {roteiro.id}")
        return roteiro

    # ── Helpers ──────────────────────────────────────────────────

    def _montar_historico(self, sessao: ChatSessao) -> list:
        return [
            {"role": m.role, "content": m.content} for m in sessao.mensagens.order_by("criado_em")
        ]

    def _formatar_dict(self, dados: dict) -> str:
        if not dados:
            return "Não informado."
        return "\n".join(f"- {k}: {v}" for k, v in dados.items())

    def _enriquecer_mensagem_com_arquivos(self, mensagem: str, arquivos: list, system: str) -> str:
        """
        Processa anexos PDF em base64.
        Contrato: [{"nome": "...", "tipo": "application/pdf", "dados_base64": "..."}]
        """
        if not arquivos:
            return mensagem

        partes = [mensagem]
        for arq in arquivos:
            if not isinstance(arq, dict):
                continue
            mime = (arq.get("tipo") or arq.get("media_type") or "").lower()
            if "pdf" not in mime:
                continue
            b64 = arq.get("dados_base64") or arq.get("data")
            if not b64:
                continue
            nome = arq.get("nome", "documento.pdf")
            try:
                analise = self.claude.analisar_pdf(
                    system=system,
                    mensagem=f"Resuma os pontos relevantes deste PDF ({nome}) para roteiros de casamento.",
                    pdf_base64=b64,
                )
                partes.append(f"\n[Análise do PDF {nome}]:\n{analise}")
            except Exception as e:
                logger.warning(f"Falha ao analisar PDF {nome}: {e}")
                partes.append(f"\n[PDF {nome} anexado — análise indisponível no momento.]")

        return "\n".join(partes)
