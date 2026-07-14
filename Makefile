.PHONY: help install migrate superuser run test lint format shell clean

help: ## Mostrar esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Instalar dependencias de desarrollo
	pip install -r requirements/dev.txt

migrate: ## Ejecutar migraciones
	python manage.py migrate

makemigrations: ## Crear migraciones nuevas
	python manage.py makemigrations

superuser: ## Crear superusuario
	python manage.py createsuperuser

run: ## Levantar servidor de desarrollo
	python manage.py runserver

test: ## Ejecutar tests con pytest
	pytest

test-cov: ## Ejecutar tests con cobertura
	pytest --cov=apps --cov-report=html

lint: ## Verificar código con ruff
	ruff check .

format: ## Formatear código con ruff
	ruff format .
	ruff check --fix .

shell: ## Abrir shell interactivo de Django
	python manage.py shell

check: ## Verificar configuración de Django
	python manage.py check

clean: ## Limpiar archivos generados
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf htmlcov .coverage .pytest_cache .ruff_cache
