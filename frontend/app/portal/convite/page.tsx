"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { FormEvent, Suspense, useEffect, useState } from "react";
import { toast } from "sonner";
import { apiFetch, setAuthMode, setTokens, setUserMeta } from "@/lib/api/client";
import type { PortalLoginResponse } from "@/types/api";

function ConviteContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const token = searchParams.get("token") || "";
  const [valido, setValido] = useState<boolean | null>(null);
  const [prestadorNome, setPrestadorNome] = useState("");
  const [senha, setSenha] = useState("");
  const [nome, setNome] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!token) return;
    apiFetch<{
      valido: boolean;
      prestador_nome: string;
      erro?: string;
    }>(`/api/v1/portal/convites/validar/?token=${encodeURIComponent(token)}`)
      .then((r) => {
        setValido(r.valido);
        setPrestadorNome(r.prestador_nome || "");
        if (!r.valido) toast.error(r.erro || "Convite inválido.");
      })
      .catch((err) => toast.error(err.message));
  }, [token]);

  async function aceitar(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await apiFetch<PortalLoginResponse>("/api/v1/portal/convites/aceitar/", {
        method: "POST",
        body: JSON.stringify({ token, senha, nome }),
      });
      setAuthMode("portal");
      setTokens(data.access, data.refresh);
      setUserMeta({
        nome: data.nome,
        role: data.role,
        permissoes_portal: data.permissoes_portal,
      });
      toast.success("Conta criada!");
      router.push("/portal/perfil");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Erro ao aceitar convite.");
    } finally {
      setLoading(false);
    }
  }

  if (!token) {
    return (
      <div className="card max-w-md text-center">
        <p>Link de convite inválido.</p>
        <Link href="/portal/login" className="mt-4 inline-block text-secondary">
          Ir para login
        </Link>
      </div>
    );
  }

  if (valido === null) return <p className="text-text-mid">Validando convite...</p>;
  if (!valido) return <p className="text-text-mid">Convite inválido ou expirado.</p>;

  return (
    <div className="card w-full max-w-md">
      <h1 className="font-display text-2xl text-primary">Aceitar convite</h1>
      <p className="mt-2 text-sm text-text-mid">Prestador: {prestadorNome}</p>
      <form onSubmit={aceitar} className="mt-6 space-y-4">
        <div>
          <label className="mb-1 block text-sm">Seu nome</label>
          <input className="input" value={nome} onChange={(e) => setNome(e.target.value)} />
        </div>
        <div>
          <label className="mb-1 block text-sm">Crie sua senha</label>
          <input
            className="input"
            type="password"
            minLength={8}
            value={senha}
            onChange={(e) => setSenha(e.target.value)}
            required
          />
        </div>
        <button type="submit" className="btn-primary w-full" disabled={loading}>
          {loading ? "Criando..." : "Criar acesso"}
        </button>
      </form>
    </div>
  );
}

export default function PortalConvitePage() {
  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <Suspense fallback={<p>Carregando...</p>}>
        <ConviteContent />
      </Suspense>
    </div>
  );
}
