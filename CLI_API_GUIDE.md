# CLI & API Quick Reference

## 🖥️ CLI Tool

### Installation

Add to your PATH (one-time setup):
```bash
cd ~/Zazu_2026
echo 'export PATH="$PATH:$HOME/Zazu_2026/bin"' >> ~/.bashrc
source ~/.bashrc
```

Or use directly:
```bash
cd ~/Zazu_2026
./bin/zazu [command]
```

### Commands

#### Ask a Question
```bash
zazu ask "What should I focus on today?"
zazu ask "What is my current mission?" --json
```

#### Create Content
```bash
zazu create "Generate a mythos about transformation"
zazu create "Build a worldbuilding concept for trading" --consensus
```

#### Make a Plan
```bash
zazu plan "Build Phase 3 features"
zazu plan "Launch fundraising campaign" --json
```

#### Check Status
```bash
zazu status
zazu status --json
```

---

## 🌐 REST API

### Start the Server

```bash
cd ~/Zazu_2026
source venv/bin/activate
uvicorn api.server:app --reload
```

Server runs at: **http://localhost:8000**  
Interactive docs: **http://localhost:8000/docs**

### Endpoints

#### POST /ask
Ask a question to the parliament.

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What should I focus on today?",
    "mode": "auto",
    "require_consensus": false
  }'
```

#### POST /create
Create content (mythos, worldbuilding, etc).

```bash
curl -X POST "http://localhost:8000/create?request=sovereignty&creative_type=mythos"
```

#### POST /plan
Create a strategic plan.

```bash
curl -X POST "http://localhost:8000/plan" \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Build Phase 3",
    "time_horizon": "seasonal"
  }'
```

#### POST /assess-risk
Get risk assessment.

```bash
curl -X POST "http://localhost:8000/assess-risk" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Launch new feature",
    "complexity": 7,
    "timeline_days": 45
  }'
```

#### GET /status
Check parliament status.

```bash
curl http://localhost:8000/status
```

#### GET /agents
List all agents.

```bash
curl http://localhost:8000/agents
```

#### GET /agents/{agent_id}
Get specific agent info.

```bash
curl http://localhost:8000/agents/artisan
```

---

## 🔗 Integration Examples

### Python
```python
import requests

# Ask question
response = requests.post("http://localhost:8000/ask", json={
    "question": "What is my mission?",
    "mode": "inquiry"
})
result = response.json()
print(result['reflection']['coherence_score'])
```

### JavaScript
```javascript
fetch('http://localhost:8000/ask', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    question: 'Plan my next project',
    mode: 'creation',
    require_consensus: true
  })
})
.then(r => r.json())
.then(data => console.log(data))
```

### cURL
```bash
# Quick ask
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What should I do next?"}'
```

---

## 🚀 Production Deployment

### Environment Variables
```bash
export ZAZU_REDIS_URL="redis://your-redis:6379"
export ZAZU_POSTGRES_DSN="postgresql://user:pass@host:5432/db"
```

### Run with Gunicorn (Production)
```bash
pip install gunicorn
gunicorn api.server:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Docker (Optional)
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 📊 API Response Format

All endpoints return:
```json
{
  "mode_used": "creation",
  "agents_involved": ["interpreter", "strategist", "artisan"],
  "outputs": {
    "strategist": {...},
    "artisan": {...}
  },
  "reflection": {
    "coherence_score": 0.85,
    "emotional_load_estimate": "low",
    "progress_assessment": "...",
    "philosophical_alignment": true
  },
  "consensus": {
    "consensus_score": 0.75,
    "threshold_met": true
  }
}
```
