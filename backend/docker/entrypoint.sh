#!/bin/bash
set -e

echo "=== MarryMe backend startup (PORT=${PORT:-8000}) ==="

echo "Aguardando banco de dados..."
python manage.py wait_for_db --max-attempts 90

echo "Aplicando migrations..."
python manage.py migrate --noinput

echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "Iniciando gunicorn em 0.0.0.0:${PORT:-8000}..."
if [ $# -gt 0 ]; then
  exec "$@"
fi

exec gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers 2 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
