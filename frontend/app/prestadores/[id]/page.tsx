"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { FormEvent, useCallback, useEffect, useState } from "react";
import { toast } from "sonner";
import { AppShell } from "@/components/layout/AppShell";
import { apiFetch } from "@/lib/api/client";
import {
  CONVITE_TIPOS,
  FASES,
  labelCategoria,
  labelConviteStatus,
  labelFase,
  labelHsStatus,
} from "@/lib/constants";
import type {
  Convite,
  HealthScore,
  MembroPortal,
  Paginated,
  PrestadorDetail,
  RelatorioIA,
} from "@/types/api";

function hsBadge(status: string | null) {
  if (status === "saudavel") return "badge-hs-saudavel";
  if (status === "atencao") return "badge-hs-atencao";
  if (status === "em_risco") return "badge-hs-risco";
  return "badge bg-gray-100 text-gray-600";
}

export default function PrestadorDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const [prestador, setPrestador] = useState<PrestadorDetail | null>(null);
  const [hs, setHs] = useState<HealthScore | null>(null);
  const [convites, setConvites] = useState<Convite[]>([]);
  const [membros, setMembros] = useState<MembroPortal[]>([]);
  const [relatorio, setRelatorio] = useState<RelatorioIA | null>(null);
  const [novaFase, setNovaFase] = useState("");
  const [conviteEmail, setConviteEmail] = useState("");
  const [conviteTipo, setConviteTipo] = useState("assessoria");
  const [periodoInicio, setPeriodoInicio] = useState("");
  const [periodoFim, setPeriodoFim] = useState("");
  const [gerandoAnalise, setGerandoAnalise] = useState(false);
  const [loading, setLoading] = useState(true);
  const [salvandoDados, setSalvandoDados] = useState(false);
  const [editForm, setEditForm] = useState({
    whatsapp: "",
    email: "",
    instagram: "",
    meta_ad_account_id: "",
    meta_cpl_alvo: "",
    meta_orcamento_mensal: "",
    meta_leads_alvo_mensal: "",
    ticket_medio_estimado: "",
  });

  const loadAll = useCallback(async () => {
    setLoading(true);
    try {
      const [p, health, conv, memb, rels] = await Promise.all([
        apiFetch<PrestadorDetail>(`/api/v1/prestadores/${id}/`),
        apiFetch<HealthScore>(`/api/v1/health-scores/ultimo/?prestador=${id}`).catch(
          () => null,
        ),
        apiFetch<Paginated<Convite>>(`/api/v1/prestadores/${id}/convites/`),
        apiFetch<Paginated<MembroPortal>>(`/api/v1/prestadores/${id}/membros/`),
        apiFetch<Paginated<RelatorioIA>>(`/api/v1/relatorios/?prestador=${id}`),
      ]);
      setPrestador(p);
      setHs(health);
      setConvites(conv.resultados);
      setMembros(memb.resultados);
      setRelatorio(rels.resultados[0] ?? null);
      setNovaFase(p.fase);
      setEditForm({
        whatsapp: p.whatsapp ?? "",
        email: p.email ?? "",
        instagram: p.instagram ?? "",
        meta_ad_account_id: p.meta_ad_account_id ?? "",
        meta_cpl_alvo: p.meta_cpl_alvo != null ? String(p.meta_cpl_alvo) : "",
        meta_orcamento_mensal:
          p.meta_orcamento_mensal != null ? String(p.meta_orcamento_mensal) : "",
        meta_leads_alvo_mensal:
          p.meta_leads_alvo_mensal != null ? String(p.meta_leads_alvo_mensal) : "",
        ticket_medio_estimado: p.ticket_medio_estimado != null ? String(p.ticket_medio_estimado) : "",
      });
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Erro ao carregar prestador.");
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  async function salvarDados(e: FormEvent) {
    e.preventDefault();
    setSalvandoDados(true);
    try {
      const body: Record<string, unknown> = {
        whatsapp: editForm.whatsapp,
        email: editForm.email,
        instagram: editForm.instagram,
        meta_ad_account_id: editForm.meta_ad_account_id,
      };
      if (editForm.ticket_medio_estimado) {
        body.ticket_medio_estimado = Number(editForm.ticket_medio_estimado);
      }
      if (editForm.meta_cpl_alvo) body.meta_cpl_alvo = editForm.meta_cpl_alvo;
      if (editForm.meta_orcamento_mensal) body.meta_orcamento_mensal = editForm.meta_orcamento_mensal;
      if (editForm.meta_leads_alvo_mensal) {
        body.meta_leads_alvo_mensal = Number(editForm.meta_leads_alvo_mensal);
      }

      await apiFetch(`/api/v1/prestadores/${id}/`, {
        method: "PATCH",
        body: JSON.stringify(body),
      });
      toast.success("Dados salvos.");
      loadAll();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Erro ao salvar.");
    } finally {
      setSalvandoDados(false);
    }
  }

  async function atualizarFase() {
    try {
      await apiFetch(`/api/v1/prestadores/${id}/atualizar-fase/`, {
        method: "POST",
        body: JSON.stringify({ fase: novaFase }),
      });
      toast.success("Fase atualizada.");
      loadAll();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Erro ao atualizar fase.");
    }
  }

  async function syncMeta() {
    try {
      await apiFetch(`/api/v1/prestadores/${id}/sync-meta/`, { method: "POST" });
      toast.success("Sync Meta enfileirado — aguarde ~1 min e recarregue.");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Erro ao enfileirar sync.");
    }
  }

  async function emitirConvite(e: FormEvent) {
    e.preventDefault();
    try {
      const res = await apiFetch<Convite>(`/api/v1/prestadores/${id}/convites/`, {
        method: "POST",
        body: JSON.stringify({ email: conviteEmail, tipo: conviteTipo }),
      });
      if (res.link_portal) {
        await navigator.clipboard.writeText(res.link_portal);
        toast.success("Convite criado — link copiado!");
      } else {
        toast.success("Convite criado.");
      }
      setConviteEmail("");
      loadAll();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Erro ao emitir convite.");
    }
  }

  async function reenviarConvite(conviteId: string) {
    try {
      const res = await apiFetch<Convite>(
        `/api/v1/prestadores/${id}/convites/${conviteId}/reenviar/`,
        { method: "POST" },
      );
      if (res.link_portal) {
        await navigator.clipboard.writeText(res.link_portal);
        toast.success("Novo link copiado!");
      }
      loadAll();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Erro ao reenviar.");
    }
  }

  async function revogarConvite(conviteId: string) {
    try {
      await apiFetch(`/api/v1/prestadores/${id}/convites/${conviteId}/`, {
        method: "DELETE",
      });
      toast.success("Convite revogado.");
      loadAll();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Erro ao revogar.");
    }
  }

  async function revogarMembro(usuarioId: string) {
    try {
      await apiFetch(`/api/v1/prestadores/${id}/membros/${usuarioId}/`, {
        method: "DELETE",
      });
      toast.success("Acesso revogado.");
      loadAll();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Erro ao revogar membro.");
    }
  }

  async function gerarRelatorioIA(e: FormEvent) {
    e.preventDefault();
    if (!periodoInicio || !periodoFim) {
      toast.error("Informe o período.");
      return;
    }
    setGerandoAnalise(true);
    try {
      let rel = relatorio;
      if (
        !rel ||
        (periodoInicio && rel.periodo_inicio !== periodoInicio) ||
        (periodoFim && rel.periodo_fim !== periodoFim)
      ) {
        rel = await apiFetch<RelatorioIA>("/api/v1/relatorios/", {
          method: "POST",
          body: JSON.stringify({
            prestador: id,
            periodo_inicio: periodoInicio,
            periodo_fim: periodoFim,
            dados_json: {},
          }),
        });
      }
      await apiFetch(`/api/v1/relatorios/${rel.id}/gerar-analise/`, { method: "POST" });
      toast.success("Análise enfileirada — atualizando...");

      for (let i = 0; i < 12; i++) {
        await new Promise((r) => setTimeout(r, 2000));
        const atualizado = await apiFetch<RelatorioIA>(`/api/v1/relatorios/${rel.id}/`);
        if (atualizado.dados_json?.analise) {
          setRelatorio(atualizado);
          toast.success("Pauta pronta!");
          return;
        }
      }
      toast.message("Ainda processando — recarregue a página em instantes.");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Erro no relatório IA.");
    } finally {
      setGerandoAnalise(false);
    }
  }

  if (loading) {
    return (
      <AppShell>
        <p className="text-text-mid">Carregando...</p>
      </AppShell>
    );
  }

  if (!prestador) {
    return (
      <AppShell>
        <p className="text-text-mid">Prestador não encontrado.</p>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="mb-6">
        <Link href="/prestadores" className="text-sm text-secondary hover:underline">
          ← Voltar
        </Link>
        <h1 className="mt-2 font-display text-3xl font-semibold text-primary">
          {prestador.nome_artistico}
        </h1>
        <p className="text-sm text-text-mid">
          {prestador.cidade}/{prestador.estado} · {labelCategoria(prestador.categoria)} ·{" "}
          {labelFase(prestador.fase)}
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="card space-y-4">
          <h2 className="font-display text-xl text-primary">Pipeline</h2>
          <div className="flex flex-wrap gap-2">
            <select className="input" value={novaFase} onChange={(e) => setNovaFase(e.target.value)}>
              {FASES.map((f) => (
                <option key={f.value} value={f.value}>
                  {f.label}
                </option>
              ))}
            </select>
            <button type="button" className="btn-primary" onClick={atualizarFase}>
              Atualizar fase
            </button>
          </div>
          <button type="button" className="btn-secondary" onClick={syncMeta}>
            Sync Meta Ads
          </button>
          <Link href={`/prestadores/${id}/chat`} className="btn-primary inline-block">
            Abrir chat de roteiros
          </Link>
        </div>

        <div className="card space-y-3">
          <h2 className="font-display text-xl text-primary">Health Score</h2>
          {hs ? (
            <>
              <p className="text-4xl font-display font-semibold text-primary">{hs.score}</p>
              <p className="text-sm">
                <span className={hsBadge(hs.status)}>{labelHsStatus(hs.status)}</span>
              </p>
              <p className="text-xs text-text-muted">
                CPM {hs.score_cpl} · Hook {hs.score_orcamento} · Retenção {hs.score_leads} · CTR{" "}
                {hs.score_ctr}
              </p>
              <p className="text-xs text-text-muted">Calculado em {hs.data_calculo}</p>
            </>
          ) : (
            <p className="text-text-mid">Sem health score — rode sync Meta.</p>
          )}
        </div>

        <div className="card space-y-4 lg:col-span-2">
          <h2 className="font-display text-xl text-primary">Dados operacionais</h2>
          <form onSubmit={salvarDados} className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-1 block text-sm text-text-mid">WhatsApp</label>
              <input
                className="input"
                value={editForm.whatsapp}
                onChange={(e) => setEditForm((f) => ({ ...f, whatsapp: e.target.value }))}
              />
            </div>
            <div>
              <label className="mb-1 block text-sm text-text-mid">E-mail</label>
              <input
                className="input"
                type="email"
                value={editForm.email}
                onChange={(e) => setEditForm((f) => ({ ...f, email: e.target.value }))}
              />
            </div>
            <div>
              <label className="mb-1 block text-sm text-text-mid">Instagram</label>
              <input
                className="input"
                value={editForm.instagram}
                onChange={(e) => setEditForm((f) => ({ ...f, instagram: e.target.value }))}
              />
            </div>
            <div>
              <label className="mb-1 block text-sm text-text-mid">Meta Ad Account ID</label>
              <input
                className="input"
                placeholder="act_..."
                value={editForm.meta_ad_account_id}
                onChange={(e) =>
                  setEditForm((f) => ({ ...f, meta_ad_account_id: e.target.value }))
                }
              />
            </div>
            <div>
              <label className="mb-1 block text-sm text-text-mid">CPL alvo (R$)</label>
              <input
                className="input"
                value={editForm.meta_cpl_alvo}
                onChange={(e) => setEditForm((f) => ({ ...f, meta_cpl_alvo: e.target.value }))}
              />
            </div>
            <div>
              <label className="mb-1 block text-sm text-text-mid">Orçamento mensal (R$)</label>
              <input
                className="input"
                value={editForm.meta_orcamento_mensal}
                onChange={(e) =>
                  setEditForm((f) => ({ ...f, meta_orcamento_mensal: e.target.value }))
                }
              />
            </div>
            <div>
              <label className="mb-1 block text-sm text-text-mid">Leads alvo / mês</label>
              <input
                className="input"
                type="number"
                value={editForm.meta_leads_alvo_mensal}
                onChange={(e) =>
                  setEditForm((f) => ({ ...f, meta_leads_alvo_mensal: e.target.value }))
                }
              />
            </div>
            <div>
              <label className="mb-1 block text-sm text-text-mid">Ticket médio (R$)</label>
              <input
                className="input"
                type="number"
                value={editForm.ticket_medio_estimado}
                onChange={(e) =>
                  setEditForm((f) => ({ ...f, ticket_medio_estimado: e.target.value }))
                }
              />
            </div>
            <div className="sm:col-span-2 flex flex-wrap items-center gap-3">
              <button type="submit" className="btn-primary" disabled={salvandoDados}>
                {salvandoDados ? "Salvando..." : "Salvar dados"}
              </button>
              {prestador.meta_ultima_sync && (
                <p className="text-xs text-text-muted">
                  Último sync Meta: {new Date(prestador.meta_ultima_sync).toLocaleString("pt-BR")}
                </p>
              )}
            </div>
          </form>
        </div>

        <div className="card space-y-4 lg:col-span-2">
          <h2 className="font-display text-xl text-primary">Relatório IA + pauta</h2>
          <form onSubmit={gerarRelatorioIA} className="flex flex-wrap gap-2">
            <input
              className="input w-40"
              type="date"
              value={periodoInicio}
              onChange={(e) => setPeriodoInicio(e.target.value)}
            />
            <input
              className="input w-40"
              type="date"
              value={periodoFim}
              onChange={(e) => setPeriodoFim(e.target.value)}
            />
            <button type="submit" className="btn-primary" disabled={gerandoAnalise}>
              {gerandoAnalise ? "Gerando..." : "Gerar análise e pauta"}
            </button>
          </form>
          {relatorio?.dados_json?.analise ? (
            <div className="space-y-3 rounded-lg bg-bg-light p-4 text-sm">
              <div>
                <p className="font-medium text-primary">Análise</p>
                <p className="mt-1 whitespace-pre-wrap">{relatorio.dados_json.analise}</p>
              </div>
              {relatorio.dados_json.pauta_reuniao?.length ? (
                <div>
                  <p className="font-medium text-primary">Pauta de reunião</p>
                  <ul className="mt-1 list-inside list-disc">
                    {relatorio.dados_json.pauta_reuniao.map((item, i) => (
                      <li key={i}>{item}</li>
                    ))}
                  </ul>
                </div>
              ) : null}
              {relatorio.dados_json.acoes_cs?.length ? (
                <div>
                  <p className="font-medium text-primary">Ações CS</p>
                  <ul className="mt-1 list-inside list-disc">
                    {relatorio.dados_json.acoes_cs.map((item, i) => (
                      <li key={i}>{item}</li>
                    ))}
                  </ul>
                </div>
              ) : null}
            </div>
          ) : (
            <p className="text-sm text-text-mid">
              Nenhuma análise ainda. Informe o período e clique em gerar (requer Celery + chave
              Claude).
            </p>
          )}
        </div>

        <div className="card space-y-4 lg:col-span-2">
          <h2 className="font-display text-xl text-primary">Convites portal</h2>
          <form onSubmit={emitirConvite} className="flex flex-wrap gap-2">
            <input
              className="input max-w-xs"
              type="email"
              placeholder="email@exemplo.com"
              value={conviteEmail}
              onChange={(e) => setConviteEmail(e.target.value)}
              required
            />
            <select
              className="input w-44"
              value={conviteTipo}
              onChange={(e) => setConviteTipo(e.target.value)}
            >
              {CONVITE_TIPOS.map((t) => (
                <option key={t.value} value={t.value}>
                  {t.label}
                </option>
              ))}
            </select>
            <button type="submit" className="btn-primary">
              Emitir convite
            </button>
          </form>
          {convites.length === 0 ? (
            <p className="text-sm text-text-mid">Nenhum convite emitido.</p>
          ) : (
            <ul className="space-y-2 text-sm">
              {convites.map((c) => (
                <li
                  key={c.id}
                  className="flex flex-wrap items-center justify-between gap-2 border-b border-border py-2"
                >
                  <span>
                    {c.email} —{" "}
                    {CONVITE_TIPOS.find((t) => t.value === c.tipo)?.label ?? c.tipo} —{" "}
                    {labelConviteStatus(c.status)}
                  </span>
                  <span className="flex gap-2">
                    {c.status === "pendente" && (
                      <>
                        <button
                          type="button"
                          className="text-secondary hover:underline"
                          onClick={() => reenviarConvite(c.id)}
                        >
                          Reenviar
                        </button>
                        <button
                          type="button"
                          className="text-red-600 hover:underline"
                          onClick={() => revogarConvite(c.id)}
                        >
                          Revogar
                        </button>
                      </>
                    )}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="card space-y-4 lg:col-span-2">
          <h2 className="font-display text-xl text-primary">Membros com acesso</h2>
          {membros.length === 0 ? (
            <p className="text-sm text-text-mid">Nenhum membro ativo.</p>
          ) : (
            <ul className="space-y-2 text-sm">
              {membros.map((m) => (
                <li
                  key={m.id}
                  className="flex flex-wrap items-center justify-between gap-2 border-b border-border py-2"
                >
                  <span>
                    {m.usuario_email} — {m.tipo}
                  </span>
                  <button
                    type="button"
                    className="text-red-600 hover:underline"
                    onClick={() => revogarMembro(m.usuario)}
                  >
                    Revogar acesso
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </AppShell>
  );
}
