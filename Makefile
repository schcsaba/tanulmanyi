# Tanulmanyi Django Application - Docker Commands

.PHONY: help dev prod dev-up prod-up dev-down prod-down logs clean test test-faq test-szabalyzat test-verbose test-keepdb test-failfast test-coverage

help: ## Show this help message
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development Commands
dev-env: ## Copy development environment file
	@if [ ! -f .env.dev ]; then \
		cp env.dev .env.dev; \
		echo "✅ Created .env.dev - customize as needed"; \
	else \
		echo "⚠️ .env.dev already exists"; \
	fi

dev-up: dev-env ## Start development environment
	docker-compose up --build

dev-down: ## Stop development environment
	docker-compose down

dev-restart: dev-down dev-up ## Restart development environment

##@ Production Commands
prod-env: ## Copy production environment file
	@if [ ! -f .env.prod ]; then \
		cp env.prod .env.prod; \
		echo "🚨 Created .env.prod - MUST customize all values for production!"; \
	else \
		echo "⚠️ .env.prod already exists"; \
	fi

prod-up: prod-env ## Start production environment
	docker-compose -f docker-compose.prod.yml up --build

prod-down: ## Stop production environment
	docker-compose -f docker-compose.prod.yml down

prod-restart: prod-down prod-up ## Restart production environment

##@ Utility Commands
logs: ## View logs for development environment
	docker-compose logs -f

prod-logs: ## View logs for production environment
	docker-compose -f docker-compose.prod.yml logs -f

shell: ## Open Django shell in development
	docker-compose exec web python manage.py shell

prod-shell: ## Open Django shell in production
	docker-compose -f docker-compose.prod.yml exec web python manage.py shell

migrate: ## Run migrations in development
	docker-compose exec web python manage.py migrate

prod-migrate: ## Run migrations in production
	docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

collectstatic: ## Collect static files in development
	docker-compose exec web python manage.py collectstatic --noinput

prod-collectstatic: ## Collect static files in production
	docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

superuser: ## Create superuser in development
	docker-compose exec web python manage.py createsuperuser

prod-superuser: ## Create superuser in production
	docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

##@ Testing Commands
test: ## Run all tests in development
	docker-compose exec web python manage.py test

test-verbose: ## Run all tests with verbose output
	docker-compose exec web python manage.py test --verbosity=2

test-faq: ## Run FAQ module tests only
	docker-compose exec web python manage.py test faq.tests

test-szabalyzat: ## Run szabalyzat module tests only
	docker-compose exec web python manage.py test szabalyzat.tests

test-keepdb: ## Run all tests keeping the test database (faster for repeated runs)
	docker-compose exec web python manage.py test --keepdb

test-failfast: ## Run tests and stop on first failure
	docker-compose exec web python manage.py test --failfast

test-coverage: ## Run tests with coverage report (if coverage installed)
	@echo "Running tests with coverage..."
	@docker-compose exec web bash -c "if command -v coverage >/dev/null 2>&1; then \
		coverage run --source='.' manage.py test && coverage report -m; \
	else \
		echo '⚠️  Coverage not installed. Run: pip install coverage'; \
		python manage.py test; \
	fi"

##@ Cleanup Commands
clean: ## Stop containers and remove volumes
	docker-compose down -v
	docker-compose -f docker-compose.prod.yml down -v

clean-all: clean ## Remove all containers, networks, and images
	docker system prune -f
	docker volume prune -f

##@ Database Commands
db-backup: ## Backup development database
	docker-compose exec db mysqldump -u root -p${DB_ROOT_PASSWORD} ${DB_NAME} > backup_dev_$(shell date +%Y%m%d_%H%M%S).sql

prod-db-backup: ## Backup production database
	docker-compose -f docker-compose.prod.yml exec db mysqldump -u root -p${DB_ROOT_PASSWORD} ${DB_NAME} > backup_prod_$(shell date +%Y%m%d_%H%M%S).sql