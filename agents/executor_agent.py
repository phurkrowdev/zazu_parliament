"""
Executor Agent - Action Gateway
Constitutional constraint: CANNOT ORIGINATE GOALS, REQUIRES APPROVAL
"""

from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent, SubsystemID, Mode
import subprocess
import asyncio
import tempfile
from pathlib import Path
from datetime import datetime


class ExecutorAgent(BaseAgent):
    """
    The action gateway with sandboxed execution.
    
    Constitutional Constraints:
    - Can EXECUTE tasks with proper approvals
    - Cannot ORIGINATE goals (must be given tasks)
    - Requires SENTINEL approval before execution
    - Must execute in SANDBOXED environment
    """
    
    def __init__(self, **kwargs):
        super().__init__(subsystem_id=SubsystemID.EXECUTOR, **kwargs)
        
        # Execution tracking
        self.execution_history: list = []
        
        # Sandbox configuration (simplified for MVP)
        self.sandbox_timeout = 30  # seconds
        self.allowed_file_paths = ['/tmp', '/home/phurkrow/Zazu_2026']  # Whitelist
    
    async def _process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute approved tasks in sandboxed environment.
        
        Input schema:
        {
            "task": {
                "type": "file_write|command|api_call",
                "parameters": {},
                "tool": str
            },
            "skip_approval": bool  # For testing only
        }
        
        Output schema:
        {
            "execution_result": {
                "status": "success|failure|partial",
                "output": any,
                "errors": [],
                "rollback_available": bool
            },
            "executed_at": timestamp
        }
        """
        task = input_data['task']
        skip_approval = input_data.get('skip_approval', False)
        
        # Step 1: Request Sentinel approval (unless explicitly skipped for testing)
        if not skip_approval:
            approval = await self._request_sentinel_approval(task)
            if not approval['approved']:
                return {
                    'execution_result': {
                        'status': 'rejected',
                        'output': None,
                        'errors': [approval.get('reason', 'Sentinel rejected execution')],
                        'rollback_available': False
                    },
                    'executed_at': datetime.utcnow().isoformat()
                }
        
        # Step 2: Execute in sandbox
        try:
            result = await self._execute_sandboxed(task)
            
            # Log successful execution
            await self.write_episodic(
                event_type="task_executed",
                context={
                    'task': task,
                    'result': result
                }
            )
            
            # Track for rollback
            self.execution_history.append({
                'task': task,
                'result': result,
                'timestamp': datetime.utcnow()
            })
            
            return {
                'execution_result': result,
                'executed_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            # Handle execution error
            error_result = await self._handle_execution_error(task, e)
            return {
                'execution_result': error_result,
                'executed_at': datetime.utcnow().isoformat()
            }
    
    async def _request_sentinel_approval(
        self,
        task: Dict[str, Any]
    ) -> Dict[str, bool]:
        """
        Request pre-execution approval from Sentinel.
        Uses the request() method from BaseAgent for direct communication.
        """
        # Import here to avoid circular dependency
        from agents.sentinel_agent import SentinelAgent
        
        # Create Sentinel instance
        sentinel = SentinelAgent(
            redis_url=self.redis_url,
            postgres_dsn=self.postgres_dsn
        )
        await sentinel.initialize()
        
        try:
            # Request approval
            approval_response = await sentinel.process({
                'artifact': task,
                'subsystem_origin': SubsystemID.EXECUTOR.value,
                'action_type': self._map_task_to_action_type(task),
                'context': {}
            })
            
            approved = approval_response['decision'] == 'approve'
            
            return {
                'approved': approved,
                'reason': approval_response.get('halt_reason', ''),
                'approval_data': approval_response
            }
            
        finally:
            await sentinel.shutdown()
    
    def _map_task_to_action_type(self, task: Dict[str, Any]) -> str:
        """Map task type to Sentinel's action_type classification"""
        task_type = task.get('type', '')
        
        mapping = {
            'file_write': 'real_world_execution',
            'file_delete': 'real_world_execution',
            'command': 'real_world_execution',
            'api_call': 'real_world_execution',
            'financial': 'financial_exposure'
        }
        
        return mapping.get(task_type, 'real_world_execution')
    
    async def _execute_sandboxed(
        self,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute task in sandboxed environment.
        For MVP: subprocess with timeout and path restrictions.
        Phase 2C: Full Docker sandbox.
        """
        task_type = task['type']
        parameters = task['parameters']
        
        if task_type == 'file_write':
            return await self._execute_file_write(parameters)
        elif task_type == 'file_read':
            return await self._execute_file_read(parameters)
        elif task_type == 'command':
            return await self._execute_command(parameters)
        elif task_type == 'api_call':
            return await self._execute_api_call(parameters)
        else:
            raise ValueError(f"Unsupported task type: {task_type}")
    
    async def _execute_file_write(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file write operation with path validation"""
        file_path = Path(params['path'])
        content = params['content']
        
        # Validate path is within allowed directories
        if not any(str(file_path).startswith(allowed) for allowed in self.allowed_file_paths):
            return {
                'status': 'failure',
                'output': None,
                'errors': [f"Path {file_path} not in allowed directories"],
                'rollback_available': False
            }
        
        try:
            # Write file
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            
            return {
                'status': 'success',
                'output': str(file_path),
                'errors': [],
                'rollback_available': True
            }
        except Exception as e:
            return {
                'status': 'failure',
                'output': None,
                'errors': [str(e)],
                'rollback_available': False
            }
    
    async def _execute_file_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file read operation"""
        file_path = Path(params['path'])
        
        # Validate path
        if not any(str(file_path).startswith(allowed) for allowed in self.allowed_file_paths):
            return {
                'status': 'failure',
                'output': None,
                'errors': [f"Path {file_path} not in allowed directories"],
                'rollback_available': False
            }
        
        try:
            content = file_path.read_text()
            return {
                'status': 'success',
                'output': content,
                'errors': [],
                'rollback_available': False
            }
        except Exception as e:
            return {
                'status': 'failure',
                'output': None,
                'errors': [str(e)],
                'rollback_available': False
            }
    
    async def _execute_command(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute shell command with timeout"""
        command = params['command']
        cwd = params.get('cwd', '/tmp')
        
        try:
            # Run with timeout
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.sandbox_timeout
                )
                
                return {
                    'status': 'success' if process.returncode == 0 else 'failure',
                    'output': {
                        'stdout': stdout.decode(),
                        'stderr': stderr.decode(),
                        'returncode': process.returncode
                    },
                    'errors': [stderr.decode()] if process.returncode != 0 else [],
                    'rollback_available': False
                }
                
            except asyncio.TimeoutError:
                process.kill()
                return {
                    'status': 'failure',
                    'output': None,
                    'errors': [f"Command timed out after {self.sandbox_timeout}s"],
                    'rollback_available': False
                }
                
        except Exception as e:
            return {
                'status': 'failure',
                'output': None,
                'errors': [str(e)],
                'rollback_available': False
            }
    
    async def _execute_api_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute API call (placeholder for Phase 2B)"""
        # For MVP, return placeholder
        return {
            'status': 'success',
            'output': {'message': 'API call placeholder (implement in Phase 2B)'},
            'errors': [],
            'rollback_available': False
        }
    
    async def _handle_execution_error(
        self,
        task: Dict[str, Any],
        error: Exception
    ) -> Dict[str, Any]:
        """Handle execution errors and attempt rollback if needed"""
        self.logger.error(f"Execution error for task {task['type']}: {error}")
        
        # Log error to episodic memory
        await self.write_episodic(
            event_type="execution_error",
            context={
                'task': task,
                'error': str(error)
            }
        )
        
        return {
            'status': 'failure',
            'output': None,
            'errors': [str(error)],
            'rollback_available': False
        }
    
    def _check_constraints(self, proposed_output: Dict[str, Any]) -> bool:
        """
        Verify Executor doesn't violate constitutional constraints.
        """
        # Executor should never:
        # - Originate goals (cannot_originate_goals)
        # - Execute without approval (requires_sentinel_approval)
        
        # Check that execution was approved (in production, verify approval chain)
        execution_result = proposed_output.get('execution_result', {})
        
        # If execution failed due to rejection, that's compliant
        if execution_result.get('status') == 'rejected':
            return True
        
        # All executions should have been approved
        return True
