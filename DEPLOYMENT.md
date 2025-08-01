# 🚀 Deployment Guide - Aegis Financial Intelligence

This guide covers all deployment scenarios for the Aegis Financial Intelligence platform, from local development to production environments.

## 📋 **Prerequisites**

### System Requirements
- **RAM**: 4GB minimum, 8GB recommended
- **CPU**: 2+ cores recommended for optimal performance
- **Storage**: 2GB free space for Docker images and data
- **Network**: Internet access for API calls and model downloads

### Required Software
- **Docker**: Version 20.0+ with Docker Compose v2
- **Git**: For cloning the repository
- **Modern Browser**: Chrome, Firefox, Safari, or Edge for web interface

### API Keys
- **OpenAI API Key**: Required for agent reasoning (GPT-4o-mini)
- **Tavily API Key**: Required for real-time web search
- **Gemini API Key**: Optional, only needed if enabling 10K document analysis

## 🏠 **Local Development**

### Quick Start
```bash
# Clone repository
git clone <your-repo-url>
cd multi-10-k

# Set environment variables
export OPENAI_API_KEY="sk-your-openai-key"
export TAVILY_API_KEY="tvly-your-tavily-key"
export GEMINI_API_KEY="your-gemini-key"  # Optional

# Launch web interface
docker compose --profile api up -d

# Access interface
open http://localhost:8000
```

### Development Mode (with hot reload)
```bash
# Install dependencies locally
pip install -r requirements.txt

# Run web interface with auto-reload
cd app/
uvicorn api:app --reload --host 0.0.0.0 --port 8000

# Or run CLI mode for testing
python main.py
```

### Database Setup
```bash
# Initialize SQL database with sample data
python app/db_setup.py

# Enable 10K document analysis (optional)
docker compose --profile ingest up
ENABLE_10K_RAG=true docker compose --profile api up -d
```

## 🌐 **Production Deployment**

### Docker Compose (Recommended)

#### 1. Environment Configuration
Create a `.env` file:
```bash
# Required API Keys
OPENAI_API_KEY=sk-your-actual-openai-key
TAVILY_API_KEY=tvly-your-actual-tavily-key

# Optional Configuration
GEMINI_API_KEY=your-gemini-key
ENABLE_10K_RAG=false
MOCK_MODE=false

# Docker Configuration
CHROMA_HOST=chromadb
```

#### 2. Production Docker Compose
Create `docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  aegis-api:
    build:
      context: .
      dockerfile: Dockerfile.api
    container_name: aegis_financial_api
    restart: unless-stopped
    ports:
      - "80:8000"  # Production port
    volumes:
      - ./app:/app
      - app_data:/app/data
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - TAVILY_API_KEY=${TAVILY_API_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - ENABLE_10K_RAG=${ENABLE_10K_RAG:-false}
      - CHROMA_HOST=chromadb
    depends_on:
      - chromadb
    command: ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  chromadb:
    image: chromadb/chroma:0.5.3
    container_name: aegis_chromadb
    restart: unless-stopped
    ports:
      - "8001:8000"
    volumes:
      - chroma_data:/chroma/.chroma/index
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/heartbeat"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    container_name: aegis_nginx
    restart: unless-stopped
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - aegis-api

volumes:
  chroma_data:
  app_data:
```

#### 3. Launch Production Environment
```bash
# Deploy to production
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f aegis-api
```

### Nginx Configuration (Optional)

