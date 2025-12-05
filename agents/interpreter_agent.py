"""
Interpreter Agent - Semantic Spine
Constitutional constraint: CANNOT CREATE, EXECUTE, OR ASSESS RISK
"""

from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent, SubsystemID, Mode
import re


class InterpreterAgent(BaseAgent):
    """
    The semantic spine for intent clarification and routing.
    
    Constitutional Constraints:
    - Can PARSE semantics and ROUTE to subsystems
    - Cannot GENERATE strategy
    - Cannot CREATE artifacts
    - Cannot EXECUTE actions
    - Cannot ASSESS risk
    """
    
    def __init__(self, **kwargs):
        super().__init__(subsystem_id=SubsystemID.INTERPRETER, **kwargs)
        
        # Intent classification patterns (keyword-based for MVP)
        self.intent_patterns = {
            'query': [
                r'\b(what|how|why|when|where|who|explain|tell|show)\b',
                r'\b(status|current|mission|progress|check)\b'
            ],
            'create': [
                r'\b(create|build|make|generate|design|write)\b',
                r'\b(new|develop|craft|compose)\b'
            ],
            'execute': [
                r'\b(run|execute|do|perform|start|deploy)\b',
                r'\b(action|task|command)\b'
            ],
            'reflect': [
                r'\b(reflect|review|assess|evaluate|analyze)\b',
                r'\b(coherence|alignment|progress)\b'
            ],
            'plan': [
                r'\b(plan|strategy|roadmap|approach|steps)\b',
                r'\b(scenario|timeline|forecast)\b'
            ]
        }
        
        # Subsystem routing rules
        self.routing_rules = {
            'query': {
                'default': SubsystemID.INTERPRETER.value,
                'mission': SubsystemID.MIRROR.value,
                'risk': SubsystemID.LEDGER.value
            },
            'create': {
                'narrative': SubsystemID.ARTISAN.value,
                'mythos': SubsystemID.ARTISAN.value,
                'default': SubsystemID.STRATEGIST.value
            },
            'execute': {
                'default': SubsystemID.EXECUTOR.value
            },
            'reflect': {
                'default': SubsystemID.MIRROR.value
            },
            'plan': {
                'default': SubsystemID.STRATEGIST.value
            }
        }
    
    async def _process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse user input and route to appropriate subsystem.
        
        Input schema:
        {
            "user_input": str,
            "context": {
                "previous_inputs": [],
                "current_mode": "inquiry|creation|execution"
            }
        }
        
        Output schema:
        {
            "intent": {
                "primary_goal": str,
                "action_type": str,
                "ambiguities": [],
                "requires_clarification": bool
            },
            "routing": {
                "target_subsystem": str,
                "suggested_mode": str,
                "confidence": float
            }
        }
        """
        user_input = input_data['user_input']
        context = input_data.get('context', {})
        
        # Step 1: Semantic parsing
        intent = await self._semantic_parse(user_input, context)
        
        # Step 2: Ambiguity detection
        ambiguities = await self._detect_ambiguity(user_input, intent)
        intent['ambiguities'] = ambiguities
        intent['requires_clarification'] = len(ambiguities) > 0
        
        # Step 3: Routing logic
        routing = await self._route_to_subsystem(intent, context)
        
        # Log to episodic memory
        await self.write_episodic(
            event_type="intent_parsed",
            context={
                'user_input': user_input,
                'intent': intent,
                'routing': routing
            }
        )
        
        return {
            'intent': intent,
            'routing': routing
        }
    
    async def _semantic_parse(
        self,
        user_input: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract intent from user input using pattern matching.
        In production, this could be enhanced with LLM-based parsing.
        """
        user_input_lower = user_input.lower()
        
        # Classify action type
        action_type = 'query'  # Default
        max_matches = 0
        
        for intent_type, patterns in self.intent_patterns.items():
            match_count = sum(
                1 for pattern in patterns
                if re.search(pattern, user_input_lower)
            )
            if match_count > max_matches:
                max_matches = match_count
                action_type = intent_type
        
        # Extract primary goal (simplified: first sentence)
        primary_goal = user_input.split('.')[0].strip()
        
        return {
            'primary_goal': primary_goal,
            'action_type': action_type,
            'original_input': user_input
        }
    
    async def _detect_ambiguity(
        self,
        user_input: str,
        intent: Dict[str, Any]
    ) -> List[str]:
        """
        Detect ambiguities in user input that require clarification.
        """
        ambiguities = []
        
        # Check for vague pronouns without context
        vague_pronouns = ['it', 'that', 'this', 'those', 'them']
        for pronoun in vague_pronouns:
            if re.search(rf'\b{pronoun}\b', user_input.lower()):
                # Check if there's clear antecedent context
                # For MVP, flag all pronouns as potentially ambiguous
                ambiguities.append(f"Unclear reference: '{pronoun}'")
        
        # Check for missing parameters for execution actions
        if intent['action_type'] == 'execute':
            # Look for common execution keywords without clear targets
            if not any(kw in user_input.lower() for kw in ['file', 'api', 'command', 'task']):
                ambiguities.append("Execution target not specified")
        
        # Check for contradictory keywords
        if 'create' in user_input.lower() and 'delete' in user_input.lower():
            ambiguities.append("Contradictory actions detected (create vs delete)")
        
        return ambiguities
    
    async def _route_to_subsystem(
        self,
        intent: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Map intent to appropriate subsystem and suggest mode.
        """
        action_type = intent['action_type']
        original_input = intent['original_input'].lower()
        
        # Get routing rules for this action type
        rules = self.routing_rules.get(action_type, {'default': SubsystemID.INTERPRETER.value})
        
        # Check for specialized routing
        target_subsystem = rules['default']
        for keyword, subsystem in rules.items():
            if keyword != 'default' and keyword in original_input:
                target_subsystem = subsystem
                break
        
        # Suggest mode based on action type
        mode_mapping = {
            'query': Mode.INQUIRY.value,
            'reflect': Mode.INQUIRY.value,
            'create': Mode.CREATION.value,
            'plan': Mode.CREATION.value,
            'execute': Mode.EXECUTION.value
        }
        suggested_mode = mode_mapping.get(action_type, Mode.INQUIRY.value)
        
        # Calculate confidence (simple heuristic)
        confidence = 0.8  # Default
        if intent.get('ambiguities'):
            confidence = 0.5  # Lower confidence if ambiguous
        
        return {
            'target_subsystem': target_subsystem,
            'suggested_mode': suggested_mode,
            'confidence': confidence
        }
    
    def _check_constraints(self, proposed_output: Dict[str, Any]) -> bool:
        """
        Verify Interpreter doesn't violate constitutional constraints.
        """
        # Interpreter should never output:
        # - Strategy artifacts (cannot_generate_strategy)
        # - Created content (cannot_create_artifacts)
        # - Execution commands (cannot_execute_actions)
        # - Risk assessments (cannot_assess_risk)
        
        routing = proposed_output.get('routing', {})
        
        # Interpreter should not route to itself for execution
        if routing.get('target_subsystem') == SubsystemID.INTERPRETER.value:
            action_type = proposed_output.get('intent', {}).get('action_type')
            if action_type in ['execute', 'create']:
                self.logger.error(
                    "Constraint violation: Interpreter attempted to handle execution/creation"
                )
                return False
        
        return True
