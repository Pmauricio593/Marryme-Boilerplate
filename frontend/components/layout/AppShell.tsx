"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { clearTokens, getUserMeta } from "@/lib/api/client";

type PortalMeta = {
  permissoes_portal?: Record<string, boolean>;
};

type Props = {
  children: React.ReactNode;
  variant?: "cs" | "portal";
};

export function AppShell({ children, variant = "cs" }: Props) {
  const base = variant === "cs" ? "/prestadores" : "/portal/perfil";
  const [permissoes, setPermissoes] = useState<Record<string, boolean>>({});

  useEffect(() => {
    if (variant === "portal") {
      const meta = getUserMeta<PortalMeta>();
      setPermissoes(meta?.permissoes_portal ?? {});
    }
  }, [variant]);

  const podeCampanhas = variant !== "portal" || permissoes.campanhas !== false;
  const podeRoteiros = variant !== "portal" || permissoes.roteiros !== false;

  return (
    <div className="min-h-screen">
      <header className="border-b border-border bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4">
          <Link href={base} className="font-display text-2xl font-semibold text-primary">
            MarryMe
          </Link>
          <nav className="flex items-center gap-4 text-sm text-text-mid">
            {variant === "cs" && (
              <Link href="/prestadores" className="hover:text-primary">
                Prestadores
              </Link>
            )}
            {variant === "portal" && (
              <>
                <Link href="/portal/perfil" className="hover:text-primary">
                  Perfil
                </Link>
                {podeCampanhas && (
                  <Link href="/portal/campanhas" className="hover:text-primary">
                    Campanhas
                  </Link>
                )}
                {podeRoteiros && (
                  <Link href="/portal/roteiros" className="hover:text-primary">
                    Roteiros
                  </Link>
                )}
              </>
            )}
            <button
              type="button"
              className="btn-secondary"
              onClick={() => {
                clearTokens();
                window.location.href = variant === "cs" ? "/login" : "/portal/login";
              }}
            >
              Sair
            </button>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-8">{children}</main>
    </div>
  );
}
