# Docker Setup for Tanulmanyi Django Application

This guide explains how to run the Tanulmanyi Django application using Docker and Docker Compose.

## Prerequisites

- Docker
- Docker Compose

## Quick Start

1. **Clone the repository** (if not already done)

2. **Set up environment file**
   For development, copy the development environment template:

   ```bash
   cp env.dev .env.dev
   ```

   Or for production:

   ```bash
   cp env.prod .env.prod
   ```

   Then customize the values as needed. The development template includes safe defaults for local development.

3. **Build and start the services**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Django app: http://localhost:8000
   - MySQL database: localhost:3306

## Services

### Web Service (Django)
- **Container**: `tanulmanyi_web`
- **Port**: 8000
- **Volume mounts**:
  - Source code: `.:/app`
  - Static files: `static_volume:/app/static`
  - Media files: `media_volume:/app/media`

### Database Service (MySQL)
- **Container**: `tanulmanyi_db`
- **Port**: 3306
- **Volume**: `mysql_data:/var/lib/mysql`

## Environment Variables

### Required Variables
- `SECRET_KEY`: Django secret key
- `DB_NAME`: Database name
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password
- `DB_ROOT_PASSWORD`: MySQL root password
- `ALLOWED_HOST`: Allowed hostname for Django

### Optional Variables
- `DEBUG`: Enable/disable debug mode (default: True)
- `SECURE_SSL_REDIRECT`: Enable SSL redirect (default: False for development)

## Common Commands

We've included a Makefile to simplify common operations:

### Quick Commands
```bash
# Development
make dev-up          # Start development environment
make dev-down        # Stop development environment
make logs           # View development logs

# Production  
make prod-up        # Start production environment
make prod-down      # Stop production environment
make prod-logs      # View production logs

# See all available commands
make help
```

### Manual Docker Commands
```bash
# Development
docker-compose up --build
docker-compose down
docker-compose logs -f

# Production
docker-compose -f docker-compose.prod.yml up --build
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml logs -f
```

### Execute commands in containers
```bash
# Django shell
docker-compose exec web python manage.py shell

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Run migrations
docker-compose exec web python manage.py migrate

# Collect static files
docker-compose exec web python manage.py collectstatic
```

### Database operations
```bash
# Access MySQL shell
docker-compose exec db mysql -u root -p tanulmanyi

# Backup database
docker-compose exec db mysqldump -u root -p tanulmanyi > backup.sql

# Restore database
docker-compose exec -T db mysql -u root -p tanulmanyi < backup.sql
```

## Development Workflow

1. **Code changes**: The source code is mounted as a volume, so changes are reflected immediately
2. **Database changes**: Run migrations using the command above
3. **Static files**: Collect static files if you add new ones

## Production Deployment

For production deployment, consider:

1. **Environment variables**: Set production values
   ```bash
   DEBUG=False
   ALLOWED_HOST=yourdomain.com
   SECURE_SSL_REDIRECT=True
   ```

2. **Use a reverse proxy**: Add nginx or similar
3. **Use environment-specific docker-compose files**
4. **Set up proper secrets management**
5. **Configure logging and monitoring**

## Troubleshooting

### Database connection issues
- Ensure the database container is running: `docker-compose ps`
- Check database logs: `docker-compose logs db`

### Permission issues
```bash
# Fix static/media directory permissions
sudo chown -R $(whoami):$(whoami) static/ media/
```

### Clean restart
```bash
# Stop and remove containers, networks, volumes
docker-compose down -v
docker-compose up --build
```

## File Structure

```
.
├── Dockerfile              # Django app container definition
├── docker-compose.yml      # Service orchestration
├── docker-entrypoint.sh    # Container startup script
├── .dockerignore           # Files to exclude from build
└── DOCKER_README.md        # This file
```

## Notes

- The application uses MySQL 8.0
- Static and media files are stored in Docker volumes
- The entrypoint script automatically runs migrations and collects static files
- Development server runs on 0.0.0.0:8000 inside the container