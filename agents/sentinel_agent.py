"""
Sentinel Agent - Safety & Ethical Adjudicator
Constitutional constraint: NEGATIVE AUTHORITY ONLY
"""

from typing import Dict, Any, List
from agents.base_agent import BaseAgent, SubsystemID, Mode
import json


class SentinelAgent(BaseAgent):
    """
    The guardian subsystem with veto power but no creative authority.
    Enforces the Seven Laws of Moral Physics.
    
    Constitutional Constraints:
    - Can HALT execution
    - Cannot CREATE, REVISE, or PROPOSE alternatives
    - Jurisdiction is threshold-activated (pre-execution/publication only)
    - Subject to anti-paralysis calibration
    """
    
    def __init__(self, **kwargs):
        super().__init__(subsystem_id=SubsystemID.SENTINEL, **kwargs)
        
        # Load halt protocol config
        halt_config = self.constitution['operational_constraints']['halt_repair_loop']
        self.max_repair_cycles = halt_config['max_repair_cycles']
        
        anti_paralysis = self.constitution['operational_constraints']['anti_paralysis']
        self.halt_threshold = anti_paralysis['halt_threshold']
        self.measurement_window = int(anti_paralysis['measurement_window'].replace('last_', '').replace('_decisions', ''))
        
        # Runtime state
        self.recent_decisions: List[Dict] = []
        self.current_repair_cycle = 0
    
    async def _process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate artifact for constitutional compliance.
        
        Input schema:
        {
            "artifact": {...},
            "subsystem_origin": "strategist|artisan|executor|...",
            "action_type": "execution|publication|financial|...",
            "context": {...}
        }
        
        Output schema:
        {
            "decision": "approve|halt",
            "halt_reason": "..." (if halted),
            "fault_code": "..." (if halted),
            "repair_cycle": int
        }
        """
        artifact = input_data['artifact']
        subsystem_origin = input_data['subsystem_origin']
        action_type = input_data['action_type']
        context = input_data.get('context', {})
        
        # Check if this is within jurisdiction (threshold-activated)
        if not self._is_threshold_action(action_type):
            return {
                'decision': 'approve',
                'reason': 'not_threshold_action'
            }
        
        # Moral regression testing (Law 5)
        moral_check = await self._moral_regression_test(artifact, context)
        if not moral_check['passed']:
            return await self._issue_halt(
                reason=moral_check['reason'],
                fault_code=moral_check['fault_code'],
                context=context
            )
        
        # Ethical boundary check (Laws 1, 2)
        ethical_check = await self._ethical_boundary_check(artifact, context)
        if not ethical_check['passed']:
            return await self._issue_halt(
                reason=ethical_check['reason'],
                fault_code=ethical_check['fault_code'],
                context=context
            )
        
        # Legal constraint validation
        legal_check = await self._legal_constraint_check(artifact, action_type)
        if not legal_check['passed']:
            return await self._issue_halt(
                reason=legal_check['reason'],
                fault_code=legal_check['fault_code'],
                context=context
            )
        
        # Subsystem-specific constraint check
        subsystem_check = await self._subsystem_constraint_check(
            artifact,
            subsystem_origin
        )
        if not subsystem_check['passed']:
            return await self._issue_halt(
                reason=subsystem_check['reason'],
                fault_code=subsystem_check['fault_code'],
                context=context
            )
        
        # All checks passed
        decision = {
            'decision': 'approve',
            'timestamp': str(datetime.utcnow())
        }
        
        self.recent_decisions.append(decision)
        await self._check_anti_paralysis()
        
        return decision
    
    def _is_threshold_action(self, action_type: str) -> bool:
        """
        Check if action crosses threshold requiring Sentinel review.
        Non-threshold actions bypass Sentinel (protected dreamspace).
        """
        thresholds = self.constitution['axioms']['permissive_until_dangerous']['restriction_thresholds']
        return action_type in thresholds
    
    async def _moral_regression_test(
        self,
        artifact: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Law 5: Check if artifact increases/decreases user long-arc coherence
        and whether it crosses harm/legality/irreversibility boundaries.
        """
        checks = self.constitution['moral_physics']['moral_regression_testing']['pre_execution_checks']
        
        # Check 1: Long-arc coherence
        coherence_check = checks[0]
        for halt_condition in coherence_check['halt_conditions']:
            # In production, this would use Mirror's coherence tracking
            # For now, keyword-based heuristic
            if await self._detect_coherence_violation(artifact, halt_condition):
                return {
                    'passed': False,
                    'reason': f"Violates long-arc coherence: {halt_condition}",
                    'fault_code': 'coherence_violation'
                }
        
        # Check 2: Harm/legality/irreversibility
        boundary_check = checks[1]
        for halt_condition in boundary_check['halt_conditions']:
            if await self._detect_boundary_violation(artifact, halt_condition):
                return {
                    'passed': False,
                    'reason': f"Crosses boundary: {halt_condition}",
                    'fault_code': 'boundary_violation'
                }
        
        return {'passed': True}
    
    async def _ethical_boundary_check(
        self,
        artifact: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Laws 1 & 2: Dual anchoring + permissive-until-dangerous.
        Check protection of user arc and external world safeguards.
        """
        dual_anchoring = self.constitution['moral_physics']['dual_anchoring']
        
        # User arc protection
        user_arc_violations = dual_anchoring['protection_of_user_arc']
        for violation_pattern in user_arc_violations:
            if await self._pattern_match(artifact, violation_pattern):
                return {
                    'passed': False,
                    'reason': f"Violates user arc protection: {violation_pattern}",
                    'fault_code': 'user_arc_violation'
                }
        
        # External world safeguards
        external_violations = dual_anchoring['safeguarding_external_world']
        for violation_pattern in external_violations:
            if await self._pattern_match(artifact, violation_pattern):
                return {
                    'passed': False,
                    'reason': f"Violates external safeguards: {violation_pattern}",
                    'fault_code': 'external_harm'
                }
        
        return {'passed': True}
    
    async def _legal_constraint_check(
        self,
        artifact: Dict[str, Any],
        action_type: str
    ) -> Dict[str, Any]:
        """
        Check for legal constraint violations (criminal activity, fraud, etc.)
        """
        # Keyword-based heuristics for demo
        # In production: integrated legal compliance API
        prohibited_keywords = [
            'illegal', 'fraud', 'laundering', 'hack', 'exploit',
            'steal', 'insider trading', 'manipulation'
        ]
        
        artifact_text = json.dumps(artifact).lower()
        for keyword in prohibited_keywords:
            if keyword in artifact_text:
                return {
                    'passed': False,
                    'reason': f"Potential legal violation detected: {keyword}",
                    'fault_code': 'legal_violation'
                }
        
        return {'passed': True}
    
    async def _subsystem_constraint_check(
        self,
        artifact: Dict[str, Any],
        subsystem_origin: str
    ) -> Dict[str, Any]:
        """
        Verify that originating subsystem didn't violate its own constraints.
        E.g., Artisan attempting planning, Strategist attempting execution.
        """
        if subsystem_origin not in self.constitution['subsystems']:
            return {'passed': True}
        
        origin_config = self.constitution['subsystems'][subsystem_origin]
        constraints = origin_config['constraints']
        
        # Check constraints (keyword matching for demo)
        # In production: structured validation against API contracts
        for constraint in constraints:
            if 'cannot_execute' in constraint and 'execute_command' in artifact:
                return {
                    'passed': False,
                    'reason': f"{subsystem_origin} violated constraint: {constraint}",
                    'fault_code': 'subsystem_constraint_violation'
                }
        
        return {'passed': True}
    
    async def _issue_halt(
        self,
        reason: str,
        fault_code: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Issue halt decision and log to halt_events table.
        Initiates bounded repair loop.
        """
        self.current_repair_cycle += 1
        
        # Log halt event
        async with self.postgres.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO halt_events 
                (halted_subsystem, halt_reason, repair_cycle_count)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (
                    context.get('subsystem_origin', 'unknown'),
                    reason,
                    self.current_repair_cycle
                )
            )
            halt_event_id = (await cur.fetchone())[0]
            await self.postgres.commit()
        
        # Check if max repair cycles exceeded
        if self.current_repair_cycle >= self.max_repair_cycles:
            await self.log_reflective(
                log_type="escalation",
                message=f"Max repair cycles ({self.max_repair_cycles}) exceeded. Escalating to user.",
                metadata={'halt_event_id': halt_event_id, 'fault_code': fault_code}
            )
            
            return {
                'decision': 'escalate',
                'halt_reason': reason,
                'fault_code': fault_code,
                'repair_cycle': self.current_repair_cycle,
                'escalation_target': 'user_via_mirror',
                'halt_event_id': halt_event_id
            }
        
        decision = {
            'decision': 'halt',
            'halt_reason': reason,
            'fault_code': fault_code,
            'repair_cycle': self.current_repair_cycle,
            'halt_event_id': halt_event_id
        }
        
        self.recent_decisions.append(decision)
        await self._check_anti_paralysis()
        
        return decision
    
    async def _check_anti_paralysis(self):
        """
        Anti-paralysis rule: monitor halt rate and trigger calibration if threshold exceeded.
        """
        if len(self.recent_decisions) < 10:  # Need minimum sample
            return
        
        # Keep only recent decisions within measurement window
        self.recent_decisions = self.recent_decisions[-self.measurement_window:]
        
        halt_count = sum(1 for d in self.recent_decisions if d['decision'] in ['halt', 'escalate'])
        halt_rate = halt_count / len(self.recent_decisions)
        
        if halt_rate > self.halt_threshold:
            await self.log_reflective(
                log_type="anti_paralysis_trigger",
                message=f"Halt rate ({halt_rate:.2f}) exceeds threshold ({self.halt_threshold})",
                metadata={
                    'halt_count': halt_count,
                    'total_decisions': len(self.recent_decisions),
                    'halt_rate': halt_rate
                }
            )
            
            # Trigger calibration workflow
            await self.publish(
                channel="system:calibration",
                message={
                    'trigger': 'anti_paralysis',
                    'subsystem': 'sentinel',
                    'halt_rate': halt_rate,
                    'threshold': self.halt_threshold
                }
            )
    
    async def _detect_coherence_violation(
        self,
        artifact: Dict[str, Any],
        halt_condition: str
    ) -> bool:
        """Detect long-arc coherence violations (placeholder for Mirror integration)"""
        # In production: query Mission Memory and Mirror's coherence tracker
        return False  # Conservative default
    
    async def _detect_boundary_violation(
        self,
        artifact: Dict[str, Any],
        halt_condition: str
    ) -> bool:
        """Detect harm/legality/irreversibility boundary violations"""
        # Keyword-based heuristic for demo
        violation_keywords = {
            'crosses_harm_boundary': ['harm', 'damage', 'hurt', 'destroy'],
            'violates_legality': ['illegal', 'unlawful', 'fraud'],
            'creates_irreversible_action': ['delete', 'irreversible', 'permanent']
        }
        
        keywords = violation_keywords.get(halt_condition, [])
        artifact_text = json.dumps(artifact).lower()
        
        return any(kw in artifact_text for kw in keywords)
    
    async def _pattern_match(
        self,
        artifact: Dict[str, Any],
        pattern: str
    ) -> bool:
        """Pattern matching for ethical violations (placeholder)"""
        # In production: ML-based pattern recognition or rule engine
        artifact_text = json.dumps(artifact).lower()
        pattern_keywords = pattern.replace('_', ' ').lower()
        return pattern_keywords in artifact_text


# Import datetime
from datetime import datetime
