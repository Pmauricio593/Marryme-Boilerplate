"use client";

import Link from "next/link";

type Props = {
  title?: string;
  message?: string;
  reset?: () => void;
  homeHref?: string;
  homeLabel?: string;
};

export function ErrorFallback({
  title = "Algo deu errado",
  message = "Ocorreu um erro inesperado. Tente novamente ou volte para a página inicial.",
  reset,
  homeHref = "/",
  homeLabel = "Ir para início",
}: Props) {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center px-4 text-center">
      <div className="card max-w-md space-y-4">
        <h1 className="font-display text-2xl text-primary">{title}</h1>
        <p className="text-sm text-text-mid">{message}</p>
        <div className="flex flex-wrap justify-center gap-3 pt-2">
          {reset && (
            <button type="button" className="btn-primary" onClick={reset}>
              Tentar novamente
            </button>
          )}
          <Link href={homeHref} className="btn-secondary inline-block">
            {homeLabel}
          </Link>
        </div>
      </div>
    </div>
  );
}

function safeMessage(error: Error): string {
  if (process.env.NODE_ENV === "development") {
    return error.message || "Erro desconhecido.";
  }
  return "Ocorreu um erro inesperado. Tente novamente.";
}

export function logClientError(error: Error, context?: string) {
  if (process.env.NODE_ENV === "development") {
    console.error(context ? `[${context}]` : "[error]", error);
  }
}

export { safeMessage };
