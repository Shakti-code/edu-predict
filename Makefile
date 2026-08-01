.PHONY: help up down logs shell migrate createsuperuser test clean

# Default target
help:
	@echo "EduPredict Makefile"
	@echo "==================="
	@echo "Commands:"
	@echo "  make up               - Start the Docker production stack"
	@echo "  make down             - Stop the Docker stack"
	@echo "  make logs             - View logs from the web container"
	@echo "  make shell            - Open a bash shell in the web container"
	@echo "  make migrate          - Run Django migrations in the web container"
	@echo "  make createsuperuser  - Create a Django superuser"
	@echo "  make test             - Run Django tests in the web container"
	@echo "  make clean            - Remove all Docker volumes and clean pyc files"

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f web

shell:
	docker compose exec web /bin/bash

migrate:
	docker compose exec web python manage.py migrate

createsuperuser:
	docker compose exec web python manage.py createsuperuser

test:
	docker compose exec web python manage.py test

clean:
	docker compose down -v
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
