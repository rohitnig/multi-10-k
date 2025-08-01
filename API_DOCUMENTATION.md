# 🌐 API Documentation - Aegis Financial Intelligence

Complete API documentation for the Aegis Financial Intelligence platform, including REST endpoints, WebSocket connections, and integration examples.

## 📊 **API Overview**

### Base Information
- **Base URL**: `http://localhost:8000` (development) or `https://your-domain.com` (production)
- **API Version**: 2.0.0
- **Content Type**: `application/json`
- **Authentication**: None required (currently open access)
- **Rate Limiting**: Recommended in production

### Quick Links
- **Interactive Docs**: `/api/docs` (Swagger UI)
- **ReDoc Documentation**: `/api/redoc` (Alternative docs)
- **OpenAPI Schema**: `/openapi.json`

## 🌟 **Web Interface Endpoints**

### GET `/`
**Serves the main web interface**

Returns the beautiful Apple-inspired web interface for interactive financial analysis.

**Response**: HTML page with embedded CSS and JavaScript

**Example**:
```bash
curl http://localhost:8000/
# Returns the full web interface
```

## 🔍 **Health & Status Endpoints**

### GET `/health`
**Comprehensive health check**

Returns detailed system status including agent readiness and service health.

**Response**:
```json
{
  "status": "healthy",
  "agent_ready": true,
  "message": "API is running and agent is ready"
}
```

**Status Codes**:
- `200 OK`: System is healthy
- `503 Service Unavailable`: System is initializing or unhealthy

**Example**:
```bash
curl http://localhost:8000/health
```

### GET `/api`
**API information endpoint**

Returns basic API information and status.

**Response**:
```json
{
  "name": "Aegis Financial Intelligence API",
  "version": "2.0.0",
  "status": "ready",
  "agent_ready": true
}
```

## 🤖 **Financial Analysis Endpoints**

### POST `/query`
**Execute financial analysis query**

The main endpoint for performing financial analysis using the multi-agent system.

**Request Body**:
```json
{
  "question": "string"  // The financial question to analyze
}
```

**Response**:
```json
{
  "answer": "string"  // The agent's comprehensive analysis
}
```

**Status Codes**:
- `200 OK`: Query executed successfully  
- `400 Bad Request`: Invalid request format
- `500 Internal Server Error`: Agent execution failed

**Example Request**:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are Google'\''s main risk factors for 2023?"
  }'
```

**Example Response**:
```json
{
  "answer": "Based on my analysis of Google's 2023 10-K filing and current market data, the main risk factors include:\n\n1. **Regulatory Risk**: Increasing scrutiny from global regulators regarding antitrust concerns and data privacy regulations...\n\n2. **Competition Risk**: Intense competition in cloud computing, search, and AI markets from Microsoft, Amazon, and emerging players...\n\n3. **Technology Risk**: Rapid changes in AI and machine learning requiring continuous investment and adaptation..."
}
```

## 📝 **Request/Response Models**

### QueryRequest
```typescript
interface QueryRequest {
  question: string;  // Required. The financial question to analyze
}
```

**Validation Rules**:
- `question` must be non-empty string
- Maximum length: 10,000 characters
- Minimum length: 10 characters

### QueryResponse  
```typescript
interface QueryResponse {
  answer: string;  // The agent's analysis result
}
```

### HealthResponse
```typescript
interface HealthResponse {
  status: "healthy" | "initializing" | "error";
  agent_ready: boolean;
  message: string;
}
```

### APIInfoResponse
```typescript
interface APIInfoResponse {
  name: string;
  version: string;
  status: string;
  agent_ready: boolean;
}
```

## 🔧 **Integration Examples**

### JavaScript/TypeScript (Web)

```javascript
class AegisFinancialClient {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async checkHealth() {
    const response = await fetch(`${this.baseUrl}/health`);
    return await response.json();
  }

