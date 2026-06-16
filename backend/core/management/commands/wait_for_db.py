import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = 'Aguarda o banco de dados ficar disponível'

    def handle(self, *args, **options):
        self.stdout.write('Aguardando banco de dados...')
        attempts = 0
        while True:
            try:
                conn = connections['default']
                conn.ensure_connection()
                self.stdout.write(self.style.SUCCESS('Banco disponível!'))
                break
            except OperationalError:
                attempts += 1
                self.stdout.write(f'Tentativa {attempts} — aguardando 2s...')
                time.sleep(2)
