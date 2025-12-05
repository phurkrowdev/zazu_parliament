# Using the Zazu Parliamentary Intelligence System

## Quick Usage Options

### Option 1: Interactive Python (Best for Testing)

```python
import asyncio
from core.chorus import ask_parliament

# Simple one-off questions
result = asyncio.run(ask_parliament("What is my current mission?"))
print(result)

# Creative requests
result = asyncio.run(ask_parliament(
    "Create a mythos about transformation",
    mode="creation"
))
print(result['outputs']['artisan']['creation']['content'])
```

---

### Option 2: Python Script Integration

```python
from core.chorus import Chorus
import asyncio

async def main():
    # Initialize parliament once
    chorus = Chorus()
    await chorus.initialize()
    
    try:
        # Ask multiple questions
        result1 = await chorus.process_request(
            "What should I focus on today?",
            mode="inquiry"
        )
        
        result2 = await chorus.process_request(
            "Plan my next project phase",
            mode="creation",
            require_consensus=True  # Get multi-agent consensus
        )
        
        # Access specific agent outputs
        if 'strategist' in result2['outputs']:
            strategy = result2['outputs']['strategist']
            print(f"Timeline: {len(strategy['strategy']['timeline'])} phases")
        
        # Check coherence
        coherence = result2['reflection']['coherence_score']
        print(f"Coherence: {coherence:.2f}")
        
    finally:
        await chorus.shutdown()

asyncio.run(main())
```

---

### Option 3: Command-Line Tool (Coming next!)

```bash
# Ask a question
zazu ask "What is my mission?"

# Create content
zazu create "Generate a mythos about sovereignty"

# Plan with consensus
zazu plan "Build Phase 3 features" --consensus

# Execute with approval
zazu execute "Run backup script" --require-approval
```

---

## Real-World Use Cases

### 1. Daily Planning Assistant
```python
result = await chorus.process_request(
    "Review my progress this week and suggest what to prioritize",
    mode="creation",
    context={'week': '2025-W49'}
)

# Get strategic plan
plan = result['outputs']['strategist']['strategy']

# Get coherence check
coherence = result['reflection']
```

### 2. Creative Content Generation
```python
result = await chorus.process_request(
    "Create a worldbuilding concept for the Zazu trading system",
    mode="creation"
)

mythos = result['outputs']['artisan']['creation']
print(mythos['content'])
```

### 3. Risk Assessment
```python
result = await chorus.process_request(
    "Assess the risks of implementing real-time trading",
    mode="creation",
    require_consensus=True
)

risk_score = result['outputs']['ledger']['analysis']['risk_score']
strategy = result['outputs']['strategist']['strategy']['risk_factors']
```

### 4. Decision Support
```python
result = await chorus.process_request(
    "Should I pivot to focus on fundraising or continue development?",
    mode="creation",
    require_consensus=True
)

# Multiple agents weigh in
consensus = result['consensus']['consensus_score']
perspectives = result['consensus']['additional_perspectives']
```

---

## Advanced: Custom Workflows

### Direct Agent Access
```python
chorus = Chorus()
await chorus.initialize()

# Talk to specific agents directly
artisan = chorus.agents['artisan']
creation = await artisan.process({
    'creative_type': 'symbolic',
    'theme': 'emergence',
    'constraints': {}
})

ledger = chorus.agents['ledger']
risk = await ledger.process({
    'analysis_type': 'variance',
    'data': {'time_series': [...]},
    'parameters': {}
})
```

### Custom Mode Detection
```python
# Override auto-detection
result = await chorus.process_request(
    user_input="Build me a plan",
    mode="creation",  # Force creation mode
    context={'previous_convo': '...'}
)
```

---

## Integration Patterns

### Web API (FastAPI)
```python
from fastapi import FastAPI
from core.chorus import Chorus

app = FastAPI()
chorus = Chorus()

@app.on_event("startup")
async def startup():
    await chorus.initialize()

@app.post("/ask")
async def ask(question: str, mode: str = "auto"):
    result = await chorus.process_request(question, mode=mode)
    return result

@app.on_event("shutdown")
async def shutdown():
    await chorus.shutdown()
```

### Discord Bot
```python
import discord
from core.chorus import Chorus

chorus = Chorus()

@client.event
async def on_ready():
    await chorus.initialize()

@client.event
async def on_message(message):
    if message.content.startswith('!zazu'):
        question = message.content[6:]
        result = await chorus.process_request(question)
        
        # Format response
        response = f"**Coherence**: {result['reflection']['coherence_score']:.2f}\n"
        await message.channel.send(response)
```

### Telegram Bot
```python
from telegram import Update
from core.chorus import Chorus

chorus = Chorus()

async def handle_message(update: Update, context):
    question = update.message.text
    result = await chorus.process_request(question, mode="auto")
    
    await update.message.reply_text(
        f"Agents: {', '.join(result['agents_involved'])}\n"
        f"Coherence: {result['reflection']['coherence_score']:.2f}"
    )
```

---

## What's Missing (Next Steps)

If you want to use this in production, you'd want:

1. **CLI Tool** - Simple `zazu ask "question"` interface
2. **REST API** - FastAPI server for remote access
3. **Persistent Context** - Remember conversations across sessions
4. **Streaming Responses** - Real-time output as agents think
5. **Web Interface** - Simple UI for non-programmers

**Want me to build any of these?** The CLI tool would take ~15 minutes, the REST API ~30 minutes.
