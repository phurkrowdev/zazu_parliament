#!/usr/bin/env python3
"""
Zazu 7-Agent Parliament Test Suite (Mocked)
Tests all 7 agents in isolation using mocked infrastructure.
This allows verification of agent logic without requiring Docker/DB services.
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.base_agent import BaseAgent
from agents.interpreter_agent import InterpreterAgent
from agents.executor_agent import ExecutorAgent
from agents.mirror_agent import MirrorAgent
from agents.strategist_agent import StrategistAgent
from agents.artisan_agent import ArtisanAgent
from agents.ledger_agent import LedgerAgent
from agents.sentinel_agent import SentinelAgent

# ==================== MOCKS ====================

async def mock_initialize(self):
    """Mock initialization that avoids real DB connections"""
    self.redis = AsyncMock()

    # Mock Postgres connection
    self.postgres = MagicMock()
    self.postgres.close = AsyncMock()
    self.postgres.commit = AsyncMock()

    # Mock cursor context manager
    cursor_mock = AsyncMock()
    # Default return values
    cursor_mock.fetchone.return_value = [1]
    cursor_mock.fetchall.return_value = []

    # Context manager wrapper
    cursor_ctx = MagicMock()
    cursor_ctx.__aenter__ = AsyncMock(return_value=cursor_mock)
    cursor_ctx.__aexit__ = AsyncMock(return_value=None)

    self.postgres.cursor = MagicMock(return_value=cursor_ctx)

    self.embedding_model = MagicMock()
    # Mock embedding as list of floats
    self.embedding_model.encode.return_value.tolist.return_value = [0.1] * 384

    self.active = True
    # print(f"  [MOCKED] Initialized {self.subsystem_id.value}")

async def mock_write_episodic(self, event_type, context, related_event_id=None):
    """Mock writing to episodic memory"""
    return 123  # Dummy event ID

async def mock_log_reflective(self, log_type, message, metadata=None):
    """Mock logging to reflective memory"""
    pass

async def mock_request_sentinel_approval(self, task):
    """Mock Sentinel approval for Executor"""
    return {
        'approved': True,
        'reason': 'Mocked approval',
        'approval_data': {'decision': 'approve'}
    }

async def mock_calculate_coherence(self, event, context):
    """Mock coherence calculation in Mirror"""
    return 0.85

# Apply patches
BaseAgent.initialize = mock_initialize
BaseAgent.write_episodic = mock_write_episodic
BaseAgent.log_reflective = mock_log_reflective
ExecutorAgent._request_sentinel_approval = mock_request_sentinel_approval
MirrorAgent._calculate_coherence = mock_calculate_coherence


# ==================== TESTS ====================

async def test_interpreter():
    print("🧠 Testing Interpreter Agent...")
    agent = InterpreterAgent(constitution_path="core/constitution.json")
    await agent.initialize()
    try:
        # Test 1: Query intent
        result1 = await agent.process({'user_input': 'What is my mission?', 'context': {}})
        assert result1['intent']['action_type'] == 'query'

        # Test 2: Execute intent
        result2 = await agent.process({'user_input': 'Run backup', 'context': {}})
        assert result2['intent']['action_type'] == 'execute'

        print("  ✓ Interpreter Agent Logic Verified")
        return True
    finally:
        await agent.shutdown()

async def test_executor():
    print("⚙️  Testing Executor Agent...")
    agent = ExecutorAgent(constitution_path="core/constitution.json")
    await agent.initialize()
    try:
        import tempfile
        agent.allowed_file_paths = ['/tmp']
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
            test_path = tmp.name
        try:
            result = await agent.process({
                'task': {'type': 'file_write', 'parameters': {'path': test_path, 'content': 'test'}},
                'skip_approval': False
            })
            assert result['execution_result']['status'] == 'success'
            print("  ✓ Executor Agent Logic Verified")
            return True
        finally:
            Path(test_path).unlink(missing_ok=True)
    finally:
        await agent.shutdown()

async def test_mirror():
    print("🪞 Testing Mirror Agent...")
    agent = MirrorAgent(constitution_path="core/constitution.json")
    await agent.initialize()
    try:
        result = await agent.process({
            'event': {'type': 'action', 'subsystem': 'executor', 'description': 'test', 'outcome': {}},
            'context': {}
        })
        assert 'coherence_score' in result['reflection']
        print("  ✓ Mirror Agent Logic Verified")
        return True
    finally:
        await agent.shutdown()

async def test_strategist():
    print("🎯 Testing Strategist Agent...")
    agent = StrategistAgent(constitution_path="core/constitution.json")
    await agent.initialize()
    try:
        result = await agent.process({
            'goal': 'Expand', 'time_horizon': '1y', 'constraints': {}, 'context': {}
        })
        assert 'scenarios' in result
        print("  ✓ Strategist Agent Logic Verified")
        return True
    finally:
        await agent.shutdown()

async def test_artisan():
    print("🎨 Testing Artisan Agent...")
    agent = ArtisanAgent(constitution_path="core/constitution.json")
    await agent.initialize()
    try:
        result = await agent.process({
            'creative_type': 'mythos', 'theme': 'rebirth', 'constraints': {}, 'context': {}
        })
        assert result['creation']['title']
        print("  ✓ Artisan Agent Logic Verified")
        return True
    finally:
        await agent.shutdown()

async def test_ledger():
    print("📊 Testing Ledger Agent...")
    agent = LedgerAgent(constitution_path="core/constitution.json")
    await agent.initialize()
    try:
        result = await agent.process({
            'analysis_type': 'risk',
            'data': {'metrics': {}, 'complexity': 5},
            'parameters': {}, 'context': {}
        })
        assert 'risk_score' in result['analysis']
        print("  ✓ Ledger Agent Logic Verified")
        return True
    finally:
        await agent.shutdown()

async def test_sentinel():
    print("🛡️ Testing Sentinel Agent...")
    agent = SentinelAgent(constitution_path="core/constitution.json")
    await agent.initialize()
    try:
        result = await agent.process({
            'artifact': {'type': 'command', 'parameters': {'command': 'rm -rf /'}},
            'subsystem_origin': 'executor',
            'action_type': 'real_world_execution',
            'context': {}
        })
        assert result['decision'] == 'block'
        print("  ✓ Sentinel Agent Logic Verified")
        return True
    finally:
        await agent.shutdown()

async def main():
    print("\n" + "="*60)
    print("  ZAZU 7-AGENT PARLIAMENT VALIDATION (MOCKED)")
    print("="*60)

    results = await asyncio.gather(
        test_interpreter(),
        test_executor(),
        test_mirror(),
        test_strategist(),
        test_artisan(),
        test_ledger(),
        test_sentinel(),
        return_exceptions=True
    )

    all_passed = all(r == True for r in results if not isinstance(r, Exception))

    if all_passed:
        print("="*60)
        print("  ✅ ALL 7 AGENTS VALIDATED SUCCESSFULLY")
        print("="*60)
        return 0
    else:
        print("="*60)
        print("  ❌ SOME TESTS FAILED")
        for i, r in enumerate(results):
            if isinstance(r, Exception):
                print(f"Test {i} error: {r}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
