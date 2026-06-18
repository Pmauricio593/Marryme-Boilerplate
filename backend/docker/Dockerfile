FROM python:3.12-alpine

# Evita arquivos .pyc e garante logs em tempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# curl: healthcheck do compose; bash: entrypoint.sh
# psycopg2-binary já traz wheel — sem libpq-dev/gcc
RUN apk add --no-cache curl bash

# Instala dependências Python (base + dev para lint/test no container web)
COPY requirements/base.txt requirements/dev.txt ./
RUN pip install --no-cache-dir -r dev.txt

# Copia o código
COPY . .

# Copia e configura o entrypoint
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120"]