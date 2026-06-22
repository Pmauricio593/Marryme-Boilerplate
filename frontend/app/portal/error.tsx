"use client";

import { useEffect } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { ErrorFallback, logClientError, safeMessage } from "@/components/errors/ErrorFallback";

export default function PortalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    logClientError(error, "portal");
  }, [error]);

  return (
    <AppShell variant="portal">
      <ErrorFallback
        message={safeMessage(error)}
        reset={reset}
        homeHref="/portal/perfil"
        homeLabel="Voltar ao perfil"
      />
    </AppShell>
  );
}
