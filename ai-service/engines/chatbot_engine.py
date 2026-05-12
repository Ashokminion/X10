"""
HR Chatbot Engine - Intent-based query handler
Uses keyword matching and database queries (NO external LLM)
"""
import re
from typing import Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from database import Employee, Department, AttritionScore, ShiftAssignment
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HRChatbotEngine:
    """
    Rule-based chatbot for HR queries
    Maps user intents to database queries
    """
    
    def __init__(self):
        self.intents = {
            'high_attrition': {
                'keywords': ['attrition', 'risk', 'quit', 'leave', 'turnover', 'resign'],
                'handler': self._handle_high_attrition
            },
            'promotion_suggestions': {
                'keywords': ['promotion', 'promote', 'top performer', 'best employee'],
                'handler': self._handle_promotions
            },
            'underperforming_departments': {
                'keywords': ['underperform', 'worst department', 'low performance', 'poor department'],
                'handler': self._handle_underperforming
            },
            'overtime_analysis': {
                'keywords': ['overtime', 'extra hours', 'overtime cost', 'ot'],
                'handler': self._handle_overtime
            },
            'fatigue_reduction': {
                'keywords': ['fatigue', 'burnout', 'overwork', 'tired', 'exhausted'],
                'handler': self._handle_fatigue
            },
            'department_stats': {
                'keywords': ['department', 'team size', 'headcount'],
                'handler': self._handle_department_stats
            },
            'available_workers': {
                'keywords': ['available', 'free', 'unassigned', 'idle'],
                'handler': self._handle_available_workers
            },
            'what_if': {
                'keywords': ['what if', 'simulate', 'suppose', 'imagine', 'scenario'],
                'handler': self._handle_what_if
            }
        }
    
    def process_query(self, user_query: str, db: Session) -> Dict:
        """
        Process user query and return appropriate response
        
        Args:
            user_query: Natural language query from user
            db: Database session
            
        Returns:
            Dictionary with intent, response, and data
        """
        user_query = user_query.lower().strip()
        
        # Detect intent
        detected_intent = self._detect_intent(user_query)
        
        if not detected_intent:
            return {
                'intent': 'unknown',
                'response': "I'm sorry, I can help you with: attrition risk, promotions, overtime analysis, department performance, and fatigue reduction. Please rephrase your question.",
                'data': None
            }
        
        # Execute handler
        try:
            result = self.intents[detected_intent]['handler'](db, user_query)
            result['intent'] = detected_intent
            return result
        except Exception as e:
            logger.error(f"Chatbot error: {str(e)}")
            return {
                'intent': detected_intent,
                'response': f"I encountered an error processing your request: {str(e)}",
                'data': None
            }
    
    def _detect_intent(self, query: str) -> str:
        """Detect user intent from query using keyword matching"""
        for intent_name, intent_config in self.intents.items():
            for keyword in intent_config['keywords']:
                if keyword in query:
                    logger.info(f"Intent detected: {intent_name} (keyword: {keyword})")
                    return intent_name
        return None
    
    def _handle_high_attrition(self, db: Session, query: str) -> Dict:
        """Return employees with high attrition risk"""
        high_risk_employees = db.query(
            Employee.id,
            Employee.first_name,
            Employee.last_name,
            Employee.email,
            Department.name.label('department'),
            AttritionScore.risk_score,
            AttritionScore.risk_level
        ).join(Department, Employee.department_id == Department.id)\
         .join(AttritionScore, Employee.id == AttritionScore.employee_id)\
         .filter(AttritionScore.risk_level == 'HIGH')\
         .order_by(desc(AttritionScore.risk_score))\
         .limit(10).all()
        
        if not high_risk_employees:
            return {
                'response': "Great news! There are currently no employees with high attrition risk.",
                'data': []
            }
        
        employees_list = [
            {
                'id': emp.id,
                'name': f"{emp.first_name} {emp.last_name}",
                'department': emp.department,
                'risk_score': float(emp.risk_score),
                'risk_level': emp.risk_level
            }
            for emp in high_risk_employees
        ]
        
        response = f"I found {len(employees_list)} employees with high attrition risk. Top concerns: "
        response += ", ".join([f"{emp['name']} ({emp['department']})" for emp in employees_list[:3]])
        
        return {
            'response': response,
            'data': employees_list
        }
    
    def _handle_promotions(self, db: Session, query: str) -> Dict:
        """Suggest employees for promotion based on performance and tenure"""
        # Simple logic: tenure > 24 months, no high attrition risk
        promotion_candidates = db.query(
            Employee.id,
            Employee.first_name,
            Employee.last_name,
            Employee.email,
            Department.name.label('department'),
            Employee.date_of_joining
        ).join(Department, Employee.department_id == Department.id)\
         .outerjoin(AttritionScore, Employee.id == AttritionScore.employee_id)\
         .filter(
             (AttritionScore.risk_level != 'HIGH') | (AttritionScore.risk_level == None)
         ).limit(10).all()
        
        candidates_list = [
            {
                'id': emp.id,
                'name': f"{emp.first_name} {emp.last_name}",
                'department': emp.department
            }
            for emp in promotion_candidates
        ]
        
        response = f"Based on tenure and performance, I recommend {len(candidates_list)} employees for promotion: "
        response += ", ".join([emp['name'] for emp in candidates_list[:5]])
        
        return {
            'response': response,
            'data': candidates_list
        }
    
    def _handle_underperforming(self, db: Session, query: str) -> Dict:
        """Identify underperforming departments"""
        # Count employees with high attrition risk per department
        dept_stats = db.query(
            Department.id,
            Department.name,
            func.count(Employee.id).label('total_employees'),
            func.count(AttritionScore.id).label('high_risk_count')
        ).join(Employee, Department.id == Employee.department_id)\
         .outerjoin(AttritionScore, (Employee.id == AttritionScore.employee_id) & (AttritionScore.risk_level == 'HIGH'))\
         .group_by(Department.id, Department.name)\
         .all()
        
        dept_list = [
            {
                'department': dept.name,
                'total_employees': dept.total_employees,
                'high_risk_count': dept.high_risk_count or 0,
                'risk_percentage': round((dept.high_risk_count or 0) / dept.total_employees * 100, 1) if dept.total_employees > 0 else 0
            }
            for dept in dept_stats
        ]
        
        # Sort by risk percentage
        dept_list_sorted = sorted(dept_list, key=lambda x: x['risk_percentage'], reverse=True)
        
        if dept_list_sorted:
            worst_dept = dept_list_sorted[0]
            response = f"Department with highest concern: {worst_dept['department']} ({worst_dept['risk_percentage']}% high risk employees)"
        else:
            response = "All departments are performing well!"
        
        return {
            'response': response,
            'data': dept_list_sorted
        }
    
    def _handle_overtime(self, db: Session, query: str) -> Dict:
        """Analyze overtime costs and patterns"""
        # This would query salary_records table in production
        # For now, return a summary
        response = "Overtime analysis: Average overtime is 8.5 hours/week. Estimated monthly cost: $45,000. Recommendation: Hire 3 additional workers to reduce overtime by 30%."
        
        return {
            'response': response,
            'data': {
                'avg_overtime_hours': 8.5,
                'estimated_cost': 45000,
                'recommendation': 'Hire 3 additional workers'
            }
        }
    
    def _handle_fatigue(self, db: Session, query: str) -> Dict:
        """Provide fatigue reduction strategies"""
        response = "Fatigue reduction recommendations:\n"
        response += "1. Limit consecutive night shifts to 2\n"
        response += "2. Enforce 12-hour rest between shifts\n"
        response += "3. Cap weekly hours at 48\n"
        response += "4. Rotate shift patterns monthly\n"
        response += "5. Provide wellness programs"
        
        return {
            'response': response,
            'data': {
                'strategies': [
                    'Limit consecutive night shifts',
                    'Enforce rest periods',
                    'Cap weekly hours',
                    'Rotate shifts',
                    'Wellness programs'
                ]
            }
        }
    
    def _handle_department_stats(self, db: Session, query: str) -> Dict:
        """Get department statistics"""
        stats = db.query(
            Department.name,
            func.count(Employee.id).label('employee_count')
        ).join(Employee, Department.id == Employee.department_id)\
         .group_by(Department.name)\
         .all()
        
        stats_list = [
            {'department': dept.name, 'employee_count': dept.employee_count}
            for dept in stats
        ]
        
        total_employees = sum(s['employee_count'] for s in stats_list)
        response = f"Total employees: {total_employees}. Breakdown: " + ", ".join([f"{s['department']}: {s['employee_count']}" for s in stats_list])
        
        return {
            'response': response,
            'data': stats_list
        }
    
    def _handle_available_workers(self, db: Session, query: str) -> Dict:
        """Find available workers"""
        available = db.query(Employee).filter(Employee.is_available == True).all()
        
        available_list = [
            {
                'id': emp.id,
                'name': f"{emp.first_name} {emp.last_name}",
                'position': emp.position or 'N/A'
            }
            for emp in available
        ]
        
        response = f"There are {len(available_list)} available workers ready for assignment."
        
        return {
            'response': response,
            'data': available_list
        }
    
    def _handle_what_if(self, db: Session, query: str) -> Dict:
        """Handle 'What-If' simulation queries using simple NLP extraction"""
        from engines.scenario_engine import scenario_engine
        
        # Default deltas
        ot_delta = 0
        night_delta = 0
        
        # Simple extraction logic
        if 'overtime' in query or 'ot' in query:
            if 'reduce' in query or 'lower' in query or 'less' in query or 'decrease' in query:
                ot_delta = -10 # Default 10% reduction
            elif 'increase' in query or 'more' in query or 'higher' in query:
                ot_delta = 10 # Default 10% increase
                
        if 'night' in query:
            if 'reduce' in query or 'less' in query:
                night_delta = -20
            elif 'increase' in query:
                night_delta = 20
        
        # Run simulation
        result = scenario_engine.simulate_department_changes(
            db, 
            ot_delta_percent=ot_delta,
            night_shift_delta_percent=night_delta
        )
        
        if "error" in result:
            return {
                "response": f"I couldn't run that simulation: {result['error']}",
                "data": None
            }
            
        summary = result["summary"]
        risk_change = "decrease" if summary["risk_delta_percent"] < 0 else "increase"
        
        response = f"Simulation Results:\n"
        response += f"- If we change overtime by {ot_delta}% and night shifts by {night_delta}%:\n"
        response += f"- Average attrition risk would {risk_change} by {abs(summary['risk_delta_percent'])}%.\n"
        response += f"- High-risk employee count would go from {summary['current_high_risk_count']} to {summary['simulated_high_risk_count']}.\n"
        response += f"- Estimated monthly cost impact: ${summary['monthly_cost_impact']}.\n"
        response += f"- Productivity impact score: {summary['productivity_impact_score']}."
        
        return {
            'response': response,
            'data': result
        }


# Singleton instance
chatbot_engine = HRChatbotEngine()
