"""
Strategist Agent - Temporal Foresight Layer
Constitutional constraint: NO EXECUTION AUTHORITY
"""

from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent, SubsystemID, Mode
from datetime import datetime, timedelta
import json


class StrategistAgent(BaseAgent):
    """
    Temporal foresight and scenario modeling subsystem.
    
    Constitutional Constraints:
    - Can MODEL scenarios and PLAN long-horizon strategies
    - Cannot EXECUTE actions
    - Cannot TOUCH real systems
    - Cannot COMMIT resources
    - Cannot OVERRIDE Ledger's risk assessments
    """
    
    def __init__(self, **kwargs):
        super().__init__(subsystem_id=SubsystemID.STRATEGIST, **kwargs)
        
        # Time horizons for planning
        self.horizons = {
            'immediate': timedelta(days=7),
            'seasonal': timedelta(days=90),
            'epochal': timedelta(days=365)
        }
    
    async def _process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate strategic plans and scenario models.
        
        Input schema:
        {
            "goal": str,
            "constraints": [],
            "time_horizon": "immediate|seasonal|epochal",
            "context": {}
        }
        
        Output schema:
        {
            "strategy": {
                "primary_approach": str,
                "alternative_approaches": [],
                "decision_tree": {},
                "timeline": [],
                "dependencies": [],
                "risk_factors": []
            },
            "scenarios": [
                {
                    "name": str,
                    "probability": float,
                    "outcomes": {},
                    "mitigation": str
                }
            ]
        }
        """
        goal = input_data['goal']
        constraints = input_data.get('constraints', [])
        time_horizon = input_data.get('time_horizon', 'immediate')
        context = input_data.get('context', {})
        
        # Step 1: Scenario modeling
        scenarios = await self._model_scenarios(goal, time_horizon, context)
        
        # Step 2: Decision tree generation
        decision_tree = await self._generate_decision_tree(goal, scenarios, constraints)
        
        # Step 3: Timeline planning
        timeline = await self._plan_timeline(goal, time_horizon, decision_tree)
        
        # Step 4: Constraint mapping
        constraint_map = await self._map_constraints(goal, constraints, decision_tree)
        
        # Step 5: Risk factor identification (coordinate with Ledger)
        risk_factors = await self._identify_risk_factors(scenarios, decision_tree)
        
        # Log to episodic memory
        await self.write_episodic(
            event_type="strategy_generated",
            context={
                'goal': goal,
                'time_horizon': time_horizon,
                'scenarios_count': len(scenarios),
                'decision_tree_depth': self._tree_depth(decision_tree)
            }
        )
        
        return {
            'strategy': {
                'primary_approach': decision_tree.get('root', {}).get('action', ''),
                'alternative_approaches': [s['name'] for s in scenarios[1:3]],  # Top alternatives
                'decision_tree': decision_tree,
                'timeline': timeline,
                'dependencies': constraint_map.get('dependencies', []),
                'risk_factors': risk_factors
            },
            'scenarios': scenarios
        }
    
    async def _model_scenarios(
        self,
        goal: str,
        time_horizon: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple scenario models with probability estimates.
        For MVP: Rule-based. Can enhance with ML in Phase 2C.
        """
        scenarios = []
        
        # Base scenario (optimistic)
        scenarios.append({
            'name': 'Optimal Path',
            'probability': 0.3,
            'outcomes': {
                'success': 'high',
                'timeline': f'Within {time_horizon} horizon',
                'resource_cost': 'moderate'
            },
            'mitigation': 'Maintain current trajectory, monitor for deviations'
        })
        
        # Conservative scenario
        scenarios.append({
            'name': 'Conservative Approach',
            'probability': 0.5,
            'outcomes': {
                'success': 'moderate',
                'timeline': f'Extended beyond {time_horizon}',
                'resource_cost': 'low'
            },
            'mitigation': 'Reduce scope, focus on core deliverables'
        })
        
        # High-risk scenario
        scenarios.append({
            'name': 'Aggressive Timeline',
            'probability': 0.2,
            'outcomes': {
                'success': 'variable',
                'timeline': f'Compressed within {time_horizon}',
                'resource_cost': 'high'
            },
            'mitigation': 'Parallel workstreams, accept higher risk'
        })
        
        return scenarios
    
    async def _generate_decision_tree(
        self,
        goal: str,
        scenarios: List[Dict[str, Any]],
        constraints: List[str]
    ) -> Dict[str, Any]:
        """
        Build decision tree mapping choices to outcomes.
        """
        # Simple tree structure for MVP
        tree = {
            'root': {
                'decision': f'Approach for: {goal}',
                'action': scenarios[0]['name'],  # Primary
                'branches': []
            }
        }
        
        # Add scenario branches
        for i, scenario in enumerate(scenarios):
            branch = {
                'condition': f'Probability: {scenario["probability"]}',
                'action': scenario['name'],
                'expected_outcome': scenario['outcomes'],
                'next_decision': 'Monitor and adjust' if i == 0 else 'Evaluate alternatives'
            }
            tree['root']['branches'].append(branch)
        
        # Add constraint checks
        if constraints:
            tree['root']['constraint_gates'] = constraints
        
        return tree
    
    async def _plan_timeline(
        self,
        goal: str,
        time_horizon: str,
        decision_tree: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate phased timeline based on time horizon.
        """
        horizon_days = self.horizons.get(time_horizon, timedelta(days=30)).days
        
        # Divide into phases
        phases = []
        
        # Phase 1: Planning (10% of timeline)
        phases.append({
            'phase': 'Planning & Requirements',
            'duration_days': int(horizon_days * 0.1),
            'deliverables': ['Detailed plan', 'Resource allocation', 'Risk assessment'],
            'start_offset_days': 0
        })
        
        # Phase 2: Execution (60% of timeline)
        phases.append({
            'phase': 'Core Execution',
            'duration_days': int(horizon_days * 0.6),
            'deliverables': ['Incremental progress', 'Milestone checkpoints'],
            'start_offset_days': int(horizon_days * 0.1)
        })
        
        # Phase 3: Validation (20% of timeline)
        phases.append({
            'phase': 'Validation & Testing',
            'duration_days': int(horizon_days * 0.2),
            'deliverables': ['Quality verification', 'Integration testing'],
            'start_offset_days': int(horizon_days * 0.7)
        })
        
        # Phase 4: Deployment (10% of timeline)
        phases.append({
            'phase': 'Deployment & Monitoring',
            'duration_days': int(horizon_days * 0.1),
            'deliverables': ['Production deployment', 'Post-deployment monitoring'],
            'start_offset_days': int(horizon_days * 0.9)
        })
        
        return phases
    
    async def _map_constraints(
        self,
        goal: str,
        constraints: List[str],
        decision_tree: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Map constraints to decision points.
        """
        constraint_map = {
            'hard_constraints': [],
            'soft_constraints': [],
            'dependencies': []
        }
        
        for constraint in constraints:
            constraint_lower = constraint.lower()
            
            # Categorize constraints
            if any(kw in constraint_lower for kw in ['must', 'required', 'cannot']):
                constraint_map['hard_constraints'].append(constraint)
            else:
                constraint_map['soft_constraints'].append(constraint)
            
            # Identify dependencies
            if 'depends on' in constraint_lower or 'requires' in constraint_lower:
                constraint_map['dependencies'].append(constraint)
        
        return constraint_map
    
    async def _identify_risk_factors(
        self,
        scenarios: List[Dict[str, Any]],
        decision_tree: Dict[str, Any]
    ) -> List[str]:
        """
        Identify potential risk factors across scenarios.
        """
        risk_factors = []
        
        # Analyze scenario probabilities
        low_prob_scenarios = [s for s in scenarios if s['probability'] < 0.3]
        if low_prob_scenarios:
            risk_factors.append(
                f"Low probability of optimal outcome ({low_prob_scenarios[0]['probability']:.0%})"
            )
        
        # Check for high resource costs
        high_cost_scenarios = [
            s for s in scenarios 
            if s['outcomes'].get('resource_cost') == 'high'
        ]
        if high_cost_scenarios:
            risk_factors.append("High resource cost in some scenarios")
        
        # Check for timeline compression
        compressed_timelines = [
            s for s in scenarios
            if 'Compressed' in s['outcomes'].get('timeline', '')
        ]
        if compressed_timelines:
            risk_factors.append("Timeline compression may impact quality")
        
        return risk_factors
    
    def _tree_depth(self, tree: Dict[str, Any], current_depth: int = 0) -> int:
        """Calculate decision tree depth"""
        if 'branches' not in tree.get('root', {}):
            return current_depth
        
        branches = tree['root']['branches']
        if not branches:
            return current_depth
        
        return current_depth + 1
    
    def _check_constraints(self, proposed_output: Dict[str, Any]) -> bool:
        """
        Verify Strategist doesn't violate constitutional constraints.
        """
        strategy = proposed_output.get('strategy', {})
        
        # Strategist should never:
        # - Execute actions (no_execution_authority)
        # - Touch real systems (cannot_touch_real_systems)
        # - Commit resources (cannot_commit_resources)
        
        # Check for execution commands in strategy
        execution_keywords = ['execute', 'deploy', 'run', 'commit', 'allocate']
        
        primary_approach = strategy.get('primary_approach', '').lower()
        for keyword in execution_keywords:
            if keyword in primary_approach:
                self.logger.warning(
                    f"Strategy contains execution keyword: {keyword}. "
                    "Strategist can plan but not execute."
                )
                # Allow but log warning - planning language may include these terms
        
        return True
