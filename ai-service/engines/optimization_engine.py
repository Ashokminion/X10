"""
Shift Optimization Engine using Google OR-Tools CP-SAT Solver
Enterprise-grade constraint programming for workforce scheduling
"""
from ortools.sat.python import cp_model
from typing import List, Dict, Tuple
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ShiftOptimizationEngine:
    """
    Optimizes shift assignments using constraint programming
    Objective: Minimize total cost (wages + overtime + penalties)
    """
    
    def __init__(self):
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        
    def optimize_shifts(self, employees: List[Dict], shifts: List[Dict], constraints: Dict) -> Dict:
        """
        Main optimization function
        
        Args:
            employees: List of employee data with skills, wages, availability
            shifts: List of shift requirements
            constraints: Optimization constraints (max_hours, rest_period, etc.)
            
        Returns:
            Optimized assignments with cost breakdown
        """
        try:
            logger.info(f"Starting optimization for {len(employees)} employees and {len(shifts)} shifts")
            
            # Decision Variables: X[worker_id][shift_id] = 1 if assigned, 0 otherwise
            assignments = {}
            for emp in employees:
                for shift in shifts:
                    var_name = f"emp_{emp['id']}_shift_{shift['id']}"
                    assignments[(emp['id'], shift['id'])] = self.model.NewBoolVar(var_name)
            
            # Constraint 1: Shift Coverage - Each shift must have required number of workers
            for shift in shifts:
                workers_assigned = []
                for emp in employees:
                    workers_assigned.append(assignments[(emp['id'], shift['id'])])
                self.model.Add(sum(workers_assigned) >= shift['required_workers'])
            
            # Constraint 2: Skill Matching - Only assign workers with required skills
            for shift in shifts:
                if shift.get('required_skill_id'):
                    for emp in employees:
                        emp_skills = emp.get('skill_ids', [])
                        if shift['required_skill_id'] not in emp_skills:
                            # Force this assignment to 0
                            self.model.Add(assignments[(emp['id'], shift['id'])] == 0)
            
            # Constraint 3: Max Weekly Hours - Workers cannot exceed max weekly hours
            max_weekly_hours = constraints.get('max_weekly_hours', 48)
            for emp in employees:
                weekly_hours = []
                for shift in shifts:
                    shift_hours = self._calculate_shift_duration(shift)
                    weekly_hours.append(assignments[(emp['id'], shift['id'])] * shift_hours)
                self.model.Add(sum(weekly_hours) <= max_weekly_hours)
            
            # Constraint 4: Rest Period - 12-hour gap between shifts
            shifts_sorted = sorted(shifts, key=lambda x: (x['shift_date'], x['start_time']))
            for emp in employees:
                for i in range(len(shifts_sorted) - 1):
                    shift1 = shifts_sorted[i]
                    shift2 = shifts_sorted[i + 1]
                    if self._shifts_too_close(shift1, shift2):
                        # Cannot work both shifts
                        self.model.Add(
                            assignments[(emp['id'], shift1['id'])] + 
                            assignments[(emp['id'], shift2['id'])] <= 1
                        )
            
            # Constraint 5: Limit Consecutive Night Shifts (max 3)
            night_shifts = [s for s in shifts if s['shift_type'] == 'NIGHT']
            for emp in employees:
                for i in range(len(night_shifts) - 2):
                    consecutive = [
                        assignments[(emp['id'], night_shifts[i]['id'])],
                        assignments[(emp['id'], night_shifts[i+1]['id'])],
                        assignments[(emp['id'], night_shifts[i+2]['id'])]
                    ]
                    if len(consecutive) >= 3:
                        self.model.Add(sum(consecutive) <= 2)
            
            # Constraint 6: Fair Distribution - Balance workload
            avg_shifts_per_worker = len(shifts) * shifts[0].get('required_workers', 1) / len(employees)
            for emp in employees:
                emp_shifts = [assignments[(emp['id'], s['id'])] for s in shifts]
                # Allow ±20% variance from average
                self.model.Add(sum(emp_shifts) >= int(avg_shifts_per_worker * 0.8))
                self.model.Add(sum(emp_shifts) <= int(avg_shifts_per_worker * 1.2) + 1)
            
            # Objective Function: Minimize total cost
            total_cost = []
            
            for emp in employees:
                for shift in shifts:
                    if assignments.get((emp['id'], shift['id'])):
                        var = assignments[(emp['id'], shift['id'])]
                        
                        # Base wage cost
                        shift_hours = self._calculate_shift_duration(shift)
                        wage = int(emp['hourly_wage'] * shift_hours)
                        total_cost.append(var * wage)
                        
                        # Overtime penalty (shifts beyond 40 hours/week)
                        overtime_penalty = int(wage * 0.5)  # 50% premium
                        total_cost.append(var * overtime_penalty)
                        
                        # Night shift penalty
                        if shift['shift_type'] == 'NIGHT':
                            night_penalty = int(emp.get('night_shift_allowance', 50))
                            total_cost.append(var * night_penalty)
                        
                        # Skill mismatch penalty (if worker doesn't have optimal skill)
                        if shift.get('required_skill_id'):
                            if shift['required_skill_id'] not in emp.get('skill_ids', []):
                                total_cost.append(var * 1000)  # High penalty
            
            # Set objective
            self.model.Minimize(sum(total_cost))
            
            # Solve
            self.solver.parameters.max_time_in_seconds = 60.0
            status = self.solver.Solve(self.model)
            
            if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
                # Extract solution
                solution = self._extract_solution(assignments, employees, shifts)
                solution['status'] = 'OPTIMAL' if status == cp_model.OPTIMAL else 'FEASIBLE'
                solution['objective_value'] = self.solver.ObjectiveValue()
                solution['solve_time_seconds'] = self.solver.WallTime()
                
                logger.info(f"Optimization completed: {solution['status']}, Cost: ${solution['objective_value']}")
                return solution
            else:
                logger.error(f"Optimization failed with status: {status}")
                return {
                    'status': 'FAILED',
                    'message': 'No feasible solution found',
                    'assignments': []
                }
                
        except Exception as e:
            logger.error(f"Optimization error: {str(e)}")
            raise
    
    def _calculate_shift_duration(self, shift: Dict) -> int:
        """Calculate shift duration in hours"""
        start = shift['start_time']
        end = shift['end_time']
        # Simple calculation (can be enhanced for cross-day shifts)
        return 8  # Default 8-hour shifts
    
    def _shifts_too_close(self, shift1: Dict, shift2: Dict) -> bool:
        """Check if shifts violate 12-hour rest period"""
        # Simplified logic - check if shifts are on consecutive days
        date1 = shift1['shift_date']
        date2 = shift2['shift_date']
        
        if isinstance(date1, str):
            from datetime import datetime
            date1 = datetime.strptime(date1, '%Y-%m-%d').date()
            date2 = datetime.strptime(date2, '%Y-%m-%d').date()
        
        return (date2 - date1).days <= 1
    
    def _extract_solution(self, assignments: Dict, employees: List, shifts: List) -> Dict:
        """Extract assignment solution from solver"""
        result_assignments = []
        
        for emp in employees:
            for shift in shifts:
                if self.solver.Value(assignments[(emp['id'], shift['id'])]) == 1:
                    result_assignments.append({
                        'employee_id': emp['id'],
                        'employee_name': f"{emp.get('first_name', '')} {emp.get('last_name', '')}",
                        'shift_id': shift['id'],
                        'shift_name': shift['shift_name'],
                        'shift_date': str(shift['shift_date']),
                        'shift_type': shift['shift_type']
                    })
        
        return {
            'assignments': result_assignments,
            'total_employees_assigned': len(set(a['employee_id'] for a in result_assignments)),
            'total_shifts_covered': len(set(a['shift_id'] for a in result_assignments))
        }


# Singleton instance
optimization_engine = ShiftOptimizationEngine()
