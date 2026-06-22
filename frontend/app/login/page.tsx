"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { toast } from "sonner";
import { apiFetch, setAuthMode, setTokens, setUserMeta } from "@/lib/api/client";
import type { LoginEquipeResponse } from "@/types/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await apiFetch<LoginEquipeResponse>("/api/v1/auth/login/", {
        method: "POST",
        body: JSON.stringify({ username: email, password: senha }),
      });
      setAuthMode("cs");
      setTokens(data.access, data.refresh);
      setUserMeta({ nome: data.nome, role: data.role, nivel: data.nivel_acesso });
      toast.success(`Bem-vindo, ${data.nome}`);
      router.push("/prestadores");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Falha no login.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <div className="card w-full max-w-md">
        <h1 className="font-display text-3xl font-semibold text-primary">MarryMe CS</h1>
        <p className="mt-2 text-sm text-text-mid">Acesso da equipe interna</p>
        <form onSubmit={handleSubmit} className="mt-8 space-y-4">
          <div>
            <label className="mb-1 block text-sm text-text-mid">E-mail</label>
            <input
              className="input"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="mb-1 block text-sm text-text-mid">Senha</label>
            <input
              className="input"
              type="password"
              value={senha}
              onChange={(e) => setSenha(e.target.value)}
              required
            />
          </div>
          <button type="submit" className="btn-primary w-full" disabled={loading}>
            {loading ? "Entrando..." : "Entrar"}
          </button>
        </form>
      </div>
    </div>
  );
}
