# Zazu 7-Agent Parliament - Testing Guide

## Quick Start: See the System in Action

### 1. Navigate to Project Directory
```bash
cd ~/Zazu_2026
```

### 2. Activate Virtual Environment
```bash
source venv/bin/activate
```

### 3. Verify Infrastructure (Docker Services)
```bash
cd infrastructure
docker-compose ps
```

**Expected Output**: PostgreSQL, Redis, MinIO, and Loki should all be "Up"

If services aren't running:
```bash
docker-compose up -d
```

### 4. Initialize Zazu (if not already done)
```bash
cd ~/Zazu_2026
python core/init_zazu.py
```

**Expected Output**: "ZAZU PARLIAMENTARY INTELLIGENCE - ONLINE"

*Note: If you need to reset the database, use `python core/init_zazu.py --reset`*

---

## Testing Individual Agents

### Test Phase 2A Agents (Core Triad)
```bash
python tests/validate_phase2a.py
```

**Tests**:
- 🧠 **Interpreter**: Intent parsing, ambiguity detection, routing
- ⚙️ **Executor**: File operations, command execution, sandboxing
- 🪞 **Mirror**: Coherence scoring, emotional load, progress assessment

**Expected Output**:
```
============================================================
  ZAZU PHASE 2A AGENT VALIDATION
============================================================

🧠 Testing Interpreter Agent...
  ✓ Query intent parsing and routing
  ✓ Execute intent parsing and routing
  ✓ Ambiguity detection
✅ Interpreter Agent: All tests passed

⚙️  Testing Executor Agent...
  ✓ File write execution
  ✓ Path validation
✅ Executor Agent: All tests passed

🪞 Testing Mirror Agent...
  ✓ Coherence scoring
  ✓ Emotional load detection
  ✓ Recommendations generation
  ✓ Philosophical alignment check
✅ Mirror Agent: All tests passed

============================================================
  ✅ ALL AGENTS VALIDATED SUCCESSFULLY
============================================================
```

---

### Test Phase 2B Agents (Strategic & Creative Layer)
```bash
python tests/validate_phase2b.py
```

**Tests**:
- 🎯 **Strategist**: Scenario modeling, decision trees, timeline planning
- 🎨 **Artisan**: Mythos generation, worldbuilding, aesthetic creation
- 📊 **Ledger**: Risk quantification, variance tracking, backtesting

**Expected Output**:
```
============================================================
  ZAZU PHASE 2B AGENT VALIDATION
============================================================

🎯 Testing Strategist Agent...
  ✓ Scenario modeling
  ✓ Decision tree generation
  ✓ Timeline planning
✅ Strategist Agent: All tests passed

🎨 Testing Artisan Agent...
  ✓ Mythos generation
  ✓ Worldbuilding
  ✓ Aesthetic creation
  ✓ Symbolic synthesis
✅ Artisan Agent: All tests passed

📊 Testing Ledger Agent...
  ✓ Risk quantification
  ✓ Variance tracking
  ✓ Backtesting
  ✓ Scenario safety checks
✅ Ledger Agent: All tests passed

============================================================
  ✅ ALL PHASE 2B AGENTS VALIDATED
  🎉 7-AGENT PARLIAMENT COMPLETE!
============================================================
```

---

### Test Constitutional Compliance (Existing)
```bash
pytest tests/test_constitutional_compliance.py -v
```

**Tests**: Validates that Sentinel enforces:
- Halt-repair loop (max 3 cycles)
- Anti-paralysis rule (halt rate monitoring)
- Protected dreamspace (bypass for speculation)
- Subsystem constraint enforcement

---

## Interactive Agent Testing (Python REPL)

Want to interact with agents directly? Try this:

```bash
python3
```

```python
import asyncio
from agents.artisan_agent import ArtisanAgent

async def test_artisan():
    agent = ArtisanAgent(
        constitution_path="core/constitution.json",
        redis_url="redis://localhost:6379",
        postgres_dsn="postgresql://zazu:zazu_dev_password@localhost:5432/zazu_memory"
    )
    await agent.initialize()
    
    # Generate a mythos
    result = await agent.process({
        'creative_type': 'mythos',
        'theme': 'transformation',
        'constraints': {'tone': 'mythic'},
        'context': {}
    })
    
    print("\n" + "="*60)
    print(result['creation']['title'])
    print("="*60)
    print(result['creation']['content'])
    print("="*60)
    
    await agent.shutdown()

# Run it
asyncio.run(test_artisan())
```

**Expected**: A generated mythos about transformation with archetypal elements!

---

## Quick Health Check (All Services)

```bash
# From ~/Zazu_2026
./scripts/health_check.sh
```

*(Coming in Phase 2C)*

---

## Troubleshooting

### Services Not Running
```bash
cd ~/Zazu_2026/infrastructure
docker-compose down
docker-compose up -d
docker-compose ps
```

### Database Errors
```bash
# Reset the database
python core/init_zazu.py --reset
```

### Virtual Environment Issues
```bash
deactivate
cd ~/Zazu_2026
source venv/bin/activate
pip install -r requirements.txt
```

### PyTorch CUDA Warnings
These are non-blocking warnings about GPU compatibility. The system works fine on CPU:
```
UserWarning: NVIDIA GeForce GTX 1060 6GB with CUDA capability sm_61 is not compatible...
```
**Solution**: Ignore or install CUDA 11.8 compatible PyTorch (not required).

---

## What's Next?

Once all tests pass, you have a fully operational 7-agent parliament! Next steps:

1. **Build Chorus Orchestrator** (Phase 2C) - Coordinate agents
2. **Create Demo Scripts** - Show multi-agent workflows
3. **Deploy to Production** - Scale the infrastructure

---

## File Locations

- **Agents**: `~/Zazu_2026/agents/`
- **Tests**: `~/Zazu_2026/tests/`
- **Constitution**: `~/Zazu_2026/core/constitution.json`
- **Infrastructure**: `~/Zazu_2026/infrastructure/docker-compose.yml`
- **Logs**: Check `docker logs` for PostgreSQL/Redis
