# Zazu 2026 - Constitutional Intelligence System

**Status**: Phase 1 Complete - Foundation Infrastructure Operational

## Overview

Zazu is a constitutional, parliamentary multi-agent AI system designed with seven orthogonal subsystems governed by immutable ethical axioms. This implementation transforms the Zazu Constitutional Genome from conceptual architecture into operational reality.

## Architecture

### Seven Subsystems (The Parliament)

1. **Interpreter** - Semantic spine for intent clarification
2. **Strategist** - Temporal foresight and scenario modeling
3. **Artisan** - Creative fabricator for mythos and worldbuilding
4. **Ledger** - Risk engine for quantitative analysis
5. **Sentinel** - Safety & ethical adjudicator (negative authority only)
6. **Executor** - Action gateway with sandboxed execution
7. **Mirror** - Self-model and recovery context tracker

### Five-Layer Stack

1. **Foundations** - Orthogonality, epistemic redundancy, moral physics
2. **Cognition** - Self-representation, constitutional identity, evolution engine
3. **Risk & Resilience** - Edge-case detection, failure containment
4. **Operational Integration** - Creative, trading, recovery playbooks
5. **Temporal Alignment** - Multi-horizon coherence, companion-intelligence emergence

### Three Constitutional Axioms

1. **User Sovereignty** - User is the final axiom (cannot override intent or impose values)
2. **Permissive-Until-Dangerous** - Default to freedom, restrict only at thresholds
3. **Redundant Epistemics** - Truth emerges from convergence, not dictation

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- 4GB RAM minimum

### Installation

```bash
# 1. Clone/navigate to project root
cd ~/Zazu_2026

# 2. Start infrastructure services
cd infrastructure
docker-compose up -d

# 3. Verify services are running
docker-compose ps
# All services should show "Up" status

# 4. Return to project root and activate virtual environment
cd ~/Zazu_2026
source venv/bin/activate

# 5. Install Python dependencies
pip install -r requirements.txt

# 6. Initialize Zazu constitutional kernel
python core/init_zazu.py

# 7. (Optional) Reset database if re-initializing
# python core/init_zazu.py --reset
```

---

## Testing the 7-Agent Parliament

After initialization, verify all agents are working:

```bash
# Test Phase 2A agents (Interpreter, Executor, Mirror)
python tests/validate_phase2a.py

# Test Phase 2B agents (Strategist, Artisan, Ledger)
python tests/validate_phase2b.py

# Test constitutional compliance (Sentinel)
pytest tests/test_constitutional_compliance.py -v
```

**See [`TESTING.md`](TESTING.md) for detailed testing guide and interactive examples.**

---

## Using the Zazu Parliament

### Command-Line Tool
```bash
# Simple commands
./bin/zazu ask "What should I focus on today?"
./bin/zazu create "Generate a mythos about transformation"
./bin/zazu plan "Build Phase 3 features"
./bin/zazu status
```

### REST API
```bash
# Start server
uvicorn api.server:app --reload

# Interactive docs: http://localhost:8000/docs
```

### Python Integration
```python
from core.chorus import ask_parliament
import asyncio

result = asyncio.run(ask_parliament("What is my mission?"))
print(result['reflection']['coherence_score'])
```

**See [`CLI_API_GUIDE.md`](CLI_API_GUIDE.md) for complete usage documentation.**

---
### Expected Output

```
═══════════════════════════════════════════════════════
  ZAZU CONSTITUTIONAL INTELLIGENCE - INITIALIZATION  
═══════════════════════════════════════════════════════

✓ Infrastructure validated
✓ Constitutional kernel loaded
✓ Memory architecture initialized
✓ Procedural workflows loaded
✓ Constitutional compliance verified

════════════════════════════════════════════════════
  ZAZU PARLIAMENTARY INTELLIGENCE - ONLINE  
════════════════════════════════════════════════════
```

## Project Structure

```
Zazu_2026/
├── core/
│   ├── constitution.json         # Constitutional kernel
│   ├── init_zazu.py              # Initialization sequence
│   ├── memory/
│   │   ├── schemas.sql           # Postgres memory schemas
│   │   └── procedural_memory.yaml# Workflow templates
│   └── schemas/                  # API contract schemas
├── agents/
│   ├── base_agent.py             # Abstract agent template
│   ├── sentinel_agent.py         # Safety adjudicator
│   ├── [... 6 more agents TBD]
├── playbooks/
│   └── [Operational workflows]
├── infrastructure/
│   ├── docker-compose.yml        # Service orchestration
│   └── loki-config.yml           # Reflective memory config
├── tests/
│   └── test_constitutional_compliance.py
└── requirements.txt
```

## Memory Architecture

- **Episodic**: Postgres JSONB (event logs with temporal indexing)
- **Semantic**: Postgres + pgvector (knowledge graph with similarity search)
- **Procedural**: Redis (YAML workflow templates)
- **Reflective**: Loki (time-series calibration logs)
- **Mission**: Postgres recursive (hierarchical purpose tracking)

## Testing

```bash
# Run constitutional compliance tests
pytest tests/test_constitutional_compliance.py -v

# With coverage
pytest tests/ --cov=core --cov=agents
```

## Next Steps (Phase 2)

- [ ] Implement remaining 6 subsystem agents
- [ ] Build Chorus orchestrator (mode-switching + consensus)
- [ ] Test orthogonality (failure isolation)
- [ ] Validate halt-repair loops
- [ ] Test epistemic redundancy mechanisms

## Constitutional Highlights

### Sentinel Anti-Paralysis

- Max 3 repair cycles before user escalation
- Halt rate monitoring (50% threshold triggers calibration)
- Protected dreamspace (creativity flows freely, gated at publication)

### Moral Physics

- Dual anchoring (user arc + external world protection)
- Moral regression testing (coherence + harm boundaries)
- Permissive-until-dangerous (freedom first, safety gates at thresholds)

## License

Proprietary - Phurkrow 2026

## Contact

For architectural questions or implementation guidance, see `implementation_plan.md` in the brain artifacts directory.

---

*"Amplify ordered intelligence without overstepping sovereignty."*
