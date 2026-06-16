#!/bin/bash
set -e

echo "Aguardando banco de dados..."
python manage.py wait_for_db

exec "$@"
