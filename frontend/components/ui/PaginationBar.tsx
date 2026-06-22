type Props = {
  paginaAtual: number;
  paginas: number;
  total: number;
  onPage: (page: number) => void;
};

export function PaginationBar({ paginaAtual, paginas, total, onPage }: Props) {
  if (paginas <= 1) return null;

  return (
    <div className="mt-4 flex flex-wrap items-center justify-between gap-2 text-sm text-text-mid">
      <span>
        {total} registro{total !== 1 ? "s" : ""} · página {paginaAtual} de {paginas}
      </span>
      <div className="flex gap-2">
        <button
          type="button"
          className="btn-secondary"
          disabled={paginaAtual <= 1}
          onClick={() => onPage(paginaAtual - 1)}
        >
          Anterior
        </button>
        <button
          type="button"
          className="btn-secondary"
          disabled={paginaAtual >= paginas}
          onClick={() => onPage(paginaAtual + 1)}
        >
          Próxima
        </button>
      </div>
    </div>
  );
}
