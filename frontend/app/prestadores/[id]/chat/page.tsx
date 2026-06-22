"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { FormEvent, useCallback, useEffect, useRef, useState } from "react";
import { toast } from "sonner";
import { AppShell } from "@/components/layout/AppShell";
import { apiFetch, streamSessaoChat } from "@/lib/api/client";
import { labelRoteiroTipo } from "@/lib/constants";
import type { ChatMensagemApi, ChatSessao, Paginated, RoteiroFinal } from "@/types/api";

type Mensagem = { role: "user" | "assistant"; content: string };

export default function ChatPage() {
  const params = useParams();
  const prestadorId = params.id as string;
  const [sessoes, setSessoes] = useState<ChatSessao[]>([]);
  const [sessaoId, setSessaoId] = useState<string | null>(null);
  const [mensagens, setMensagens] = useState<Mensagem[]>([]);
  const [roteiros, setRoteiros] = useState<RoteiroFinal[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [finalizando, setFinalizando] = useState(false);
  const [aprovandoId, setAprovandoId] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  const loadRoteiros = useCallback(async () => {
    try {
      const res = await apiFetch<Paginated<RoteiroFinal>>(
        `/api/v1/roteiros-finais/?prestador=${prestadorId}`,
      );
      setRoteiros(res.resultados);
    } catch {
      setRoteiros([]);
    }
  }, [prestadorId]);

  const loadSessoes = useCallback(async () => {
    try {
      const res = await apiFetch<Paginated<ChatSessao>>(
        `/api/v1/sessoes/?prestador=${prestadorId}`,
      );
      setSessoes(res.resultados);
      if (res.resultados[0]) {
        setSessaoId((atual) => atual ?? res.resultados[0].id);
      }
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Erro ao carregar sessões.");
    }
  }, [prestadorId]);

  useEffect(() => {
    loadSessoes();
    loadRoteiros();
  }, [loadSessoes, loadRoteiros]);

  useEffect(() => {
    if (sessaoId) loadMensagens(sessaoId);
  }, [sessaoId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [mensagens]);

  async function loadMensagens(id: string) {
    try {
      const res = await apiFetch<Paginated<ChatMensagemApi>>(`/api/v1/mensagens/?sessao=${id}`);
      setMensagens(
        res.resultados.map((m) => ({
          role: m.role === "assistant" ? "assistant" : "user",
          content: m.content,
        })),
      );
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Erro ao carregar mensagens.");
      setMensagens([]);
    }
  }

  async function criarSessao() {
    try {
      const s = await apiFetch<ChatSessao>("/api/v1/sessoes/", {
        method: "POST",
        body: JSON.stringify({
          prestador: prestadorId,
          titulo: "Nova conversa",
          tipo: "cta",
        }),
      });
      setSessoes((prev) => [s, ...prev]);
      setSessaoId(s.id);
      setMensagens([]);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Erro ao criar sessão.");
    }
  }

  async function finalizarSessao() {
    if (!sessaoId) return;
    setFinalizando(true);
    try {
      const res = await apiFetch<{ status: string; roteiro_final_id: string }>(
        `/api/v1/sessoes/${sessaoId}/finalizar/`,
        { method: "POST", body: JSON.stringify({}) },
      );
      toast.success(`Roteiro finalizado — aprove quando estiver ok.`);
      loadSessoes();
      loadRoteiros();
      if (res.roteiro_final_id) {
        setAprovandoId(res.roteiro_final_id);
      }
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Erro ao finalizar.");
    } finally {
      setFinalizando(false);
    }
  }

  async function aprovarRoteiro(roteiroId: string) {
    setAprovandoId(roteiroId);
    try {
      await apiFetch(`/api/v1/roteiros-finais/${roteiroId}/aprovar/`, { method: "POST" });
      toast.success("Roteiro aprovado — entrou no pool de few-shot.");
      loadRoteiros();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Erro ao aprovar.");
    } finally {
      setAprovandoId(null);
    }
  }

  async function enviar(e: FormEvent) {
    e.preventDefault();
    if (!sessaoId || !input.trim() || streaming) return;

    const texto = input.trim();
    setInput("");
    setMensagens((m) => [...m, { role: "user", content: texto }]);
    setStreaming(true);

    let resposta = "";
    setMensagens((m) => [...m, { role: "assistant", content: "" }]);

    try {
      await streamSessaoChat(sessaoId, texto, (chunk) => {
        resposta += chunk;
        setMensagens((m) => {
          const copy = [...m];
          copy[copy.length - 1] = { role: "assistant", content: resposta };
          return copy;
        });
      });
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Erro no stream.");
    } finally {
      setStreaming(false);
    }
  }

  return (
    <AppShell>
      <div className="mb-4">
        <Link href={`/prestadores/${prestadorId}`} className="text-sm text-secondary hover:underline">
          ← Voltar ao prestador
        </Link>
        <h1 className="mt-2 font-display text-2xl text-primary">Chat de roteiros</h1>
      </div>

      <div className="mb-4 flex flex-wrap gap-2">
        <select
          className="input max-w-md"
          value={sessaoId || ""}
          onChange={(e) => setSessaoId(e.target.value)}
        >
          {sessoes.map((s) => (
            <option key={s.id} value={s.id}>
              {s.titulo} ({s.status})
            </option>
          ))}
        </select>
        <button type="button" className="btn-secondary" onClick={criarSessao}>
          Nova sessão
        </button>
        <button
          type="button"
          className="btn-secondary"
          disabled={!sessaoId || finalizando}
          onClick={finalizarSessao}
        >
          {finalizando ? "Finalizando..." : "Finalizar roteiro"}
        </button>
      </div>

      <div className="card mb-6 flex h-[480px] flex-col">
        <div className="flex-1 space-y-3 overflow-y-auto pr-2">
          {mensagens.length === 0 && (
            <p className="text-sm text-text-mid">Envie a primeira mensagem para a IA.</p>
          )}
          {mensagens.map((m, i) => (
            <div
              key={i}
              className={`rounded-lg px-3 py-2 text-sm ${
                m.role === "user" ? "ml-8 bg-secondary/10" : "mr-8 bg-bg-light"
              }`}
            >
              <p className="mb-1 text-xs font-medium text-text-muted">
                {m.role === "user" ? "Você" : "IA"}
              </p>
              <p className="whitespace-pre-wrap">{m.content}</p>
            </div>
          ))}
          <div ref={bottomRef} />
        </div>
        <form onSubmit={enviar} className="mt-4 flex gap-2 border-t border-border pt-4">
          <input
            className="input flex-1"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Escreva sua mensagem..."
            disabled={!sessaoId || streaming}
          />
          <button type="submit" className="btn-primary" disabled={!sessaoId || streaming}>
            {streaming ? "Gerando..." : "Enviar"}
          </button>
        </form>
      </div>

      <div className="card space-y-4">
        <h2 className="font-display text-xl text-primary">Roteiros finalizados</h2>
        {roteiros.length === 0 ? (
          <p className="text-sm text-text-mid">Nenhum roteiro finalizado ainda.</p>
        ) : (
          <ul className="space-y-3">
            {roteiros.map((r) => (
              <li key={r.id} className="rounded-lg border border-border p-3 text-sm">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span>
                    {labelRoteiroTipo(r.tipo)} ·{" "}
                    {new Date(r.criado_em).toLocaleDateString("pt-BR")}
                    {r.aprovado ? (
                      <span className="ml-2 badge-hs-saudavel">Aprovado</span>
                    ) : (
                      <span className="ml-2 badge-hs-atencao">Aguardando aprovação</span>
                    )}
                  </span>
                  {!r.aprovado && (
                    <button
                      type="button"
                      className="btn-primary text-xs"
                      disabled={aprovandoId === r.id}
                      onClick={() => aprovarRoteiro(r.id)}
                    >
                      {aprovandoId === r.id ? "Aprovando..." : "Aprovar"}
                    </button>
                  )}
                </div>
                {"texto" in r.conteudo_json && typeof r.conteudo_json.texto === "string" ? (
                  <p className="mt-2 whitespace-pre-wrap text-text-mid">
                    {r.conteudo_json.texto.slice(0, 400)}
                    {r.conteudo_json.texto.length > 400 ? "…" : ""}
                  </p>
                ) : null}
              </li>
            ))}
          </ul>
        )}
      </div>
    </AppShell>
  );
}
