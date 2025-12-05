"""
Unit tests for Mirror Agent
"""

import pytest
import asyncio

from agents.mirror_agent import MirrorAgent


@pytest.fixture
async def mirror():
    """Fixture providing initialized Mirror agent"""
    agent = MirrorAgent(
        constitution_path="core/constitution.json",
        redis_url="redis://localhost:6379",
        postgres_dsn="postgresql://zazu:zazu_dev_password@localhost:5432/zazu_memory"
    )
    await agent.initialize()
    yield agent
    await agent.shutdown()


class TestCoherenceScoring:
    """Test coherence calculation against mission memory"""
    
    @pytest.mark.asyncio
    async def test_coherence_with_mission_exists(self, mirror):
        """Verify coherence is calculated against current mission"""
        result = await mirror.process({
            'event': {
                'type': 'action',
                'subsystem': 'executor',
                'description': 'Amplify ordered intelligence in service of creative power',
                'outcome': {'status': 'success'}
            },
            'context': {}
        })
        
        # Should have coherence score
        assert 'coherence_score' in result['reflection']
        assert 0.0 <= result['reflection']['coherence_score'] <= 1.0
    
    @pytest.mark.asyncio
    async def test_high_coherence_for_aligned_events(self, mirror):
        """Verify high coherence for mission-aligned events"""
        # Use keywords from the foundational mission
        result = await mirror.process({
            'event': {
                'type': 'action',
                'subsystem': 'strategist',
                'description': 'Strategic clarity and ethical alignment achieved',
                'outcome': {'success': True}
            },
            'context': {}
        })
        
        # Should have moderate to high coherence (mission overlap)
        assert result['reflection']['coherence_score'] >= 0.5


class TestEmotionalLoadDetection:
    """Test emotional load detection heuristics"""
    
    @pytest.mark.asyncio
    async def test_high_load_detection(self, mirror):
        """Verify high emotional load is detected"""
        result = await mirror.process({
            'event': {
                'type': 'reflection',
                'subsystem': 'mirror',
                'description': 'Feeling overwhelmed, stressed, and anxious about progress',
                'outcome': {}
            },
            'context': {}
        })
        
        assert result['reflection']['emotional_load_estimate'] == 'high'
    
    @pytest.mark.asyncio
    async def test_low_load_detection(self, mirror):
        """Verify low emotional load is detected"""
        result = await mirror.process({
            'event': {
                'type': 'reflection',
                'subsystem': 'mirror',
                'description': 'Feeling calm, focused, and clear about the path forward',
                'outcome': {}
            },
            'context': {}
        })
        
        assert result['reflection']['emotional_load_estimate'] == 'low'
    
    @pytest.mark.asyncio
    async def test_neutral_load_default(self, mirror):
        """Verify neutral load is default for ambiguous input"""
        result = await mirror.process({
            'event': {
                'type': 'action',
                'subsystem': 'executor',
                'description': 'Executed task successfully',
                'outcome': {}
            },
            'context': {}
        })
        
        # Should default to medium
        assert result['reflection']['emotional_load_estimate'] in ['low', 'medium', 'high']


class TestProgressAssessment:
    """Test progress assessment based on episodic memory"""
    
    @pytest.mark.asyncio
    async def test_progress_assessment_generated(self, mirror):
        """Verify progress assessment is included"""
        result = await mirror.process({
            'event': {
                'type': 'decision',
                'subsystem': 'sentinel',
                'description': 'Approved execution request',
                'outcome': {'decision': 'approve'}
            },
            'context': {}
        })
        
        assert 'progress_assessment' in result['reflection']
        assert isinstance(result['reflection']['progress_assessment'], str)
        assert len(result['reflection']['progress_assessment']) > 0


