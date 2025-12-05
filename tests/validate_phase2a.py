#!/usr/bin/env python3
"""
Quick validation script for Phase 2A agents
Tests each agent in isolation without pytest
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.interpreter_agent import InterpreterAgent
from agents.executor_agent import ExecutorAgent
from agents.mirror_agent import MirrorAgent


async def test_interpreter():
    """Test Interpreter agent"""
    print("\n🧠 Testing Interpreter Agent...")
    
    agent = InterpreterAgent(
        constitution_path="core/constitution.json",
        redis_url="redis://localhost:6379",
        postgres_dsn="postgresql://zazu:zazu_dev_password@localhost:5432/zazu_memory"
    )
    await agent.initialize()
    
    try:
        # Test 1: Query intent
        result1 = await agent.process({
            'user_input': 'What is my current mission?',
            'context': {}
        })
        assert result1['intent']['action_type'] == 'query'
        assert result1['routing']['target_subsystem'] == 'mirror'
        print("  ✓ Query intent parsing and routing")
        
        # Test 2: Execute intent
        result2 = await agent.process({
            'user_input': 'Run the backup script',
            'context': {}
        })
        assert result2['intent']['action_type'] == 'execute'
        assert result2['routing']['target_subsystem'] == 'executor'
        print("  ✓ Execute intent parsing and routing")
        
        # Test 3: Ambiguity detection  
        result3 = await agent.process({
            'user_input': 'Delete it now',
            'context': {}
        })
        assert result3['intent']['requires_clarification'] == True
        print("  ✓ Ambiguity detection")
        
        print("✅ Interpreter Agent: All tests passed\n")
        return True
        
    finally:
        await agent.shutdown()


async def test_executor():
    """Test Executor agent"""
    print("⚙️  Testing Executor Agent...")
    
    agent = ExecutorAgent(
        constitution_path="core/constitution.json",
        redis_url="redis://localhost:6379",
        postgres_dsn="postgresql://zazu:zazu_dev_password@localhost:5432/zazu_memory"
    )
    await agent.initialize()
    
    try:
        # Test: File write (skip approval for test)
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            
            result = await agent.process({
                'task': {
                    'type': 'file_write',
                    'parameters': {
                        'path': str(test_file),
                        'content': 'Zazu test'
                    }
                },
                'skip_approval': True
            })
            
            assert result['execution_result']['status'] == 'success'
            assert test_file.exists()
            assert test_file.read_text() == 'Zazu test'
            print("  ✓ File write execution")
            
        # Test: Path validation
        result2 = await agent.process({
            'task': {
                'type': 'file_write',
                'parameters': {
                    'path': '/etc/passwd',
                    'content': 'bad'
                }
            },
            'skip_approval': True
        })
        assert result2['execution_result']['status'] == 'failure'
        print("  ✓ Path validation")
        
        print("✅ Executor Agent: All tests passed\n")
        return True
        
    finally:
        await agent.shutdown()


async def test_mirror():
    """Test Mirror agent"""
    print("🪞 Testing Mirror Agent...")
    
    agent = MirrorAgent(
        constitution_path="core/constitution.json",
        redis_url="redis://localhost:6379",
        postgres_dsn="postgresql://zazu:zazu_dev_password@localhost:5432/zazu_memory"
    )
    await agent.initialize()
    
    try:
        # Test: Coherence and reflection
        result = await agent.process({
            'event': {
                'type': 'action',
                'subsystem': 'executor',
                'description': 'Amplify ordered intelligence in service of creative power',
                'outcome': {'status': 'success'}
            },
            'context': {}
        })
        
        assert 'coherence_score' in result['reflection']
        assert 0.0 <= result['reflection']['coherence_score'] <= 1.0
        print("  ✓ Coherence scoring")
        
        assert 'emotional_load_estimate' in result['reflection']
        print("  ✓ Emotional load detection")
        
        assert 'recommendations' in result
        assert len(result['recommendations']) > 0
        print("  ✓ Recommendations generation")
        
        assert result['reflection']['philosophical_alignment'] == True
        print("  ✓ Philosophical alignment check")
        
        print("✅ Mirror Agent: All tests passed\n")
        return True
        
    finally:
        await agent.shutdown()


async def main():
    print("\n" + "="*60)
    print("  ZAZU PHASE 2A AGENT VALIDATION")
    print("="*60)
    
    try:
        # Test all agents
        results = await asyncio.gather(
            test_interpreter(),
            test_executor(),
            test_mirror(),
            return_exceptions=True
        )
        
        # Check results
        all_passed = all(r == True for r in results if not isinstance(r, Exception))
        
        if all_passed:
            print("="*60)
            print("  ✅ ALL AGENTS VALIDATED SUCCESSFULLY")
            print("="*60)
            return 0
        else:
            print("="*60)
            print("  ❌ SOME TESTS FAILED")
            for i, r in enumerate(results):
                if isinstance(r, Exception):
                    print(f"Agent {i} error: {r}")
            print("="*60)
            return 1
            
    except Exception as e:
        print(f"\n❌ Validation failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
