"""
Mirror Agent - Self-Model & Recovery Context
Constitutional constraint: CONTEXT NOT COMMANDS
"""

from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent, SubsystemID, Mode
from datetime import datetime, timedelta


class MirrorAgent(BaseAgent):
    """
    Self-model and coherence tracker for reflective intelligence.
    
    Constitutional Constraints:
    - Can REFLECT on progress and alignment
    - Cannot INTERFERE with trading or lore creation
    - Provides CONTEXT not COMMANDS
    - Cannot simulate therapy
    """
    
    def __init__(self, **kwargs):
        super().__init__(subsystem_id=SubsystemID.MIRROR, **kwargs)
        
        # Emotional load keywords (heuristic-based for MVP)
        self.high_load_keywords = [
            'stress', 'anxious', 'overwhelmed', 'frustrated', 'exhausted',
            'burnout', 'panic', 'despair', 'fear', 'rage'
        ]
        self.low_load_keywords = [
            'calm', 'focused', 'clear', 'energized', 'confident',
            'peaceful', 'balanced', 'grounded', 'steady'
        ]
    
    async def _process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reflect on events and assess coherence.
        
        Input schema:
        {
            "event": {
                "type": "decision|action|reflection",
                "subsystem": str,
                "description": str,
                "outcome": {}
            },
            "context": {
                "current_mission": str (optional),
                "time_horizon": "immediate|seasonal|epochal"
            }
        }
        
        Output schema:
        {
            "reflection": {
                "coherence_score": float,
                "emotional_load_estimate": "low|medium|high",
                "progress_assessment": str,
                "philosophical_alignment": bool
            },
            "recommendations": []
        }
        """
        event = input_data['event']
        context = input_data.get('context', {})
        
        # Step 1: Calculate coherence with mission
        coherence_score = await self._calculate_coherence(event, context)
        
        # Step 2: Detect emotional load
        emotional_load = await self._detect_emotional_load(event)
        
        # Step 3: Assess progress
        progress_assessment = await self._assess_progress(event, context)
        
        # Step 4: Check philosophical alignment
        philosophical_alignment = await self._check_philosophical_alignment(event)
        
        # Step 5: Generate recommendations (context, not commands)
        recommendations = await self._generate_recommendations(
            coherence_score,
            emotional_load,
            philosophical_alignment
        )
        
        # Log reflection to episodic memory
        await self.write_episodic(
            event_type="self_reflection",
            context={
                'event': event,
                'coherence_score': coherence_score,
                'emotional_load': emotional_load,
                'recommendations': recommendations
            }
        )
        
        # Also log to reflective memory (Loki)
        await self.log_reflective(
            log_type="coherence_tracking",
            message=f"Coherence: {coherence_score:.2f}, Load: {emotional_load}",
            metadata={
                'event_type': event['type'],
                'subsystem': event['subsystem'],
                'coherence': coherence_score
            }
        )
        
        return {
            'reflection': {
                'coherence_score': coherence_score,
                'emotional_load_estimate': emotional_load,
                'progress_assessment': progress_assessment,
                'philosophical_alignment': philosophical_alignment
            },
            'recommendations': recommendations
        }
    
    async def _calculate_coherence(
        self,
        event: Dict[str, Any],
        context: Dict[str, Any]
    ) -> float:
        """
        Calculate how well this event aligns with mission memory.
        Returns score 0.0-1.0
        """
        # Get current mission from mission_memory
        async with self.postgres.cursor() as cur:
            await cur.execute("""
                SELECT mission_statement, coherence_score 
                FROM mission_memory 
                ORDER BY phase_timestamp DESC 
                LIMIT 1
            """)
            mission_row = await cur.fetchone()
        
        if not mission_row:
            # No mission set, default moderate coherence
            return 0.7
        
        current_mission = mission_row[0]
        baseline_coherence = float(mission_row[1]) if mission_row[1] else 1.0
        
        # Simple keyword overlap heuristic (can enhance with embeddings later)
        event_text = f"{event.get('description', '')} {event.get('outcome', {})}"
        mission_words = set(current_mission.lower().split())
        event_words = set(event_text.lower().split())
        
        overlap = len(mission_words.intersection(event_words))
        total = len(mission_words.union(event_words))
        
        if total == 0:
            return baseline_coherence
        
        # Jaccard similarity
        similarity = overlap / total
        
        # Blend with baseline
        coherence = (similarity * 0.4) + (baseline_coherence * 0.6)
        
        return min(1.0, max(0.0, coherence))
    
    async def _detect_emotional_load(
        self,
        event: Dict[str, Any]
    ) -> str:
        """
        Estimate emotional load from event description.
        Returns: "low", "medium", "high"
        """
        description = event.get('description', '').lower()
        
        # Count load indicators
        high_count = sum(1 for kw in self.high_load_keywords if kw in description)
        low_count = sum(1 for kw in self.low_load_keywords if kw in description)
        
        if high_count > 2:
            return "high"
        elif high_count > 0:
            return "medium"
        elif low_count > 1:
            return "low"
        else:
            return "medium"  # Default neutral
    
    async def _assess_progress(
        self,
        event: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """
        Assess progress toward goals based on recent episodic memory.
        """
        # Query recent events from this subsystem
        subsystem = event.get('subsystem', 'unknown')
        
        async with self.postgres.cursor() as cur:
            await cur.execute("""
                SELECT event_type, context 
                FROM episodic_memory 
                WHERE subsystem_id = %s 
                ORDER BY timestamp DESC 
                LIMIT 10
            """, (subsystem,))
            
            recent_events = []
            async for row in cur:
                recent_events.append({
                    'event_type': row[0],
                    'context': row[1]
                })
        
        if not recent_events:
            return "Insufficient data for progress assessment"
        
        # Count success vs failure events
        success_indicators = ['completed', 'success', 'approved', 'achieved']
        failure_indicators = ['failed', 'rejected', 'error', 'halted']
        
        success_count = 0
        failure_count = 0
        
        for evt in recent_events:
            evt_str = str(evt).lower()
            if any(ind in evt_str for ind in success_indicators):
                success_count += 1
            elif any(ind in evt_str for ind in failure_indicators):
                failure_count += 1
        
        total = success_count + failure_count
        if total == 0:
            return "Activity is ongoing, trajectory unclear"
        
        success_rate = success_count / total
        
        if success_rate > 0.7:
            return "Strong forward momentum, trajectory positive"
        elif success_rate > 0.4:
            return "Moderate progress, some obstacles encountered"
        else:
            return "Significant challenges detected, may require recalibration"
    
    async def _check_philosophical_alignment(
        self,
        event: Dict[str, Any]
    ) -> bool:
        """
        Check if event aligns with constitutional axioms.
        """
        # Get user sovereignty axiom
        user_sovereignty = self.constitution['axioms']['user_sovereignty']
        
        # Check for constraint violations
        event_text = str(event).lower()
        
        # Red flags that violate user sovereignty
        sovereignty_violations = [
            'override user',
            'ignore user',
            'force user',
            'manipulate user'
        ]
        
        for violation in sovereignty_violations:
            if violation in event_text:
                return False
        
        # Check permissive-until-dangerous principle
        axiom_pud = self.constitution['axioms']['permissive_until_dangerous']
        
        # Should default to permissive
        restrictive_keywords = ['forbid', 'prevent', 'block', 'deny']
        restriction_count = sum(1 for kw in restrictive_keywords if kw in event_text)
        
        # If overly restrictive without threshold justification, flag misalignment
        if restriction_count > 2:
            return False
        
        return True  # Default: aligned
    
    async def _generate_recommendations(
        self,
        coherence_score: float,
        emotional_load: str,
        philosophical_alignment: bool
    ) -> List[str]:
        """
        Generate contextual recommendations (not commands).
        """
        recommendations = []
        
        # Coherence-based recommendations
        if coherence_score < 0.5:
            recommendations.append(
                "Low coherence detected. Consider reviewing mission alignment."
            )
        elif coherence_score > 0.9:
            recommendations.append(
                "High coherence maintained. Current trajectory well-aligned."
            )
        
        # Emotional load recommendations
        if emotional_load == "high":
            recommendations.append(
                "High emotional load detected. Consider pacing or support structures."
            )
        elif emotional_load == "low":
            recommendations.append(
                "Operational clarity appears high. Favorable conditions for progress."
            )
        
        # Philosophical alignment
        if not philosophical_alignment:
            recommendations.append(
                "Potential constitutional misalignment detected. Review axiom adherence."
            )
        
        # If no specific issues, provide general context
        if not recommendations:
            recommendations.append(
                "System operating within expected parameters. Continue monitoring."
            )
        
        return recommendations
    
    def _check_constraints(self, proposed_output: Dict[str, Any]) -> bool:
        """
        Verify Mirror doesn't violate constitutional constraints.
        """
        recommendations = proposed_output.get('recommendations', [])
        
        # Mirror should never:
        # - Issue commands (provides_context_not_commands)
        # - Interfere with trading decisions
        # - Simulate therapy
        
        # Check for command-like language
        command_keywords = ['must', 'shall', 'require', 'order', 'command']
        
        for rec in recommendations:
            rec_lower = rec.lower()
            if any(cmd in rec_lower for cmd in command_keywords):
                self.logger.error(
                    f"Constraint violation: Mirror issued command-like recommendation: {rec}"
                )
                return False
        
        return True
