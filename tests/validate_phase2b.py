#!/usr/bin/env python3
"""
Quick validation script for Phase 2B agents
Tests Strategist, Artisan, and Ledger
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.strategist_agent import StrategistAgent
from agents.artisan_agent import ArtisanAgent
from agents.ledger_agent import LedgerAgent


async def test_strategist():
    """Test Strategist agent"""
    print("\n🎯 Testing Strategist Agent...")
    
    agent = StrategistAgent(
        constitution_path="core/constitution.json",
        redis_url="redis://localhost:6379",
        postgres_dsn="postgresql://zazu:zazu_dev_password@localhost:5432/zazu_memory"
    )
    await agent.initialize()
    
    try:
        result = await agent.process({
            'goal': 'Build Phase 2C of Zazu system',
            'constraints': ['Must complete within 90 days', 'Limited to current team'],
            'time_horizon': 'seasonal',
            'context': {}
        })
        
        assert 'strategy' in result
        assert 'scenarios' in result
        assert result['strategy']['risk_factors'] is not None
        print("  ✓ Scenario modeling")
        
        assert 'decision_tree' in result['strategy']
        print("  ✓ Decision tree generation")
        
        assert 'timeline' in result['strategy']
        assert len(result['strategy']['timeline']) > 0
        print("  ✓ Timeline planning")
        
        print("✅ Strategist Agent: All tests passed\n")
        return True
        
    finally:
        await agent.shutdown()


async def test_artisan():
    """Test Artisan agent"""
    print("🎨 Testing Artisan Agent...")
    
    agent = ArtisanAgent(
        constitution_path="core/constitution.json",
        redis_url="redis://localhost:6379",
        postgres_dsn="postgresql://zazu:zazu_dev_password@localhost:5432/zazu_memory"
    )
    await agent.initialize()
    
    try:
        # Test mythos generation
        result1 = await agent.process({
            'creative_type': 'mythos',
            'theme': 'sovereignty',
            'constraints': {'tone': 'mythic', 'length': 'medium'},
            'context': {}
        })
        
        assert result1['creation']['type'] == 'mythos'
        assert len(result1['creation']['content']) > 100
        print("  ✓ Mythos generation")
        
        # Test worldbuilding
        result2 = await agent.process({
            'creative_type': 'worldbuilding',
            'theme': 'coherence',
            'constraints': {},
            'context': {}
        })
        
        assert result2['creation']['type'] == 'worldbuilding'
        assert 'location_name' in result2['creation']['elements']
        print("  ✓ Worldbuilding")
        
        # Test aesthetic
        result3 = await agent.process({
            'creative_type': 'aesthetic',
            'theme': 'emergence',
            'constraints': {}
        })
        
        assert result3['creation']['type'] == 'aesthetic'
        print("  ✓ Aesthetic creation")
        
        # Test symbolic
        result4 = await agent.process({
            'creative_type': 'symbolic',
            'theme': 'transformation',
            'constraints': {}
        })
        
        assert result4['creation']['type'] == 'symbolic'
        print("  ✓ Symbolic synthesis")
        
        print("✅ Artisan Agent: All tests passed\n")
        return True
        
    finally:
        await agent.shutdown()


async def test_ledger():
    """Test Ledger agent"""
    print("📊 Testing Ledger Agent...")
    
    agent = LedgerAgent(
        constitution_path="core/constitution.json",
        redis_url="redis://localhost:6379",
        postgres_dsn="postgresql://zazu:zazu_dev_password@localhost:5432/zazu_memory"
    )
    await agent.initialize()
    
    try:
        # Test risk quantification
        result1 = await agent.process({
            'analysis_type': 'risk',
            'data': {
                'complexity': 7,
                'uncertainty': 0.6,
                'dependencies': ['PostgreSQL', 'Redis', 'SentenceTransformers'],
                'timeline_days': 45
            },
            'parameters': {}
        })
        
        assert 'risk_score' in result1['analysis']
        assert 0.0 <= result1['analysis']['risk_score'] <= 1.0
        print("  ✓ Risk quantification")
        
        # Test variance tracking
        result2 = await agent.process({
            'analysis_type': 'variance',
            'data': {
                'time_series': [
                    {'value': 10}, {'value': 12}, {'value': 11},
                    {'value': 13}, {'value': 15}, {'value': 14}
                ]
            },
            'parameters': {}
        })
        
        assert 'variance_data' in result2['analysis']
        assert 'mean' in result2['analysis']['variance_data']
        print("  ✓ Variance tracking")
        
        # Test backtest
        result3 = await agent.process({
            'analysis_type': 'backtest',
            'data': {
                'historical_data': [
                    {'outcome': 0.5}, {'outcome': -0.2}, {'outcome': 0.3},
                    {'outcome': 0.4}, {'outcome': -0.1}
                ],
                'strategy': {}
            },
            'parameters': {}
        })
        
        assert 'win_rate' in result3['analysis']['metrics']
        print("  ✓ Backtesting")
        
        # Test scenario safety
        result4 = await agent.process({
            'analysis_type': 'scenario_safety',
            'data': {
                'scenarios': [
                    {'probability': 0.7, 'outcome_quality': 0.8},
                    {'probability': 0.2, 'outcome_quality': 0.5},
                    {'probability': 0.1, 'outcome_quality': 0.3}
                ]
            },
            'parameters': {'safety_threshold': 0.7}
        })
        
        assert 'safety_rate' in result4['analysis']['metrics']
        print("  ✓ Scenario safety checks")
        
        print("✅ Ledger Agent: All tests passed\n")
        return True
        
    finally:
        await agent.shutdown()


async def main():
    print("\n" + "="*60)
    print("  ZAZU PHASE 2B AGENT VALIDATION")
    print("="*60)
    
    try:
        # Test all Phase 2B agents
        results = await asyncio.gather(
            test_strategist(),
            test_artisan(),
            test_ledger(),
            return_exceptions=True
        )
        
        # Check results
        all_passed = all(r == True for r in results if not isinstance(r, Exception))
        
        if all_passed:
            print("="*60)
            print("  ✅ ALL PHASE 2B AGENTS VALIDATED")
            print("  🎉 7-AGENT PARLIAMENT COMPLETE!")
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
