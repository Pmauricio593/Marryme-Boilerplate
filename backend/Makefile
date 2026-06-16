.PHONY: build up down shell migrate migrations test logs

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

logs:
	docker compose logs -f web

logs-celery:
	docker compose logs -f celery