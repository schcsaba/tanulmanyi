# Tanulmanyi Django Application

A Django-based student management system with course planning, schedule management, thesis tracking, and administrative features.

## Quick Start with Docker 🐳

The easiest way to run this application is using Docker:

1. **Set up environment file**:
   ```bash
   # For development
   cp env.dev .env.dev
   
   # For production
   cp env.prod .env.prod
   ```

2. **Start the application**:
   ```bash
   # Using Makefile (recommended)
   make dev-up
   
   # Or manually
   docker-compose up --build
   ```

3. **Access the application**:
   - Web interface: http://localhost:8000
   - Admin interface: http://localhost:8000/admin

For detailed Docker setup instructions, see [DOCKER_README.md](DOCKER_README.md).

## Traditional Setup

If you prefer to run without Docker, you'll need:
- Python 3.11+
- MySQL 8.0+
- Virtual environment

1. Install dependencies: `pip install -r requirements.txt`
2. Configure environment variables (see `env.example`)
3. Run migrations: `python manage.py migrate`
4. Start server: `python manage.py runserver`

## Features

- **Course Management** (`mintatanterv`): Academic program and course planning
- **Schedule Management** (`orarend`): Timetable and calendar functionality  
- **Thesis Management** (`szakdolgozat`): Student thesis tracking and supervision
- **FAQ System** (`faq`): Frequently asked questions management
- **Document Management** (`szabalyzat`): Regulations and policy documents

## Production Deployment

For production deployment with Docker:
```bash
# Using Makefile (recommended)
make prod-up

# Or manually
docker-compose -f docker-compose.prod.yml up --build
```

See [DOCKER_README.md](DOCKER_README.md) for comprehensive deployment instructions.
