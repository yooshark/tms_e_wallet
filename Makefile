.PHONY: format
format:
	poetry run black .
	ruff . --fix
	poetry run ruff . --fix --exit-zero
	poetry run pre-commit run --all
	poetry run mypy .

up:
	docker compose -f docker-compose.yml up -d

down:
	docker compose -f docker-compose.yml down

server:
	cd backend && ./manage.py migrate && ./manage.py runserver

lint:
	poetry run ruff .
	poetry run mypy .

test:
	poetry run coverage run -m pytest
	poetry run coverage report
