"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { AppShell } from "@/components/layout/AppShell";
import { apiFetch } from "@/lib/api/client";
import { labelHsStatus } from "@/lib/constants";

type PortalCampanhas = {
  health_score: { score: number; status: string } | null;
  metricas: Array<{ campanha_nome: string; leads: number; gasto: string; cpl: string }>;
};

export default function PortalCampanhasPage() {
  const [data, setData] = useState<PortalCampanhas | null>(null);

  useEffect(() => {
    apiFetch<PortalCampanhas>("/api/v1/portal/campanhas/")
      .then(setData)
      .catch((err) => toast.error(err.message));
  }, []);

  return (
    <AppShell variant="portal">
      <h1 className="mb-6 font-display text-3xl text-primary">Suas campanhas</h1>
      {!data && <p className="text-text-mid">Carregando...</p>}
      {data && (
        <div className="space-y-6">
          <div className="card">
            <h2 className="font-display text-xl">Health Score</h2>
            {data.health_score ? (
              <>
                <p className="mt-2 text-3xl font-semibold">{data.health_score.score}</p>
                <p className="mt-1 text-sm">
                  <span className="badge-hs-saudavel">{labelHsStatus(data.health_score.status)}</span>
                </p>
              </>
            ) : (
              <p className="mt-2 text-text-mid">Ainda não calculado.</p>
            )}
          </div>
          <div className="card">
            <h2 className="mb-4 font-display text-xl">Métricas recentes</h2>
            {data.metricas.length === 0 ? (
              <p className="text-text-mid">Sem métricas ainda.</p>
            ) : (
              <ul className="space-y-2 text-sm">
                {data.metricas.map((m, i) => (
                  <li key={i} className="flex justify-between border-b border-border py-2">
                    <span>{m.campanha_nome}</span>
                    <span>
                      {m.leads} leads · R$ {m.gasto}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}
    </AppShell>
  );
}
