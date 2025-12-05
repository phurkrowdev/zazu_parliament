"""
Ledger Agent - Risk Engine
Constitutional constraint: STRICTLY NUMERIC, NO NARRATIVE
"""

from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent, SubsystemID, Mode
import statistics
from datetime import datetime, timedelta


class LedgerAgent(BaseAgent):
    """
    Risk quantification and variance tracking subsystem.
    
    Constitutional Constraints:
    - Can QUANTIFY risk and TRACK variance
    - NO CREATIVITY (strictly numeric)
    - NO NARRATIVE (no storytelling)
    - STRICTLY NUMERIC (data-driven only)
    - Cannot OVERRIDE Sentinel (safety veto authority remains with Sentinel)
    """
    
    def __init__(self, **kwargs):
        super().__init__(subsystem_id=SubsystemID.LEDGER, **kwargs)
        
        # Risk assessment parameters
        self.risk_thresholds = {
            'low': 0.3,
            'moderate': 0.6,
            'high': 0.85,
            'critical': 1.0
        }
        
        # Variance tracking window
        self.variance_window_days = 30
    
    async def _process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform risk quantification and variance analysis.
        
        Input schema:
        {
            "analysis_type": "risk|variance|backtest|scenario_safety",
            "data": {},
            "parameters": {},
            "context": {}
        }
        
        Output schema:
        {
            "analysis": {
                "type": str,
                "risk_score": float,
                "confidence_interval": [float, float],
                "metrics": {},
                "recommendations": []
            },
            "variance_data": {},
            "historical_comparison": {}
        }
        """
        analysis_type = input_data['analysis_type']
        data = input_data.get('data', {})
        parameters = input_data.get('parameters', {})
        context = input_data.get('context', {})
        
        # Route to appropriate analysis method
        if analysis_type == 'risk':
            analysis = await self._quantify_risk(data, parameters)
        elif analysis_type == 'variance':
            analysis = await self._track_variance(data, parameters)
        elif analysis_type == 'backtest':
            analysis = await self._backtest_strategy(data, parameters)
        elif analysis_type == 'scenario_safety':
            analysis = await self._check_scenario_safety(data, parameters)
        else:
            raise ValueError(f"Unsupported analysis type: {analysis_type}")
        
        # Get historical comparison
        historical = await self._get_historical_comparison(analysis_type, data)
        
        # Log to episodic memory
        await self.write_episodic(
            event_type="risk_analysis",
            context={
                'analysis_type': analysis_type,
                'risk_score': analysis.get('risk_score'),
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        
        return {
            'analysis': analysis,
            'variance_data': analysis.get('variance_data', {}),
            'historical_comparison': historical
        }
    
    async def _quantify_risk(
        self,
        data: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Quantify risk using statistical measures.
        """
        # Extract metrics from data
        metrics = data.get('metrics', {})
        
        # Calculate risk factors
        risk_factors = []
        total_risk = 0.0
        factor_count = 0
        
        # Factor 1: Complexity risk
        complexity = data.get('complexity', 0)
        if complexity > 0:
            complexity_risk = min(complexity / 10.0, 1.0)  # Normalize to 0-1
            risk_factors.append({'factor': 'complexity', 'score': complexity_risk})
            total_risk += complexity_risk
            factor_count += 1
        
        # Factor 2: Uncertainty risk
        uncertainty = data.get('uncertainty', 0.5)  # Default medium uncertainty
        risk_factors.append({'factor': 'uncertainty', 'score': uncertainty})
        total_risk += uncertainty
        factor_count += 1
        
        # Factor 3: Dependency risk
        dependencies = data.get('dependencies', [])
        dependency_risk = min(len(dependencies) / 5.0, 1.0)  # >5 deps = high risk
        if dependencies:
            risk_factors.append({'factor': 'dependencies', 'score': dependency_risk})
            total_risk += dependency_risk
            factor_count += 1
        
        # Factor 4: Timeline pressure
        timeline_days = data.get('timeline_days', 30)
        timeline_risk = max(0, 1.0 - (timeline_days / 90.0))  # <90 days increases risk
        risk_factors.append({'factor': 'timeline_pressure', 'score': timeline_risk})
        total_risk += timeline_risk
        factor_count += 1
        
        # Calculate aggregate risk score
        risk_score = total_risk / factor_count if factor_count > 0 else 0.5
        
        # Determine risk level
        risk_level = 'low'
        for level, threshold in reversed(list(self.risk_thresholds.items())):
            if risk_score <= threshold:
                risk_level = level
                break
        
        # Calculate confidence interval (simple ±10%)
        confidence_interval = [
            max(0.0, risk_score - 0.1),
            min(1.0, risk_score + 0.1)
        ]
        
        # Generate numeric recommendations
        recommendations = []
        if risk_score > 0.7:
            recommendations.append(f"Risk score {risk_score:.2f} exceeds threshold. Recommend risk mitigation.")
        if dependency_risk > 0.6:
            recommendations.append(f"{len(dependencies)} dependencies detected. Consider dependency reduction.")
        if timeline_risk > 0.5:
            recommendations.append(f"Timeline of {timeline_days} days compressed. Recommend buffer extension.")
        
        return {
            'type': 'risk_quantification',
            'risk_score': round(risk_score, 3),
            'risk_level': risk_level,
            'confidence_interval': confidence_interval,
            'metrics': {
                'risk_factors': risk_factors,
                'total_factors_assessed': factor_count
            },
            'recommendations': recommendations
        }
    
    async def _track_variance(
        self,
        data: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Track variance in metrics over time.
        """
        time_series = data.get('time_series', [])
        
        if not time_series or len(time_series) < 2:
            return {
                'type': 'variance_tracking',
                'risk_score': 0.5,
                'variance_data': {
                    'error': 'Insufficient data for variance calculation'
                },
                'metrics': {}
            }
        
        # Extract values
        values = [float(point.get('value', 0)) for point in time_series]
        
        # Calculate variance metrics
        mean_value = statistics.mean(values)
        variance = statistics.variance(values) if len(values) > 1 else 0
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        
        # Calculate coefficient of variation (CV)
        cv = (std_dev / mean_value) if mean_value != 0 else 0
        
        # Variance risk score (higher CV = higher risk)
        variance_risk = min(cv, 1.0)
        
        # Detect trend
        if len(values) >= 3:
            recent_avg = statistics.mean(values[-3:])
            older_avg = statistics.mean(values[:3])
            trend = 'increasing' if recent_avg > older_avg else 'decreasing'
        else:
            trend = 'insufficient_data'
        
        return {
            'type': 'variance_tracking',
            'risk_score': round(variance_risk, 3),
            'variance_data': {
                'mean': round(mean_value, 3),
                'variance': round(variance, 3),
                'std_dev': round(std_dev, 3),
                'coefficient_of_variation': round(cv, 3),
                'trend': trend,
                'data_points': len(values)
            },
            'metrics': {
                'min': min(values),
                'max': max(values),
                'range': max(values) - min(values)
            },
            'recommendations': [
                f"CV of {cv:.2f} indicates {'high' if cv > 0.3 else 'moderate' if cv > 0.15 else 'low'} variability"
            ]
        }
    
    async def _backtest_strategy(
        self,
        data: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Backtest a strategy against historical data.
        """
        historical_data = data.get('historical_data', [])
        strategy = data.get('strategy', {})
        
        if not historical_data:
            return {
                'type': 'backtest',
                'risk_score': 0.5,
                'metrics': {'error': 'No historical data provided'},
                'recommendations': ['Insufficient data for backtesting']
            }
        
        # Simulate strategy performance (simplified)
        wins = 0
        losses = 0
        total_return = 0.0
        
        for point in historical_data:
            # Simplified win/loss based on threshold
            outcome = point.get('outcome', 0)
            if outcome > 0:
                wins += 1
                total_return += outcome
            else:
                losses += 1
                total_return += outcome
        
        total_trades = wins + losses
        win_rate = wins / total_trades if total_trades > 0 else 0
        avg_return = total_return / total_trades if total_trades > 0 else 0
        
        # Risk score (inverse of win rate)
        risk_score = 1.0 - win_rate
        
        return {
            'type': 'backtest',
            'risk_score': round(risk_score, 3),
            'metrics': {
                'total_trades': total_trades,
                'wins': wins,
                'losses': losses,
                'win_rate': round(win_rate, 3),
                'avg_return': round(avg_return, 3),
                'total_return': round(total_return, 3)
            },
            'recommendations': [
                f"Win rate of {win_rate:.1%} {'meets' if win_rate > 0.5 else 'below'} threshold",
                f"Average return per trade: {avg_return:.3f}"
            ]
        }
    
    async def _check_scenario_safety(
        self,
        data: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check safety bounds for scenario outcomes.
        """
        scenarios = data.get('scenarios', [])
        safety_threshold = parameters.get('safety_threshold', 0.7)
        
        if not scenarios:
            return {
                'type': 'scenario_safety',
                'risk_score': 0.5,
                'metrics': {'error': 'No scenarios provided'},
                'recommendations': []
            }
        
        # Evaluate each scenario
        safe_scenarios = 0
        unsafe_scenarios = 0
        
        for scenario in scenarios:
            probability = scenario.get('probability', 0)
            outcome_quality = scenario.get('outcome_quality', 0.5)  # 0-1 scale
            
            # Scenario is "safe" if high probability AND acceptable outcome
            is_safe = (probability * outcome_quality) >= safety_threshold
            
            if is_safe:
                safe_scenarios += 1
            else:
                unsafe_scenarios += 1
        
        total = len(scenarios)
        safety_rate = safe_scenarios / total if total > 0 else 0
        
        # Risk is inverse of safety
        risk_score = 1.0 - safety_rate
        
        return {
            'type': 'scenario_safety',
            'risk_score': round(risk_score, 3),
            'metrics': {
                'total_scenarios': total,
                'safe_scenarios': safe_scenarios,
                'unsafe_scenarios': unsafe_scenarios,
                'safety_rate': round(safety_rate, 3)
            },
            'recommendations': [
                f"{safety_rate:.0%} of scenarios meet safety threshold",
                f"{'Acceptable' if safety_rate > 0.7 else 'Review required'} risk profile"
            ]
        }
    
    async def _get_historical_comparison(
        self,
        analysis_type: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare current analysis to historical baseline.
        """
        # Query historical analyses from episodic memory
        async with self.postgres.cursor() as cur:
            await cur.execute("""
                SELECT context
                FROM episodic_memory
                WHERE subsystem_id = 'ledger'
                  AND event_type = 'risk_analysis'
                  AND timestamp > NOW() - INTERVAL '30 days'
                ORDER BY timestamp DESC
                LIMIT 10
            """)
            
            historical_scores = []
            async for row in cur:
                ctx = row[0]
                if ctx and 'risk_score' in ctx:
                    historical_scores.append(ctx['risk_score'])
        
        if not historical_scores:
            return {
                'baseline_available': False,
                'message': 'Insufficient historical data for comparison'
            }
        
        # Calculate baseline stats
        baseline_mean = statistics.mean(historical_scores)
        baseline_std = statistics.stdev(historical_scores) if len(historical_scores) > 1 else 0
        
        return {
            'baseline_available': True,
            'baseline_mean': round(baseline_mean, 3),
            'baseline_std_dev': round(baseline_std, 3),
            'data_points': len(historical_scores),
            'comparison': 'Current analysis compared against 30-day historical baseline'
        }
    
    def _check_constraints(self, proposed_output: Dict[str, Any]) -> bool:
        """
        Verify Ledger doesn't violate constitutional constraints.
        """
        analysis = proposed_output.get('analysis', {})
        
        # Ledger should never:
        # - Include narrative/creative content (strictly_numeric)
        # - Make qualitative judgments beyond quantification
        # - Override Sentinel's safety decisions
        
        # Check for narrative language
        recommendations = analysis.get('recommendations', [])
        narrative_keywords = ['story', 'mythos', 'aesthetic', 'symbolic', 'beautiful']
        
        for rec in recommendations:
            rec_lower = str(rec).lower()
            for keyword in narrative_keywords:
                if keyword in rec_lower:
                    self.logger.error(
                        f"Constraint violation: Ledger included narrative language: {keyword}"
                    )
                    return False
        
        # Ensure numeric focus
        if 'risk_score' not in analysis or not isinstance(analysis.get('risk_score'), (int, float)):
            self.logger.error("Ledger analysis missing numeric risk_score")
            return False
        
        return True
