import time

from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = "Aguarda o banco de dados ficar disponível"

    def add_arguments(self, parser):
        parser.add_argument(
            "--max-attempts",
            type=int,
            default=90,
            help="Tentativas antes de falhar (padrão 90 × 2s ≈ 3 min)",
        )

    def handle(self, *args, **options):
        max_attempts = options["max_attempts"]
        self.stdout.write("Aguardando banco de dados...")
        for attempt in range(1, max_attempts + 1):
            try:
                conn = connections["default"]
                conn.ensure_connection()
                self.stdout.write(self.style.SUCCESS("Banco disponível!"))
                return
            except OperationalError:
                if attempt >= max_attempts:
                    self.stderr.write(
                        self.style.ERROR(
                            f"Banco indisponível após {max_attempts} tentativas. "
                            "Verifique DATABASE_URL no serviço web."
                        )
                    )
                    raise SystemExit(1) from None
                self.stdout.write(f"Tentativa {attempt}/{max_attempts} — aguardando 2s...")
                time.sleep(2)