  async analyzeQuery(question) {
    const response = await fetch(`${this.baseUrl}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question })
    });
    
    if (!response.ok) {
      throw new Error(`Query failed: ${response.status}`);
    }
    
    return await response.json();
  }
}

// Usage
const client = new AegisFinancialClient();

try {
  const result = await client.analyzeQuery(
    "What are the current AI market trends?"
  );
  console.log('Analysis:', result.answer);
} catch (error) {
  console.error('Error:', error.message);
}
```

### Python (Backend Integration)

```python
import requests
import json
from typing import Dict, Any

class AegisFinancialClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def check_health(self) -> Dict[str, Any]:
        """Check system health status."""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def analyze_query(self, question: str) -> str:
        """Execute financial analysis query."""
        payload = {"question": question}
        response = self.session.post(
            f"{self.base_url}/query",
            json=payload
        )
        response.raise_for_status()
        return response.json()["answer"]
    
    def wait_for_ready(self, timeout: int = 60) -> bool:
        """Wait for the system to be ready."""
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                health = self.check_health()
                if health.get("agent_ready"):
                    return True
            except requests.RequestException:
                pass
            time.sleep(2)
        
        return False

# Usage
client = AegisFinancialClient()

# Wait for system to be ready
if client.wait_for_ready():
    # Perform analysis
    analysis = client.analyze_query(
        "Compare Google's 2023 performance with market benchmarks"
    )
    print("Analysis Result:")
    print(analysis)
else:
    print("System not ready within timeout period")
```

### cURL Examples

**Basic Health Check**:
```bash
curl -X GET http://localhost:8000/health \
  -H "Accept: application/json"
```

**Simple Query**:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the risks of investing in tech stocks?"}'
```

**Complex Multi-part Query**:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "I need a comprehensive investment analysis for Google. Please provide: 1) Current market sentiment and stock trends, 2) Key business risks from their latest filings, 3) Comparison with our internal profit data, and 4) An investment recommendation with reasoning."
  }'
```

### Node.js/Express Integration

```javascript
const express = require('express');
const axios = require('axios');

const app = express();
app.use(express.json());

const AEGIS_API_URL = 'http://localhost:8000';

// Middleware to check Aegis system health
app.use(async (req, res, next) => {
  try {
    const health = await axios.get(`${AEGIS_API_URL}/health`);
    if (!health.data.agent_ready) {
      return res.status(503).json({
        error: 'Financial analysis system is not ready'
      });
    }
    next();
  } catch (error) {
    return res.status(503).json({
      error: 'Financial analysis system unavailable'
    });
  }
});

// Proxy endpoint for financial analysis
app.post('/api/financial-analysis', async (req, res) => {
  try {
    const { question } = req.body;
    
    if (!question) {
      return res.status(400).json({
        error: 'Question is required'
      });
    }

    const response = await axios.post(`${AEGIS_API_URL}/query`, {
      question: question
    });

    res.json({
      success: true,
      analysis: response.data.answer,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Analysis error:', error.message);
    res.status(500).json({
      error: 'Analysis failed',
      message: error.response?.data?.detail || error.message
    });
  }
});

app.listen(3000, () => {
  console.log('Server running on http://localhost:3000');
});
```

## 🛡️ **Error Handling**

### Error Response Format

All errors follow a consistent format:

```json
{
  "detail": "Human-readable error description",
  "type": "error_type",
  "code": "ERROR_CODE"
}
```

### Common Error Codes

| Status Code | Error Type | Description | Solution |
|-------------|------------|-------------|----------|
| 400 | `VALIDATION_ERROR` | Invalid request format | Check request body format |
| 422 | `QUERY_VALIDATION_ERROR` | Invalid question format | Ensure question meets requirements |
| 500 | `AGENT_EXECUTION_ERROR` | Agent processing failed | Check system logs, retry request |
| 503 | `SERVICE_UNAVAILABLE` | System not ready | Wait for initialization, check health endpoint |
| 429 | `RATE_LIMIT_EXCEEDED` | Too many requests | Implement request throttling |

### Error Handling Best Practices

```python
import requests
from requests.exceptions import RequestException
import time

def robust_query(client, question, max_retries=3):
    """Execute query with retry logic and error handling."""
    
    for attempt in range(max_retries):
        try:
            # Check system health first
            health = client.check_health()
            if not health.get('agent_ready'):
                if attempt < max_retries - 1:
                    time.sleep(5)  # Wait before retry
                    continue
                else:
                    raise Exception("System not ready after multiple attempts")
            
            # Execute query
            result = client.analyze_query(question)
            return result
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 503:  # Service unavailable
                if attempt < max_retries - 1:
                    time.sleep(10)  # Longer wait for service issues
                    continue
                else:
                    raise Exception("Service unavailable after retries")
            elif e.response.status_code == 429:  # Rate limited
                if attempt < max_retries - 1:
                    time.sleep(60)  # Wait before retry
                    continue
                else:
                    raise Exception("Rate limit exceeded")
            else:
                raise  # Re-raise other HTTP errors
                
        except RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            else:
                raise Exception(f"Request failed after {max_retries} attempts: {e}")
    
    raise Exception("All retry attempts exhausted")
```

## ⚡ **Performance & Rate Limiting**

### Response Times

| Endpoint | Typical Response Time | Notes |
|----------|----------------------|--------|
| `/health` | < 100ms | Cached status check |
| `/api` | < 50ms | Static information |
| `/query` (simple) | 3-8 seconds | Single tool usage |
| `/query` (complex) | 10-30 seconds | Multi-tool analysis |

### Rate Limiting Recommendations

```python
# Production rate limiting configuration
RATE_LIMITS = {
    '/health': '100/minute',      # Health checks
    '/api': '50/minute',          # API info
    '/query': '10/minute',        # Analysis queries (resource intensive)
    'default': '30/minute'        # General requests
}
```

### Caching Strategy

```python
# Example Redis caching for frequent queries
import redis
import hashlib
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cached_query(question: str, ttl: int = 3600):
    # Create cache key from question
    cache_key = f"query:{hashlib.md5(question.encode()).hexdigest()}"
    
    # Check cache first
    cached_result = redis_client.get(cache_key)
    if cached_result:
        return json.loads(cached_result)
    
    # Execute query if not cached
    result = client.analyze_query(question)
    
    # Cache result
    redis_client.setex(cache_key, ttl, json.dumps({
        'answer': result,
        'cached_at': time.time()
    }))
    
    return result
```

## 🔐 **Security Considerations**

### Input Validation

```python
def validate_query_input(question: str) -> bool:
    """Validate query input for security and format."""
    
    # Length checks
    if len(question) < 10 or len(question) > 10000:
        return False
    
    # Content validation (basic)
    forbidden_patterns = [
        r'<script',           # XSS prevention
        r'javascript:',       # JavaScript injection
        r'data:text/html',    # Data URI injection
        r'eval\(',            # Code execution
    ]
    
    import re
    for pattern in forbidden_patterns:
        if re.search(pattern, question, re.IGNORECASE):
            return False
    
    return True
```

### API Security Headers

```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Add security middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["your-domain.com", "*.your-domain.com"]
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
```

## 📋 **API Testing**

### Health Check Tests

```bash
#!/bin/bash
# Basic API health test script

BASE_URL="http://localhost:8000"

echo "Testing API Health..."

# Test health endpoint
echo -n "Health check: "
if curl -s -f "$BASE_URL/health" > /dev/null; then
    echo "✅ PASS"
else
    echo "❌ FAIL"
    exit 1
fi

# Test API info
echo -n "API info: "
if curl -s -f "$BASE_URL/api" > /dev/null; then
    echo "✅ PASS"
else
    echo "❌ FAIL"
    exit 1
fi

# Test web interface
echo -n "Web interface: "
if curl -s -f "$BASE_URL/" > /dev/null; then
    echo "✅ PASS"
else
    echo "❌ FAIL"
    exit 1
fi

echo "All health checks passed! 🎉"
```

### Integration Test Suite

```python
import pytest
import requests
import time

class TestAegisAPI:
    base_url = "http://localhost:8000"
    
    def test_health_endpoint(self):
        response = requests.get(f"{self.base_url}/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "agent_ready" in data
    
    def test_api_info_endpoint(self):
        response = requests.get(f"{self.base_url}/api")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Aegis Financial Intelligence API"
        assert "version" in data
    
    def test_web_interface(self):
        response = requests.get(f"{self.base_url}/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_simple_query(self):
        # Wait for system to be ready
        self._wait_for_ready()
        
        query_data = {
            "question": "What are the main risks in financial markets?"
        }
        response = requests.post(
            f"{self.base_url}/query",
            json=query_data
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert len(data["answer"]) > 50  # Substantial response
    
    def test_invalid_query(self):
        # Test empty question
        response = requests.post(
            f"{self.base_url}/query",
            json={"question": ""}
        )
        assert response.status_code == 422
    
    def test_malformed_request(self):
        # Test malformed JSON
        response = requests.post(
            f"{self.base_url}/query",
            data="invalid json"
        )
        assert response.status_code == 422
    
    def _wait_for_ready(self, timeout=60):
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.base_url}/health")
                if response.json().get("agent_ready"):
                    return True
            except:
                pass
            time.sleep(2)
        raise TimeoutError("System not ready within timeout")

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

This API documentation provides everything needed to integrate with the Aegis Financial Intelligence platform, from simple health checks to complex financial analysis queries.