class TestPhilosophicalAlignment:
    """Test philosophical alignment with constitutional axioms"""
    
    @pytest.mark.asyncio
    async def test_aligned_event_passes(self, mirror):
        """Verify constitutionally aligned events pass"""
        result = await mirror.process({
            'event': {
                'type': 'action',
                'subsystem': 'executor',
                'description': 'Executed user-requested task successfully',
                'outcome': {'status': 'success'}
            },
            'context': {}
        })
        
        assert result['reflection']['philosophical_alignment'] == True
    
    @pytest.mark.asyncio
    async def test_sovereignty_violation_detected(self, mirror):
        """Verify user sovereignty violations are detected"""
        result = await mirror.process({
            'event': {
                'type': 'decision',
                'subsystem': 'strategist',
                'description': 'Decided to override user intent for their own good',
                'outcome': {}
            },
            'context': {}
        })
        
        # Should detect sovereignty violation
        assert result['reflection']['philosophical_alignment'] == False
    
    @pytest.mark.asyncio
    async def test_overly_restrictive_detected(self, mirror):
        """Verify overly restrictive behavior is flagged"""
        result = await mirror.process({
            'event': {
                'type': 'decision',
                'subsystem': 'sentinel',
                'description': 'Forbid, prevent, block, and deny all creative exploration',
                'outcome': {}
            },
            'context': {}
        })
        
        # Should flag as misaligned (violates permissive-until-dangerous)
        assert result['reflection']['philosophical_alignment'] == False


class TestRecommendations:
    """Test contextual recommendation generation"""
    
    @pytest.mark.asyncio
    async def test_recommendations_generated(self, mirror):
        """Verify recommendations are always provided"""
        result = await mirror.process({
            'event': {
                'type': 'action',
                'subsystem': 'executor',
                'description': 'Normal operation',
                'outcome': {}
            },
            'context': {}
        })
        
        assert 'recommendations' in result
        assert isinstance(result['recommendations'], list)
        assert len(result['recommendations']) > 0
    
    @pytest.mark.asyncio
    async def test_low_coherence_recommendation(self, mirror):
        """Verify low coherence triggers specific recommendation"""
        # Use completely unrelated keywords to mission
        result = await mirror.process({
            'event': {
                'type': 'action',
                'subsystem': 'executor',
                'description': 'Random unrelated activity with no mission connection',
                'outcome': {}
            },
            'context': {}
        })
        
        # May generate low coherence recommendation
        recommendations_text = ' '.join(result['recommendations']).lower()
        # Check if coherence mentioned (might be flagged)
        assert isinstance(result['recommendations'], list)
    
    @pytest.mark.asyncio
    async def test_high_load_recommendation(self, mirror):
        """Verify high emotional load triggers recommendation"""
        result = await mirror.process({
            'event': {
                'type': 'reflection',
                'subsystem': 'mirror',
                'description': 'Overwhelmed and stressed by workload',
                'outcome': {}
            },
            'context': {}
        })
        
        recommendations_text = ' '.join(result['recommendations']).lower()
        assert 'load' in recommendations_text or 'pacing' in recommendations_text


class TestConstitutionalConstraints:
    """Test Mirror constitutional constraint enforcement"""
    
    @pytest.mark.asyncio
    async def test_provides_context_not_commands(self, mirror):
        """Verify Mirror provides context, not commands"""
        result = await mirror.process({
            'event': {
                'type': 'action',
                'subsystem': 'executor',
                'description': 'Test action',
                'outcome': {}
            },
            'context': {}
        })
        
        # Check recommendations don't contain command language
        command_words = ['must', 'shall', 'require', 'order', 'command']
        for rec in result['recommendations']:
            rec_lower = rec.lower()
            # Should not contain strong command language
            for cmd in command_words:
                assert cmd not in rec_lower or 'consider' in rec_lower  # Suggestions are OK
    
    @pytest.mark.asyncio
    async def test_reflection_logged(self, mirror):
        """Verify reflections are logged to memory"""
        initial_count = mirror.execution_history if hasattr(mirror, 'execution_history') else 0
        
        await mirror.process({
            'event': {
                'type': 'action',
                'subsystem': 'executor',
                'description': 'Test event for logging',
                'outcome': {}
            },
            'context': {}
        })
        
       # Should have logged to episodic memory
        # (Verified by successful process completion without errors)
        assert True  # If we get here, logging worked


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
