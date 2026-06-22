"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { AppShell } from "@/components/layout/AppShell";
import { apiFetch } from "@/lib/api/client";
import { labelCategoria, labelFase, labelHsStatus } from "@/lib/constants";
import type { PortalPerfil } from "@/types/api";

function hsBadge(status: string | null) {
  if (status === "saudavel") return "badge-hs-saudavel";
  if (status === "atencao") return "badge-hs-atencao";
  if (status === "em_risco") return "badge-hs-risco";
  return "badge bg-gray-100 text-gray-600";
}

export default function PortalPerfilPage() {
  const [perfil, setPerfil] = useState<PortalPerfil | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch<PortalPerfil>("/api/v1/portal/perfil/")
      .then(setPerfil)
      .catch((err) => toast.error(err.message))
      .finally(() => setLoading(false));
  }, []);

  const hs = perfil?.health_score_atual;

  return (
    <AppShell variant="portal">
      {loading && <p className="text-text-mid">Carregando...</p>}
      {perfil && (
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="card max-w-lg">
            <h1 className="font-display text-3xl text-primary">{perfil.nome_artistico}</h1>
            <p className="mt-2 text-text-mid">
              {labelCategoria(perfil.categoria)} · {labelFase(perfil.fase)}
            </p>
            {(perfil.cidade || perfil.estado) && (
              <p className="mt-1 text-sm text-text-muted">
                {perfil.cidade}
                {perfil.cidade && perfil.estado ? "/" : ""}
                {perfil.estado}
              </p>
            )}
            {perfil.instagram && (
              <p className="mt-1 text-sm text-text-mid">@{perfil.instagram.replace(/^@/, "")}</p>
            )}
          </div>

          <div className="card space-y-3">
            <h2 className="font-display text-xl text-primary">Health Score</h2>
            {hs ? (
              <>
                <p className="text-4xl font-display font-semibold text-primary">{hs.score}</p>
                <p>
                  <span className={hsBadge(hs.status)}>{labelHsStatus(hs.status)}</span>
                </p>
                <p className="text-xs text-text-muted">
                  CPM {hs.breakdown.cpm} · Hook {hs.breakdown.hook_rate} · Retenção{" "}
                  {hs.breakdown.retencao} · CTR {hs.breakdown.ctr}
                </p>
                <p className="text-xs text-text-muted">
                  Atualizado em {new Date(hs.data).toLocaleDateString("pt-BR")}
                </p>
              </>
            ) : perfil.health_score != null ? (
              <p className="text-lg">
                {perfil.health_score}{" "}
                <span className={hsBadge(perfil.health_status)}>
                  {labelHsStatus(perfil.health_status)}
                </span>
              </p>
            ) : (
              <p className="text-text-mid">Ainda não calculado.</p>
            )}
          </div>

          <div className="card lg:col-span-2">
            <h2 className="mb-3 font-display text-xl text-primary">Resumo</h2>
            <div className="flex flex-wrap gap-6 text-sm">
              <p>
                <span className="text-text-muted">Sessões de roteiro:</span>{" "}
                <strong>{perfil.total_sessoes ?? 0}</strong>
              </p>
              <p>
                <span className="text-text-muted">Roteiros aprovados:</span>{" "}
                <strong>{perfil.roteiros_aprovados ?? 0}</strong>
              </p>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
}
