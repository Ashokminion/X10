"""
Scenario Engine - Workforce simulation and What-If analysis
Uses AttritionPredictor to model impacts of changes
"""
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import Employee, AttritionScore, Department, ShiftAssignment
from engines.attrition_model import attrition_predictor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScenarioEngine:
    """
    Engine for simulating changes in employee workload, pay, or shifts
    and predicting the impact on attrition, cost, and productivity.
    """
    
    def simulate_department_changes(
        self, 
        db: Session, 
        department_id: Optional[int] = None,
        ot_delta_percent: float = 0,
        night_shift_delta_percent: float = 0,
        salary_delta_percent: float = 0
    ) -> Dict:
        """
        Simulate changes for an entire department or company
        
        Args:
            db: Database session
            department_id: Target department (None for all)
            ot_delta_percent: Percentage change in overtime (e.g., -10 for 10% reduction)
            night_shift_delta_percent: Percentage change in night shifts
            salary_delta_percent: Percentage change in salary (not currently in predictor but used for cost)
            
        Returns:
            Comparison between current state and simulated state
        """
        # 1. Get current employees and their latest attrition scores
        query = db.query(Employee, AttritionScore).join(
            AttritionScore, Employee.id == AttritionScore.employee_id
        )
        
        if department_id:
            query = query.filter(Employee.department_id == department_id)
            
        # Get only the latest score for each employee (simplified version for demo)
        # In production, we'd use a subquery to get the absolute latest
        current_data = query.all()
        
        if not current_data:
            return {"error": "No employee attrition data found for simulation"}
            
        current_total_risk = 0
        simulated_total_risk = 0
        current_high_risk_count = 0
        simulated_high_risk_count = 0
        
        total_employees = len(current_data)
        total_monthly_cost_delta = 0
        
        simulated_results = []
        
        for emp, score in current_data:
            # Current metrics
            current_risk = float(score.risk_score)
            current_total_risk += current_risk
            if score.risk_level == 'HIGH':
                current_high_risk_count += 1
                
            # Simulate features
            sim_features = {
                'overtime_hours_3m': float(score.overtime_hours_3m or 0) * (1 + ot_delta_percent / 100),
                'night_shifts_count_3m': int(float(score.night_shifts_count_3m or 0) * (1 + night_shift_delta_percent / 100)),
                'performance_score': float(score.performance_score or 70),
                'absenteeism_rate': float(score.absenteeism_rate or 0),
                'tenure_months': int(score.tenure_months or 12)
            }
            
            # Predict new risk
            prediction = attrition_predictor.predict(sim_features)
            sim_risk = prediction['risk_score']
            simulated_total_risk += sim_risk
            
            if prediction['risk_level'] == 'HIGH':
                simulated_high_risk_count += 1
                
            # Cost impact (Heuristic)
            # OT cost change = Delta OT hours * Hourly Wage * OT Rate
            ot_hours_change = sim_features['overtime_hours_3m'] - float(score.overtime_hours_3m or 0)
            cost_change = ot_hours_change * float(emp.hourly_wage) * float(emp.overtime_rate or 1.5)
            total_monthly_cost_delta += cost_change
            
        # Heuristic Productivity Impact
        # Reducing OT by 10% might improve productivity by 5% due to less fatigue
        productivity_impact = - (ot_delta_percent * 0.5) # Negative delta (reduction) -> positive impact
        
        return {
            "summary": {
                "total_employees": total_employees,
                "current_avg_risk": round(current_total_risk / total_employees, 3),
                "simulated_avg_risk": round(simulated_total_risk / total_employees, 3),
                "risk_delta_percent": round((simulated_total_risk - current_total_risk) / current_total_risk * 100, 2) if current_total_risk > 0 else 0,
                "current_high_risk_count": current_high_risk_count,
                "simulated_high_risk_count": simulated_high_risk_count,
                "monthly_cost_impact": round(total_monthly_cost_delta, 2),
                "productivity_impact_score": round(productivity_impact, 1)
            },
            "parameters_applied": {
                "ot_delta": ot_delta_percent,
                "night_shift_delta": night_shift_delta_percent,
                "salary_delta": salary_delta_percent
            }
        }

# Singleton instance
scenario_engine = ScenarioEngine()
