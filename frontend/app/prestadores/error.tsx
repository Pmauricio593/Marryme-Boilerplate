"use client";

import { useEffect } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { ErrorFallback, logClientError, safeMessage } from "@/components/errors/ErrorFallback";

export default function PrestadoresError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    logClientError(error, "prestadores");
  }, [error]);

  return (
    <AppShell>
      <ErrorFallback
        message={safeMessage(error)}
        reset={reset}
        homeHref="/prestadores"
        homeLabel="Voltar aos prestadores"
      />
    </AppShell>
  );
}
