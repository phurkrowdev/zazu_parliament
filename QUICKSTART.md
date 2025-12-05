# ⚡ Quick Start: Run This Exactly

**Goal**: See all 7 agents working in under 2 minutes.

**Just copy-paste these commands in order. No thinking required.**

---

## Step 1: Get to the Right Place
```bash
cd ~/Zazu_2026
```

---

## Step 2: Turn On the Environment
```bash
source venv/bin/activate
```

**You should see `(venv)` appear in your terminal prompt.**

---

## Step 3: Make Sure Docker is Running
```bash
cd infrastructure
docker-compose ps
```

**Expected:** You should see PostgreSQL and Redis with status "Up"

**If NOT running:**
```bash
docker-compose up -d
cd ..
```

**If already running:**
```bash
cd ..
```

---

## Step 4: Test All Agents (This is it!)

### Test the first 3 agents:
```bash
python tests/validate_phase2a.py
```

**Wait for:** "✅ ALL AGENTS VALIDATED SUCCESSFULLY"

---

### Test the next 3 agents:
```bash
python tests/validate_phase2b.py
```

**Wait for:** "🎉 7-AGENT PARLIAMENT COMPLETE!"

---

## ✅ Done!

If both tests passed, **you have a working 7-agent parliament**.

---

## 🔥 Bonus: See an Agent Create Mythos (Optional)

```bash
python3 << 'EOF'
import asyncio
from agents.artisan_agent import ArtisanAgent

async def demo():
    agent = ArtisanAgent(
        constitution_path="core/constitution.json",
        redis_url="redis://localhost:6379",
        postgres_dsn="postgresql://zazu:zazu_dev_password@localhost:5432/zazu_memory"
    )
    await agent.initialize()
    
    result = await agent.process({
        'creative_type': 'mythos',
        'theme': 'sovereignty',
        'constraints': {},
        'context': {}
    })
    
    print("\n" + "="*60)
    print(result['creation']['title'])
    print("="*60)
    print(result['creation']['content'])
    
    await agent.shutdown()

asyncio.run(demo())
EOF
```

**Expected:** A generated mythos about sovereignty and self-determination.

---

## 🛠️ If Something Breaks

### Docker not running?
```bash
cd ~/Zazu_2026/infrastructure
docker-compose down
docker-compose up -d
cd ..
```

### Database needs reset?
```bash
python core/init_zazu.py --reset
```

### Tests failing?
Check you're in the right directory:
```bash
pwd
# Should show: /home/phurkrow/Zazu_2026
```

---

## 📍 You Are Here
- ✅ All agents implemented (7/7)
- ✅ All agents tested
- 🔲 Chorus orchestrator (next phase)
- 🔲 Demo workflows (next phase)
