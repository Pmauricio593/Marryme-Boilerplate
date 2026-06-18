.PHONY: build up down shell migrate migrations test pytest lint format cov logs createsuperuser

build:
	docker compose build

up:
	docker compose up

upd:
	docker compose up -d

down:
	docker compose down

shell:
	docker compose exec web python manage.py shell

migrate:
	docker compose exec web python manage.py migrate

migrations:
	docker compose exec web python manage.py makemigrations

createsuperuser:
	docker compose exec web python manage.py createsuperuser

test:
	docker compose exec web python manage.py test

pytest:
	docker compose exec web pytest

lint:
	docker compose exec web ruff check .
	docker compose exec web black --check .

format:
	docker compose exec web ruff check . --fix
	docker compose exec web black .

cov:
	docker compose exec web pytest --cov=apps --cov=core --cov-report=term-missing

logs:
	docker compose logs -f web

logs-celery:
	docker compose logs -f celery
