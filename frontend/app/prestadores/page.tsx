"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";
import { AppShell } from "@/components/layout/AppShell";
import { PaginationBar } from "@/components/ui/PaginationBar";
import { apiFetch } from "@/lib/api/client";
import { FASES, labelCategoria, labelFase, labelHsStatus } from "@/lib/constants";
import type { Paginated, PrestadorListItem } from "@/types/api";

function hsBadge(status: string | null) {
  if (status === "saudavel") return "badge-hs-saudavel";
  if (status === "atencao") return "badge-hs-atencao";
  if (status === "em_risco") return "badge-hs-risco";
  return "badge bg-gray-100 text-gray-600";
}

export default function PrestadoresPage() {
  const [data, setData] = useState<Paginated<PrestadorListItem> | null>(null);
  const [loading, setLoading] = useState(true);
  const [fase, setFase] = useState("");
  const [busca, setBusca] = useState("");
  const [pagina, setPagina] = useState(1);
  const [soRisco, setSoRisco] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (fase) params.set("fase", fase);
      if (busca) params.set("busca", busca);
      params.set("page", String(pagina));
      const res = await apiFetch<Paginated<PrestadorListItem>>(
        `/api/v1/prestadores/?${params.toString()}`,
      );
      setData(res);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Erro ao carregar.");
    } finally {
      setLoading(false);
    }
  }, [fase, busca, pagina]);

  useEffect(() => {
    load();
  }, [load]);

  const resultados =
    data?.resultados.filter((p) => !soRisco || p.health_status === "em_risco") ?? [];

  return (
    <AppShell>
      <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="font-display text-3xl font-semibold text-primary">Prestadores</h1>
          <p className="text-sm text-text-mid">Pipeline CS — quem precisa de atenção agora</p>
        </div>
        <Link href="/prestadores/novo" className="btn-primary">
          + Novo prestador
        </Link>
      </div>

      <div className="mb-4 flex flex-wrap gap-2">
        <input
          className="input w-48"
          placeholder="Buscar nome ou cidade"
          value={busca}
          onChange={(e) => {
            setBusca(e.target.value);
            setPagina(1);
          }}
        />
        <select
          className="input w-52"
          value={fase}
          onChange={(e) => {
            setFase(e.target.value);
            setPagina(1);
          }}
        >
          <option value="">Todas as fases</option>
          {FASES.map((f) => (
            <option key={f.value} value={f.value}>
              {f.label}
            </option>
          ))}
        </select>
        <label className="flex items-center gap-2 text-sm text-text-mid">
          <input
            type="checkbox"
            checked={soRisco}
            onChange={(e) => setSoRisco(e.target.checked)}
          />
          Só em risco
        </label>
      </div>

      {loading && <p className="text-text-mid">Carregando...</p>}

      {!loading && resultados.length === 0 && (
        <div className="card text-center text-text-mid">Nenhum prestador encontrado.</div>
      )}

      {!loading && resultados.length > 0 && (
        <div className="overflow-hidden rounded-card border border-border bg-white">
          <table className="w-full text-left text-sm">
            <thead className="border-b border-border bg-bg-light text-text-mid">
              <tr>
                <th className="px-4 py-3">Nome</th>
                <th className="px-4 py-3">Fase</th>
                <th className="px-4 py-3">Categoria</th>
                <th className="px-4 py-3">Cidade</th>
                <th className="px-4 py-3">Health Score</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody>
              {resultados.map((p) => (
                <tr key={p.id} className="border-b border-border last:border-0">
                  <td className="px-4 py-3 font-medium">{p.nome_artistico}</td>
                  <td className="px-4 py-3">{labelFase(p.fase)}</td>
                  <td className="px-4 py-3">{labelCategoria(p.categoria)}</td>
                  <td className="px-4 py-3">
                    {p.cidade}/{p.estado}
                  </td>
                  <td className="px-4 py-3">
                    {p.health_score != null ? (
                      <span className={hsBadge(p.health_status)}>
                        {p.health_score} — {labelHsStatus(p.health_status)}
                      </span>
                    ) : (
                      "—"
                    )}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Link href={`/prestadores/${p.id}`} className="text-secondary hover:underline">
                      Abrir
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {data && (
        <PaginationBar
          paginaAtual={data.pagina_atual}
          paginas={data.paginas}
          total={data.total}
          onPage={setPagina}
        />
      )}
    </AppShell>
  );
}
