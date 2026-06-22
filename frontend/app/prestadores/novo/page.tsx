"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { toast } from "sonner";
import { AppShell } from "@/components/layout/AppShell";
import { apiFetch } from "@/lib/api/client";
import { CATEGORIAS } from "@/lib/constants";
import type { PrestadorDetail } from "@/types/api";

export default function NovoPrestadorPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    nome_artistico: "",
    nome_completo: "",
    categoria: "musico",
    cidade: "",
    estado: "",
    whatsapp: "",
    email: "",
    instagram: "",
  });

  function update(field: string, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const p = await apiFetch<PrestadorDetail>("/api/v1/prestadores/", {
        method: "POST",
        body: JSON.stringify(form),
      });
      toast.success("Prestador criado.");
      router.push(`/prestadores/${p.id}`);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Erro ao criar.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppShell>
      <Link href="/prestadores" className="text-sm text-secondary hover:underline">
        ← Voltar
      </Link>
      <h1 className="mt-2 font-display text-3xl font-semibold text-primary">Novo prestador</h1>
      <p className="mb-6 text-sm text-text-mid">Cadastro mínimo para iniciar onboarding.</p>

      <form onSubmit={handleSubmit} className="card max-w-xl space-y-4">
        <div>
          <label className="mb-1 block text-sm text-text-mid">Nome artístico</label>
          <input
            className="input"
            value={form.nome_artistico}
            onChange={(e) => update("nome_artistico", e.target.value)}
            required
          />
        </div>
        <div>
          <label className="mb-1 block text-sm text-text-mid">Nome completo</label>
          <input
            className="input"
            value={form.nome_completo}
            onChange={(e) => update("nome_completo", e.target.value)}
            required
          />
        </div>
        <div>
          <label className="mb-1 block text-sm text-text-mid">Categoria</label>
          <select
            className="input"
            value={form.categoria}
            onChange={(e) => update("categoria", e.target.value)}
          >
            {CATEGORIAS.map((c) => (
              <option key={c.value} value={c.value}>
                {c.label}
              </option>
            ))}
          </select>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-1 block text-sm text-text-mid">Cidade</label>
            <input
              className="input"
              value={form.cidade}
              onChange={(e) => update("cidade", e.target.value)}
              required
            />
          </div>
          <div>
            <label className="mb-1 block text-sm text-text-mid">Estado (UF)</label>
            <input
              className="input"
              maxLength={2}
              value={form.estado}
              onChange={(e) => update("estado", e.target.value.toUpperCase())}
              required
            />
          </div>
        </div>
        <div>
          <label className="mb-1 block text-sm text-text-mid">WhatsApp</label>
          <input
            className="input"
            value={form.whatsapp}
            onChange={(e) => update("whatsapp", e.target.value)}
            required
          />
        </div>
        <div>
          <label className="mb-1 block text-sm text-text-mid">E-mail (opcional)</label>
          <input
            className="input"
            type="email"
            value={form.email}
            onChange={(e) => update("email", e.target.value)}
          />
        </div>
        <div>
          <label className="mb-1 block text-sm text-text-mid">Instagram (opcional)</label>
          <input
            className="input"
            value={form.instagram}
            onChange={(e) => update("instagram", e.target.value)}
          />
        </div>
        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? "Salvando..." : "Criar prestador"}
        </button>
      </form>
    </AppShell>
  );
}
