# Docker Deployment Guide

## Prerequisites

- Docker installed
- Docker Compose installed
- `.env` file configured with all required credentials

## Quick Start

### 1. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required variables:
- `OPENAI_API_KEY` - Your OpenAI API key
- `GOOGLE_SHEETS_SPREADSHEET_ID` - Your Google Sheets ID
- `GOOGLE_SHEETS_CREDS` - JSON string of service account credentials
- `APP_SECRET_KEY` - Random secret key for Flask sessions

### 2. Build and Run

```bash
# Build the Docker image
docker-compose build

# Start the application
docker-compose up -d

# View logs
docker-compose logs -f
```

The application will be available at `http://localhost:5001`

### 3. Stop the Application

```bash
docker-compose down
```

To also remove volumes (session data):
```bash
docker-compose down -v
```

## Production Deployment

### Using Docker Compose

For production, update `docker-compose.yml`:

1. **Change port binding** if needed:
   ```yaml
   ports:
     - "80:5001"  # Map to port 80
   ```

2. **Add reverse proxy** (recommended):
   - Use Nginx or Traefik as reverse proxy
   - Enable HTTPS with Let's Encrypt
   - Add rate limiting

3. **Set production environment**:
   ```yaml
   environment:
     - FLASK_ENV=production
   ```

### Environment Variables

Pass environment variables in production:

```bash
# Option 1: Use .env file
docker-compose --env-file .env.production up -d

# Option 2: Set in docker-compose.yml
# (see docker-compose.yml for all available variables)
```

### Health Check

Add to `docker-compose.yml`:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5001/"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

## Updating the Application

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build
```

## Troubleshooting

### View logs
```bash
docker-compose logs -f idea_factory
```

### Access container shell
```bash
docker-compose exec idea_factory /bin/bash
```

### Check environment variables
```bash
docker-compose exec idea_factory env
```

### Restart application
```bash
docker-compose restart idea_factory
```

## Backup

### Backup session data
```bash
docker run --rm -v idea_factory_idea_factory_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/session_backup.tar.gz -C /data .
```

### Restore session data
```bash
docker run --rm -v idea_factory_idea_factory_data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/session_backup.tar.gz -C /data
```

## Integration with Existing Services

If you have other services in docker-compose, add to the same network:

```yaml
networks:
  default:
    external:
      name: your_existing_network
```

## Performance Tuning

For production, consider:

1. **Use Gunicorn** instead of Flask dev server:
   ```dockerfile
   CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "app:app"]
   ```
   Add `gunicorn` to `requirements.txt`

2. **Add Redis** for session storage (optional)

3. **Set resource limits** in docker-compose.yml:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '1'
         memory: 512M
   ```
