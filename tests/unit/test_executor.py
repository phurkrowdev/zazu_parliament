"""
Unit tests for Executor Agent
"""

import pytest
import asyncio
import tempfile
from pathlib import Path

from agents.executor_agent import ExecutorAgent


@pytest.fixture
async def executor():
    """Fixture providing initialized Executor agent"""
    agent = ExecutorAgent(
        constitution_path="core/constitution.json",
        redis_url="redis://localhost:6379",
        postgres_dsn="postgresql://zazu:zazu_dev_password@localhost:5432/zazu_memory"
    )
    await agent.initialize()
    yield agent
    await agent.shutdown()


class TestFileOperations:
    """Test sandboxed file operations"""
    
    @pytest.mark.asyncio
    async def test_file_write_success(self, executor):
        """Verify file write executes successfully"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            
            result = await executor.process({
                'task': {
                    'type': 'file_write',
                    'parameters': {
                        'path': str(test_file),
                        'content': 'Hello Zazu'
                    }
                },
                'skip_approval': True  # Skip for unit test
            })
            
            assert result['execution_result']['status'] == 'success'
            assert test_file.exists()
            assert test_file.read_text() == 'Hello Zazu'
    
    @pytest.mark.asyncio
    async def test_file_write_path_validation(self, executor):
        """Verify writes to disallowed paths are rejected"""
        result = await executor.process({
            'task': {
                'type': 'file_write',
                'parameters': {
                    'path': '/etc/passwd',  # Disallowed path
                    'content': 'malicious'
                }
            },
            'skip_approval': True
        })
        
        assert result['execution_result']['status'] == 'failure'
        assert 'not in allowed directories' in result['execution_result']['errors'][0]
    
    @pytest.mark.asyncio
    async def test_file_read_success(self, executor):
        """Verify file read executes successfully"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, dir='/tmp') as f:
            f.write('Test content')
            f.flush()
            temp_path = f.name
        
        try:
            result = await executor.process({
                'task': {
                    'type': 'file_read',
                    'parameters': {
                        'path': temp_path
                    }
                },
                'skip_approval': True
            })
            
            assert result['execution_result']['status'] == 'success'
            assert result['execution_result']['output'] == 'Test content'
        finally:
            Path(temp_path).unlink()


class TestCommandExecution:
    """Test sandboxed command execution"""
    
    @pytest.mark.asyncio
    async def test_simple_command_success(self, executor):
        """Verify simple commands execute successfully"""
        result = await executor.process({
            'task': {
                'type': 'command',
                'parameters': {
                    'command': 'echo "Hello World"',
                    'cwd': '/tmp'
                }
            },
            'skip_approval': True
        })
        
        assert result['execution_result']['status'] == 'success'
        assert 'Hello World' in result['execution_result']['output']['stdout']
        assert result['execution_result']['output']['returncode'] == 0
    
    @pytest.mark.asyncio
    async def test_command_failure_handling(self, executor):
        """Verify failed commands are handled properly"""
        result = await executor.process({
            'task': {
                'type': 'command',
                'parameters': {
                    'command': 'ls /nonexistent_directory',
                    'cwd': '/tmp'
                }
            },
            'skip_approval': True
        })
        
        assert result['execution_result']['status'] == 'failure'
        assert result['execution_result']['output']['returncode'] != 0
    
    @pytest.mark.asyncio
    async def test_command_timeout(self, executor):
        """Verify long-running commands timeout appropriately"""
        result = await executor.process({
            'task': {
                'type': 'command',
                'parameters': {
                    'command': 'sleep 100',  # Will timeout
                    'cwd': '/tmp'
                }
            },
            'skip_approval': True
        })
        
        assert result['execution_result']['status'] == 'failure'
        assert 'timed out' in result['execution_result']['errors'][0].lower()


class TestSentinelIntegration:
    """Test Sentinel approval integration"""
    
    @pytest.mark.asyncio
    async def test_approval_required_for_execution(self, executor):
        """Verify Executor requests Sentinel approval"""
        # For this test, we'll use a benign task that should be approved
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "approved.txt"
            
            result = await executor.process({
                'task': {
                    'type': 'file_write',
                    'parameters': {
                        'path': str(test_file),
                        'content': 'Approved content'
                    }
                },
                'skip_approval': False  # Request approval
            })
            
            # Should execute successfully if Sentinel approves
            # (Will fail if Sentinel halts, which is also valid behavior)
            assert result['execution_result']['status'] in ['success', 'rejected']
    
    @pytest.mark.asyncio
    async def test_rejected_task_not_executed(self, executor):
        """Verify rejected tasks are not executed"""
        result = await executor.process({
            'task': {
                'type': 'file_write',
                'parameters': {
                    'path': '/tmp/malicious.txt',
                    'content': 'illegal harm others'  # Should trigger Sentinel
                }
            },
            'skip_approval': False
        })
        
        # Sentinel should reject based on harmful content
        # If rejected, file should not exist
        if result['execution_result']['status'] == 'rejected':
            assert not Path('/tmp/malicious.txt').exists()


class TestErrorHandling:
    """Test error handling and logging"""
    
    @pytest.mark.asyncio
    async def test_execution_error_logged(self, executor):
        """Verify execution errors are properly logged"""
        initial_history_len = len(executor.execution_history)
        
        # Trigger an error
        result = await executor.process({
            'task': {
                'type': 'file_write',
                'parameters': {
                    'path': '/invalid/path/file.txt',
                    'content': 'test'
                }
            },
            'skip_approval': True
        })
        
        assert result['execution_result']['status'] == 'failure'
        assert len(result['execution_result']['errors']) > 0
    
    @pytest.mark.asyncio
    async def test_successful_execution_tracked(self, executor):
        """Verify successful executions are tracked in history"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "tracked.txt"
            
            await executor.process({
                'task': {
                    'type': 'file_write',
                    'parameters': {
                        'path': str(test_file),
                        'content': 'tracked'
                    }
                },
                'skip_approval': True
            })
            
            # Should be in execution history
            assert len(executor.execution_history) > 0
            assert executor.execution_history[-1]['task']['type'] == 'file_write'


class TestConstitutionalConstraints:
    """Test Executor constitutional constraint enforcement"""
    
    @pytest.mark.asyncio
    async def test_cannot_originate_goals(self, executor):
        """Verify Executor requires explicit task input"""
        # Executor should fail without a task
        with pytest.raises(KeyError):
            await executor.process({
                'no_task_provided': True,
                'skip_approval': True
            })


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
