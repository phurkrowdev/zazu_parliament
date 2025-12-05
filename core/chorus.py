"""
Chorus Orchestrator - Parliamentary Intelligence Coordinator
Manages all 7 agents and orchestrates multi-agent workflows
"""

from typing import Dict, Any, List, Optional
from enum import Enum
import asyncio
import logging
from datetime import datetime

from agents.base_agent import SubsystemID, Mode
from agents.interpreter_agent import InterpreterAgent
from agents.strategist_agent import StrategistAgent
from agents.artisan_agent import ArtisanAgent
from agents.ledger_agent import LedgerAgent
from agents.sentinel_agent import SentinelAgent
from agents.executor_agent import ExecutorAgent
from agents.mirror_agent import MirrorAgent


class Chorus:
    """
    Parliamentary intelligence orchestrator.
    Coordinates all 7 agents with constitutional compliance.
    """
    
    def __init__(
        self,
        constitution_path: str = "core/constitution.json",
        redis_url: str = "redis://localhost:6379",
        postgres_dsn: str = "postgresql://zazu:zazu_dev_password@localhost:5432/zazu_memory"
    ):
        self.constitution_path = constitution_path
        self.redis_url = redis_url
        self.postgres_dsn = postgres_dsn
        
        self.logger = logging.getLogger("zazu.chorus")
        
        # Agent registry
        self.agents: Dict[str, Any] = {}
        self.initialized = False
    
    async def initialize(self):
        """Initialize all 7 agents"""
        if self.initialized:
            self.logger.warning("Chorus already initialized")
            return
        
        self.logger.info("Initializing Zazu Parliament (7 agents)...")
        
        # Create all agents
        agent_classes = {
            'interpreter': InterpreterAgent,
            'strategist': StrategistAgent,
            'artisan': ArtisanAgent,
            'ledger': LedgerAgent,
            'sentinel': SentinelAgent,
            'executor': ExecutorAgent,
            'mirror': MirrorAgent
        }
        
        # Initialize each agent
        for subsystem_id, agent_class in agent_classes.items():
            try:
                self.logger.info(f"Initializing {subsystem_id}...")
                agent = agent_class(
                    constitution_path=self.constitution_path,
                    redis_url=self.redis_url,
                    postgres_dsn=self.postgres_dsn
                )
                await agent.initialize()
                self.agents[subsystem_id] = agent
                self.logger.info(f"✓ {subsystem_id} ready")
            except Exception as e:
                self.logger.error(f"Failed to initialize {subsystem_id}: {e}")
                raise
        
        self.initialized = True
        self.logger.info("🎉 Parliament initialized - all 7 agents ready")
    
    async def process_request(
        self,
        user_input: str,
        mode: str = "auto",
        context: Optional[Dict[str, Any]] = None,
        require_consensus: bool = False
    ) -> Dict[str, Any]:
        """
        Main entry point for user requests.
        
        Args:
            user_input: Raw user request
            mode: "inquiry", "creation", "execution", or "auto" (detect)
            context: Optional context from previous interactions
            require_consensus: If True, get multi-agent consensus
        
        Returns:
            Aggregated response from parliament
        """
        if not self.initialized:
            raise RuntimeError("Chorus not initialized. Call initialize() first.")
        
        context = context or {}
        
        self.logger.info(f"Processing request: {user_input[:50]}...")
        
        # Step 1: Detect mode (if auto)
        if mode == "auto":
            mode = await self._detect_mode(user_input)
            self.logger.info(f"Auto-detected mode: {mode}")
        
        # Step 2: Route and execute based on mode
        result = await self._route_and_execute(user_input, mode, context, require_consensus)
        
        # Step 3: Always get Mirror reflection
        reflection = await self._get_reflection(result, context)
        result['reflection'] = reflection
        
        return result
    
    async def _detect_mode(self, user_input: str) -> str:
        """Auto-detect mode from user input"""
        user_input_lower = user_input.lower()
        
        # Check for execution keywords
        execution_keywords = ['run', 'execute', 'do', 'perform', 'deploy', 'start', 'create file', 'delete']
        if any(kw in user_input_lower for kw in execution_keywords):
            return Mode.EXECUTION.value
        
        # Check for creation keywords
        creation_keywords = ['plan', 'design', 'create', 'build', 'generate', 'write', 'compose', 'mythos', 'worldbuild']
        if any(kw in user_input_lower for kw in creation_keywords):
            return Mode.CREATION.value
        
        # Default to inquiry
        return Mode.INQUIRY.value
    
    async def _route_and_execute(
        self,
        user_input: str,
        mode: str,
        context: Dict[str, Any],
        require_consensus: bool
    ) -> Dict[str, Any]:
        """Route request to appropriate agents based on mode"""
        
        # Always start with Interpreter to parse intent
        interpreter_result = await self.agents['interpreter'].process({
            'user_input': user_input,
            'context': context
        })
        
        routing = interpreter_result['routing']
        target_subsystem = routing['target_subsystem']
        
        self.logger.info(f"Interpreter routed to: {target_subsystem}")
        
        result = {
            'mode_used': mode,
            'interpreter_analysis': interpreter_result,
            'agents_involved': ['interpreter'],
            'outputs': {}
        }
        
        # Route based on detected subsystem and mode
        if mode == Mode.INQUIRY.value:
            # Simple query - just return interpreter result
            result['outputs']['interpreter'] = interpreter_result
            
        elif mode == Mode.CREATION.value:
            # Creation mode - involve Strategist, Artisan, and possibly Ledger
            
            # Get strategic plan
            if target_subsystem in ['strategist', 'interpreter']:  # Default to strategist for planning
                strategist_result = await self.agents['strategist'].process({
                    'goal': user_input,
                    'constraints': [],
                    'time_horizon': 'immediate',
                    'context': context
                })
                result['outputs']['strategist'] = strategist_result
                result['agents_involved'].append('strategist')
            
            # Get creative content if needed
            if 'mythos' in user_input.lower() or 'worldbuild' in user_input.lower() or target_subsystem == 'artisan':
                artisan_result = await self.agents['artisan'].process({
                    'creative_type': 'mythos' if 'mythos' in user_input.lower() else 'worldbuilding',
                    'theme': 'sovereignty',  # Default theme
                    'constraints': {},
                    'context': context
                })
                result['outputs']['artisan'] = artisan_result
                result['agents_involved'].append('artisan')
            
            # Get risk assessment
            if require_consensus or 'risk' in user_input.lower():
                ledger_result = await self.agents['ledger'].process({
                    'analysis_type': 'risk',
                    'data': {
                        'complexity': 5,
                        'uncertainty': 0.5,
                        'dependencies': [],
                        'timeline_days': 30
                    },
                    'parameters': {}
                })
                result['outputs']['ledger'] = ledger_result
                result['agents_involved'].append('ledger')
        
        elif mode == Mode.EXECUTION.value:
            # Execution mode - involve Executor with Sentinel approval
            
            # Prepare execution task
            task = {
                'type': 'command',  # Simplified for demo
                'parameters': {
                    'command': 'echo "Demo execution"',
                    'cwd': '/tmp'
                }
            }
            
            # Execute (Executor will check with Sentinel internally)
            executor_result = await self.agents['executor'].process({
                'task': task,
                'skip_approval': False  # Require Sentinel approval
            })
            result['outputs']['executor'] = executor_result
            result['agents_involved'].extend(['executor', 'sentinel'])
        
        # If consensus required, aggregate multiple perspectives
        if require_consensus:
            consensus = await self._get_consensus(user_input, result)
            result['consensus'] = consensus
        
        return result
    
    async def _get_consensus(
        self,
        question: str,
        current_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get consensus from multiple agents.
        For MVP: Simple majority from 2-3 agents
        """
        # Collect perspectives from agents that haven't responded yet
        perspectives = []
        
        # If Strategist hasn't been consulted, get their view
        if 'strategist' not in current_result['agents_involved']:
            strategist_view = await self.agents['strategist'].process({
                'goal': question,
                'constraints': [],
                'time_horizon': 'immediate',
                'context': {}
            })
            perspectives.append({
                'agent': 'strategist',
                'view': strategist_view
            })
        
        # If Ledger hasn't been consulted, get risk view
        if 'ledger' not in current_result['agents_involved']:
            ledger_view = await self.agents['ledger'].process({
                'analysis_type': 'risk',
                'data': {'complexity': 5, 'uncertainty': 0.5},
                'parameters': {}
            })
            perspectives.append({
                'agent': 'ledger',
                'score': ledger_view['analysis']['risk_score']
            })
        
        # Calculate consensus score (simplified: average agreement)
        if perspectives:
            # For demo: Just return that consensus was reached
            consensus_score = 0.75  # Placeholder
        else:
            consensus_score = 1.0  # All agents already consulted
        
        return {
            'consensus_score': consensus_score,
            'additional_perspectives': perspectives,
            'threshold_met': consensus_score >= 0.66
        }
    
    async def _get_reflection(
        self,
        result: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get Mirror's reflection on the overall interaction"""
        
        # Prepare event for Mirror
        event = {
            'type': 'decision',
            'subsystem': 'chorus',
            'description': f"Coordinated {len(result['agents_involved'])} agents in {result['mode_used']} mode",
            'outcome': {
                'agents_involved': result['agents_involved'],
                'outputs_count': len(result.get('outputs', {}))
            }
        }
        
        mirror_result = await self.agents['mirror'].process({
            'event': event,
            'context': context
        })
        
        return mirror_result['reflection']
    
    async def shutdown(self):
        """Gracefully shutdown all agents"""
        if not self.initialized:
            return
        
        self.logger.info("Shutting down parliament...")
        
        for subsystem_id, agent in self.agents.items():
            try:
                await agent.shutdown()
                self.logger.info(f"✓ {subsystem_id} shutdown")
            except Exception as e:
                self.logger.error(f"Error shutting down {subsystem_id}: {e}")
        
        self.agents.clear()
        self.initialized = False
        self.logger.info("Parliament shutdown complete")
    
    def get_agent_status(self) -> Dict[str, bool]:
        """Get status of all agents"""
        return {
            subsystem_id: agent.active if hasattr(agent, 'active') else True
            for subsystem_id, agent in self.agents.items()
        }


# Convenience function for simple usage
async def ask_parliament(question: str, mode: str = "auto") -> Dict[str, Any]:
    """
    Simplified interface for one-off questions to the parliament.
    
    Usage:
        result = await ask_parliament("What is my mission?")
        result = await ask_parliament("Create a mythos about transformation", mode="creation")
    """
    chorus = Chorus()
    await chorus.initialize()
    
    try:
        result = await chorus.process_request(question, mode=mode)
        return result
    finally:
        await chorus.shutdown()
