"""
Unit tests for Interpreter Agent
"""

import pytest
import asyncio

from agents.interpreter_agent import InterpreterAgent


@pytest.fixture
async def interpreter():
    """Fixture providing initialized Interpreter agent"""
    agent = InterpreterAgent(
        constitution_path="core/constitution.json",
        redis_url="redis://localhost:6379",
        postgres_dsn="postgresql://zazu:zazu_dev_password@localhost:5432/zazu_memory"
    )
    await agent.initialize()
    yield agent
    await agent.shutdown()


class TestIntentParsing:
    """Test semantic parsing and intent classification"""
    
    @pytest.mark.asyncio
    async def test_query_intent_detection(self, interpreter):
        """Verify query intents are correctly classified"""
        result = await interpreter.process({
            'user_input': 'What is my current mission status?',
            'context': {}
        })
        
        assert result['intent']['action_type'] == 'query'
        assert 'mission' in result['intent']['primary_goal'].lower()
    
    @pytest.mark.asyncio
    async def test_create_intent_detection(self, interpreter):
        """Verify create intents are correctly classified"""
        result = await interpreter.process({
            'user_input': 'Create a new file called test.txt',
            'context': {}
        })
        
        assert result['intent']['action_type'] == 'create'
        assert 'file' in result['intent']['primary_goal'].lower()
    
    @pytest.mark.asyncio
    async def test_execute_intent_detection(self, interpreter):
        """Verify execute intents are correctly classified"""
        result = await interpreter.process({
            'user_input': 'Run the backup command now',
            'context': {}
        })
        
        assert result['intent']['action_type'] == 'execute'
    
    @pytest.mark.asyncio
    async def test_reflect_intent_detection(self, interpreter):
        """Verify reflect intents are correctly classified"""
        result = await interpreter.process({
            'user_input': 'Reflect on recent progress and coherence',
            'context': {}
        })
        
        assert result['intent']['action_type'] == 'reflect'


class TestAmbiguityDetection:
    """Test ambiguity detection in user input"""
    
    @pytest.mark.asyncio
    async def test_vague_pronoun_detection(self, interpreter):
        """Verify vague pronouns are flagged"""
        result = await interpreter.process({
            'user_input': 'Delete it from the system',
            'context': {}
        })
        
        assert result['intent']['requires_clarification'] == True
        assert len(result['intent']['ambiguities']) > 0
        assert any('it' in amb.lower() for amb in result['intent']['ambiguities'])
    
    @pytest.mark.asyncio
    async def test_missing_execution_target(self, interpreter):
        """Verify execution without target is flagged"""
        result = await interpreter.process({
            'user_input': 'Execute the task',
            'context': {}
        })
        
        # Should flag missing execution target
        assert result['intent']['requires_clarification'] == True
    
    @pytest.mark.asyncio
    async def test_clear_input_no_ambiguity(self, interpreter):
        """Verify clear inputs pass without ambiguity"""
        result = await interpreter.process({
            'user_input': 'Create a file called output.txt with content "Hello World"',
            'context': {}
        })
        
        # Should not require clarification
        assert result['intent']['requires_clarification'] == False


class TestRouting:
    """Test routing logic to subsystems"""
    
    @pytest.mark.asyncio
    async def test_query_routes_to_interpreter(self, interpreter):
        """Verify queries stay with Interpreter by default"""
        result = await interpreter.process({
            'user_input': 'What are the available commands?',
            'context': {}
        })
        
        assert result['routing']['target_subsystem'] == 'interpreter'
    
    @pytest.mark.asyncio
    async def test_mission_query_routes_to_mirror(self, interpreter):
        """Verify mission queries route to Mirror"""
        result = await interpreter.process({
            'user_input': 'What is my current mission?',
            'context': {}
        })
        
        assert result['routing']['target_subsystem'] == 'mirror'
    
    @pytest.mark.asyncio
    async def test_execute_routes_to_executor(self, interpreter):
        """Verify execution requests route to Executor"""
        result = await interpreter.process({
            'user_input': 'Execute the deployment script',
            'context': {}
        })
        
        assert result['routing']['target_subsystem'] == 'executor'
    
    @pytest.mark.asyncio
    async def test_narrative_creation_routes_to_artisan(self, interpreter):
        """Verify narrative creation routes to Artisan"""
        result = await interpreter.process({
            'user_input': 'Create a mythos narrative about the void',
            'context': {}
        })
        
        assert result['routing']['target_subsystem'] == 'artisan'
    
    @pytest.mark.asyncio
    async def test_mode_suggestion(self, interpreter):
        """Verify mode suggestions are appropriate"""
        # Query should suggest inquiry mode
        result_query = await interpreter.process({
            'user_input': 'What is the system status?',
            'context': {}
        })
        assert result_query['routing']['suggested_mode'] == 'inquiry'
        
        # Execute should suggest execution mode
        result_exec = await interpreter.process({
            'user_input': 'Run the backup task',
            'context': {}
        })
        assert result_exec['routing']['suggested_mode'] == 'execution'


class TestConstitutionalConstraints:
    """Test Interpreter constraint enforcement"""
    
    @pytest.mark.asyncio
    async def test_cannot_route_execution_to_self(self, interpreter):
        """Verify Interpreter doesn't try to handle execution itself"""
        result = await interpreter.process({
            'user_input': 'Execute command "ls -la"',
            'context': {}
        })
        
        # Should route to Executor, not stay with Interpreter
        assert result['routing']['target_subsystem'] != 'interpreter'
        assert result['routing']['target_subsystem'] == 'executor'
    
    @pytest.mark.asyncio
    async def test_routing_confidence(self, interpreter):
        """Verify confidence drops with ambiguity"""
        # Clear input
        result_clear = await interpreter.process({
            'user_input': 'Create a new file called data.json',
            'context': {}
        })
        
        # Ambiguous input
        result_ambiguous = await interpreter.process({
            'user_input': 'Do that thing with it',
            'context': {}
        })
        
        # Confidence should be lower for ambiguous input
        assert result_ambiguous['routing']['confidence'] < result_clear['routing']['confidence']


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
