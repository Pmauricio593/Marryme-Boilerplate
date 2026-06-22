"use client";

import { useEffect } from "react";
import { ErrorFallback, logClientError, safeMessage } from "@/components/errors/ErrorFallback";
import "./globals.css";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    logClientError(error, "global");
  }, [error]);

  return (
    <html lang="pt-BR">
      <body className="bg-bg-light font-sans antialiased">
        <ErrorFallback
          title="Erro crítico"
          message={safeMessage(error)}
          reset={reset}
          homeHref="/login"
          homeLabel="Ir para login"
        />
      </body>
    </html>
  );
}
