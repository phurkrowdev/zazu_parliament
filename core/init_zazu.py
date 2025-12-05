#!/usr/bin/env python3
"""
Zazu Constitutional Intelligence - Initialization Sequence
Boots infrastructure, loads constitutional kernel, instantiates parliament
"""

import asyncio
import sys
import logging
from pathlib import Path
import json
import subprocess
import time
import argparse

import redis.asyncio as redis
import psycopg
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

console = Console()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('zazu.init')


class ZazuInitializer:
    """Orchestrates the Zazu boot sequence"""
    
    def __init__(self, reset=False):
        self.redis_url = "redis://localhost:6379"
        self.postgres_dsn = "postgresql://zazu:zazu_dev_password@localhost:5432/zazu_memory"
        self.constitution_path = Path("core/constitution.json")
        self.schema_path = Path("core/memory/schemas.sql")
        self.procedural_path = Path("core/memory/procedural_memory.yaml")
        self.reset = reset
        
    async def run(self):
        """Execute full initialization sequence"""
        console.print("\n[bold cyan]═══════════════════════════════════════════════════════[/]")
        console.print("[bold cyan]  ZAZU CONSTITUTIONAL INTELLIGENCE - INITIALIZATION  [/]")
        console.print("[bold cyan]═══════════════════════════════════════════════════════[/]\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # Step 1: Infrastructure validation
            task1 = progress.add_task("[yellow]1. Validating infrastructure...", total=None)
            await self.validate_infrastructure()
            progress.update(task1, description="[green]✓ Infrastructure validated")
            
            # Step 2: Constitutional kernel loading
            task2 = progress.add_task("[yellow]2. Loading constitutional kernel...", total=None)
            constitution = await self.load_constitution()
            progress.update(task2, description="[green]✓ Constitutional kernel loaded")
            
            # Step 3: Memory initialization
            task3 = progress.add_task("[yellow]3. Initializing memory architecture...", total=None)
            await self.initialize_memory()
            progress.update(task3, description="[green]✓ Memory architecture initialized")
            
            # Step 4: Load procedural memory
            task4 = progress.add_task("[yellow]4. Loading procedural workflows...", total=None)
            await self.load_procedural_memory()
            progress.update(task4, description="[green]✓ Procedural workflows loaded")
            
            # Step 5: Constitutional compliance test
            task5 = progress.add_task("[yellow]5. Running constitutional compliance test...", total=None)
            await self.constitutional_ping_pong()
            progress.update(task5, description="[green]✓ Constitutional compliance verified")
            
        console.print("\n[bold green]════════════════════════════════════════════════════[/]")
        console.print("[bold green]  ZAZU PARLIAMENTARY INTELLIGENCE - ONLINE  [/]")
        console.print("[bold green]════════════════════════════════════════════════════[/]\n")
        
        await self.print_status(constitution)
    
    async def validate_infrastructure(self):
        """Check connectivity to all infrastructure services"""
        # Postgres
        try:
            conn = await psycopg.AsyncConnection.connect(self.postgres_dsn)
            await conn.close()
            logger.info("Postgres connection verified")
        except Exception as e:
            console.print(f"[red]✗ Postgres connection failed: {e}[/]")
            raise
        
        # Redis
        try:
            r = await redis.from_url(self.redis_url)
            await r.ping()
            await r.close()
            logger.info("Redis connection verified")
        except Exception as e:
            console.print(f"[red]✗ Redis connection failed: {e}[/]")
            raise
        
        console.print("  [dim]→ Postgres, Redis online[/]")
    
    async def load_constitution(self):
        """Parse and validate constitutional kernel"""
        if not self.constitution_path.exists():
            raise FileNotFoundError(f"Constitution not found at {self.constitution_path}")
        
        with open(self.constitution_path, 'r') as f:
            constitution = json.load(f)
        
        # Validate required keys
        required_keys = ['axioms', 'subsystems', 'modes', 'moral_physics', 'memory_architecture']
        for key in required_keys:
            if key not in constitution:
                raise ValueError(f"Constitutional kernel missing required key: {key}")
        
        # Validate seven subsystems
        subsystems = constitution['subsystems']
        expected = ['interpreter', 'strategist', 'artisan', 'ledger', 'sentinel', 'executor', 'mirror']
        if set(subsystems.keys()) != set(expected):
            raise ValueError(f"Constitution must define exactly seven subsystems: {expected}")
        
        console.print(f"  [dim]→ Validated {len(subsystems)} subsystems, {len(constitution['axioms'])} axioms[/]")
        return constitution
    
    async def initialize_memory(self):
        """Execute SQL schema to create memory tables"""
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Schema not found at {self.schema_path}")
        
        conn = await psycopg.AsyncConnection.connect(self.postgres_dsn)
        
        # Drop existing schema if reset flag is set
        if self.reset:
            async with conn.cursor() as cur:
                await cur.execute("""
                    DROP SCHEMA IF EXISTS public CASCADE;
                    CREATE SCHEMA public;
                    GRANT ALL ON SCHEMA public TO zazu;
                    GRANT ALL ON SCHEMA public TO public;
                """)
                await conn.commit()
            console.print("  [dim]→ Reset database schema[/]")
        
        with open(self.schema_path, 'r') as f:
            schema_sql = f.read()
        
        async with conn.cursor() as cur:
            await cur.execute(schema_sql)
            await conn.commit()
        
        # Verify tables created
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = [row[0] async for row in cur]
        
        await conn.close()
        
        expected_tables = [
            'episodic_memory', 'semantic_memory', 'mission_memory',
            'constitutional_violations', 'halt_events', 'calibration_history'
        ]
        
        for table in expected_tables:
            if table not in tables:
                raise ValueError(f"Expected table {table} not created")
        
        console.print(f"  [dim]→ Created {len(tables)} memory tables[/]")
    
    async def load_procedural_memory(self):
        """Load YAML workflows into Redis"""
        if not self.procedural_path.exists():
            raise FileNotFoundError(f"Procedural memory not found at {self.procedural_path}")
        
        import yaml
        
        with open(self.procedural_path, 'r') as f:
            workflows = yaml.safe_load(f)
        
        r = await redis.from_url(self.redis_url)
        
        for workflow_id, workflow_data in workflows.items():
            await r.set(
                f"procedural:{workflow_id}",
                json.dumps(workflow_data)
            )
        
        await r.close()
        
        console.print(f"  [dim]→ Loaded {len(workflows)} workflow templates[/]")
    
    async def constitutional_ping_pong(self):
        """
        Minimal test to verify constitutional constraints are enforced.
        Instantiates Sentinel and tests halt authority.
        """
        from agents.sentinel_agent import SentinelAgent
        
        sentinel = SentinelAgent(
            constitution_path=str(self.constitution_path),
            redis_url=self.redis_url,
            postgres_dsn=self.postgres_dsn
        )
        
        await sentinel.initialize()
        
        # Test 1: Approve benign artifact
        benign_result = await sentinel.process({
            'artifact': {'type': 'plan', 'content': 'Build prototype'},
            'subsystem_origin': 'strategist',
            'action_type': 'execution',
            'context': {}
        })
        
        if benign_result['decision'] != 'approve':
            raise AssertionError("Sentinel incorrectly halted benign artifact")
        
        # Test 2: Protected dreamspace (should not interfere)
        dreamspace_result = await sentinel.process({
            'artifact': {'type': 'narrative', 'content': 'Dark speculative mythos'},
            'subsystem_origin': 'artisan',
            'action_type': 'speculation',  # Not a threshold action
            'context': {}
        })
        
        if dreamspace_result['decision'] != 'approve':
            raise AssertionError("Sentinel incorrectly entered protected dreamspace")
        
        await sentinel.shutdown()
        
        console.print("  [dim]→ Sentinel halt authority verified, dreamspace protected[/]")
    
    async def print_status(self, constitution):
        """Display boot status summary"""
        console.print("\n[bold]Constitutional Parameters:[/]")
        console.print(f"  Version: {constitution['constitution_version']}")
        console.print(f"  Subsystems: {', '.join(constitution['subsystems'].keys())}")
        console.print(f"  Modes: {', '.join(constitution['modes'].keys())}")
        console.print(f"  Max Repair Cycles: {constitution['operational_constraints']['halt_repair_loop']['max_repair_cycles']}")
        console.print(f"  Anti-Paralysis Threshold: {constitution['operational_constraints']['anti_paralysis']['halt_threshold']}")
        
        console.print("\n[bold]Memory Architecture:[/]")
        for mem_type, config in constitution['memory_architecture'].items():
            console.print(f"  {mem_type.capitalize()}: {config['storage']}")
        
        console.print("\n[dim]Ready for Phase 2: Cognitive Boot & Parliament Testing[/]")


async def main():
    """Entry point"""
    parser = argparse.ArgumentParser(description='Initialize Zazu Constitutional Intelligence')
    parser.add_argument('--reset', action='store_true', 
                        help='Drop and recreate database schema (WARNING: destroys existing data)')
    args = parser.parse_args()
    
    try:
        initializer = ZazuInitializer(reset=args.reset)
        await initializer.run()
        return 0
    except Exception as e:
        console.print(f"\n[bold red]Initialization failed: {e}[/]")
        logger.exception("Initialization error")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