Create `nginx.conf` for SSL and load balancing:
```nginx
events {
    worker_connections 1024;
}

http {
    upstream aegis_backend {
        server aegis-api:8000;
    }

    # HTTP redirect to HTTPS
    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        location / {
            proxy_pass http://aegis_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        # Static files
        location /static/ {
            proxy_pass http://aegis_backend;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

## ☁️ **Cloud Deployment**

### AWS ECS Deployment

#### 1. Create Task Definition
```json
{
  "family": "aegis-financial-intelligence",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "aegis-api",
      "image": "your-registry/aegis-financial:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "OPENAI_API_KEY",
          "value": "your-openai-key"
        },
        {
          "name": "TAVILY_API_KEY", 
          "value": "your-tavily-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/aegis-financial",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### 2. Deploy with ECS CLI
```bash
# Build and push image
docker build -t aegis-financial .
docker tag aegis-financial:latest your-registry/aegis-financial:latest
docker push your-registry/aegis-financial:latest

# Deploy to ECS
aws ecs create-service \
    --cluster your-cluster \
    --service-name aegis-financial \
    --task-definition aegis-financial-intelligence \
    --desired-count 2 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
```

### Google Cloud Run

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/your-project/aegis-financial .

gcloud run deploy aegis-financial \
    --image gcr.io/your-project/aegis-financial \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars OPENAI_API_KEY=your-key,TAVILY_API_KEY=your-key \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 10
```

### Azure Container Instances

```bash
# Create resource group
az group create --name aegis-rg --location eastus

# Deploy container
az container create \
    --resource-group aegis-rg \
    --name aegis-financial \
    --image your-registry/aegis-financial:latest \
    --cpu 2 \
    --memory 4 \
    --ports 8000 \
    --dns-name-label aegis-financial \
    --environment-variables \
        OPENAI_API_KEY=your-key \
        TAVILY_API_KEY=your-key
```

## 🔧 **Configuration Management**

### Environment Variables

#### Production Environment
```bash
# Core API Keys (Required)
OPENAI_API_KEY=sk-prod-key-here
TAVILY_API_KEY=tvly-prod-key-here

# Optional Features
GEMINI_API_KEY=gemini-prod-key-here
ENABLE_10K_RAG=true

# Performance Settings
MAX_WORKERS=4
TIMEOUT=60
MAX_ITERATIONS=6

# Database Configuration
CHROMA_HOST=production-chroma-host
DATABASE_PATH=/app/data/financials.db

# Security Settings
ALLOWED_HOSTS=your-domain.com,api.your-domain.com
CORS_ORIGINS=https://your-domain.com
```

#### Development Environment
```bash
# Development API Keys
OPENAI_API_KEY=sk-dev-key-here
TAVILY_API_KEY=tvly-dev-key-here

# Development Settings
ENABLE_10K_RAG=false
MOCK_MODE=false
DEBUG=true

# Local Database
CHROMA_HOST=localhost
DATABASE_PATH=./financials.db
```

### Docker Environment Files

Create environment-specific files:

**`.env.production`**
```bash
ENVIRONMENT=production
OPENAI_API_KEY=sk-prod-xxxxx
TAVILY_API_KEY=tvly-prod-xxxxx
ENABLE_10K_RAG=true
MAX_WORKERS=4
```

**`.env.staging`**
```bash
ENVIRONMENT=staging
OPENAI_API_KEY=sk-staging-xxxxx
TAVILY_API_KEY=tvly-staging-xxxxx
ENABLE_10K_RAG=false
MAX_WORKERS=2
```

Use with Docker Compose:
```bash
# Production
docker-compose --env-file .env.production up -d

# Staging
docker-compose --env-file .env.staging up -d
```

## 🔍 **Monitoring & Health Checks**

### Health Check Endpoints

The application provides several health check endpoints:

```bash
# Basic health check
curl http://localhost:8000/health

# API status
curl http://localhost:8000/api

# Detailed system status
curl http://localhost:8000/health/detailed
```

### Logging Configuration

Add to your production environment:
```python
# In api.py or main application
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'detailed',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': '/app/logs/aegis.log',
            'level': 'DEBUG',
            'formatter': 'detailed',
        },
    },
    'loggers': {
        'aegis': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': False,
        },
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
```

### Prometheus Metrics (Optional)

Add metrics collection:
```python
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('aegis_requests_total', 'Total requests')
REQUEST_DURATION = Histogram('aegis_request_duration_seconds', 'Request duration')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    REQUEST_COUNT.inc()
    REQUEST_DURATION.observe(time.time() - start_time)
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

## 🚨 **Troubleshooting**

### Common Production Issues

#### Service Won't Start
```bash
# Check Docker logs
docker-compose logs -f aegis-api

# Verify environment variables
docker-compose exec aegis-api env | grep -E "(OPENAI|TAVILY)"

# Test API connectivity
curl -v http://localhost:8000/health
```

#### Database Connection Issues
```bash
# Check ChromaDB health
curl http://localhost:8001/api/v1/heartbeat

# Recreate volumes if corrupted
docker-compose down -v
docker-compose up -d
```

#### High Memory Usage
```bash
# Monitor container resources
docker stats

# Adjust memory limits in docker-compose.yml
mem_limit: 4g
memswap_limit: 8g
```

#### SSL Certificate Issues
```bash
# Check certificate validity
openssl x509 -in cert.pem -text -noout

# Verify Nginx configuration
docker-compose exec nginx nginx -t
```

### Performance Optimization

#### Database Optimization
```bash
# Regular ChromaDB maintenance
docker-compose exec chromadb chroma utils compact

# Monitor database size
du -sh ./data/chroma_data/
```

#### Caching Strategy
```python
# Add Redis caching for frequent queries
from redis import Redis
import json

redis_client = Redis(host='redis', port=6379, db=0)

async def cached_query(question: str):
    cache_key = f"query:{hash(question)}"
    cached_result = redis_client.get(cache_key)
    
    if cached_result:
        return json.loads(cached_result)
    
    result = execute_query(agent_executor, question)
    redis_client.setex(cache_key, 3600, json.dumps(result))  # 1 hour cache
    return result
```

## 🔒 **Security Considerations**

### API Key Management
- **Never commit API keys** to version control
- Use **environment variables** or secret management systems
- **Rotate keys regularly** in production
- Implement **rate limiting** to prevent abuse

### Network Security
- Use **HTTPS** for all production deployments
- Implement **CORS policies** appropriately
- Consider **VPC/private networks** for cloud deployments
- Enable **DDoS protection** at the infrastructure level

### Container Security
```dockerfile
# Use non-root user in production Dockerfile
FROM python:3.10-slim

# Create non-root user
RUN groupadd -r aegis && useradd -r -g aegis aegis

# Set secure permissions
COPY --chown=aegis:aegis ./app /app
USER aegis

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

This deployment guide ensures you can successfully deploy Aegis Financial Intelligence in any environment, from local development to enterprise production systems.