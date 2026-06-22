"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { AppShell } from "@/components/layout/AppShell";
import { ApiError, apiFetch } from "@/lib/api/client";
import { labelRoteiroTipo } from "@/lib/constants";

type PortalRoteiros = {
  roteiros: Array<{ id: string; tipo: string; conteudo_json: Record<string, unknown> }>;
  sessoes_recentes: Array<{ id: string; titulo: string; status: string }>;
};

export default function PortalRoteirosPage() {
  const [data, setData] = useState<PortalRoteiros | null>(null);
  const [semPermissao, setSemPermissao] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch<PortalRoteiros>("/api/v1/portal/roteiros/")
      .then(setData)
      .catch((err) => {
        if (err instanceof ApiError && err.status === 403) {
          setSemPermissao(true);
          return;
        }
        toast.error(err.message);
      })
      .finally(() => setLoading(false));
  }, []);

  if (semPermissao) {
    return (
      <AppShell variant="portal">
        <div className="card max-w-lg">
          <h1 className="font-display text-2xl text-primary">Roteiros</h1>
          <p className="mt-3 text-text-mid">
            Seu perfil de assessoria não tem permissão para ver roteiros. Fale com a equipe MarryMe
            se precisar desse acesso.
          </p>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell variant="portal">
      <h1 className="mb-6 font-display text-3xl text-primary">Seus roteiros</h1>
      {loading && <p className="text-text-mid">Carregando...</p>}
      {data && (
        <div className="space-y-6">
          <div className="card">
            <h2 className="mb-4 font-display text-xl">Roteiros aprovados</h2>
            {data.roteiros.length === 0 ? (
              <p className="text-text-mid">Nenhum roteiro aprovado ainda.</p>
            ) : (
              <ul className="space-y-3">
                {data.roteiros.map((r) => (
                  <li key={r.id} className="rounded-lg border border-border p-3 text-sm">
                    <p className="font-medium">{labelRoteiroTipo(r.tipo)}</p>
                    {"texto" in r.conteudo_json && typeof r.conteudo_json.texto === "string" ? (
                      <p className="mt-2 whitespace-pre-wrap text-text-mid">
                        {r.conteudo_json.texto}
                      </p>
                    ) : (
                      <pre className="mt-2 whitespace-pre-wrap text-text-mid">
                        {JSON.stringify(r.conteudo_json, null, 2)}
                      </pre>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>

          {data.sessoes_recentes.length > 0 && (
            <div className="card">
              <h2 className="mb-4 font-display text-xl">Sessões recentes</h2>
              <ul className="space-y-2 text-sm text-text-mid">
                {data.sessoes_recentes.map((s) => (
                  <li key={s.id} className="border-b border-border py-2">
                    {s.titulo} — {s.status.replace("_", " ")}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </AppShell>
  );
}
