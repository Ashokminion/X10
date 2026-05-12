"""
FastAPI router for shift optimization endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import date, time
from database import get_db, Employee, Shift, ShiftAssignment
from sqlalchemy.orm import Session
from engines.optimization_engine import optimization_engine
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class EmployeeOptimization(BaseModel):
    id: int
    first_name: str
    last_name: str
    hourly_wage: float
    night_shift_allowance: float
    is_available: bool
    skill_ids: List[int] = []

class ShiftOptimization(BaseModel):
    id: int
    shift_name: str
    shift_date: date
    start_time: time
    end_time: time
    shift_type: str
    required_workers: int
    required_skill_id: Optional[int] = None

class OptimizationRequest(BaseModel):
    employees: List[EmployeeOptimization]
    shifts: List[ShiftOptimization]
    constraints: Dict = {
        'max_weekly_hours': 48,
        'min_rest_hours': 12,
        'max_consecutive_nights': 3
    }

class OptimizationResponse(BaseModel):
    status: str
    assignments: List[Dict]
    objective_value: Optional[float] = None
    solve_time_seconds: Optional[float] = None
    total_employees_assigned: int
    total_shifts_covered: int

@router.post("/optimize", response_model=OptimizationResponse)
async def optimize_shifts(request: OptimizationRequest, db: Session = Depends(get_db)):
    """
    Optimize shift assignments using Google OR-Tools
    
    Returns optimized employee-shift assignments with cost minimization
    """
    try:
        logger.info(f"Optimization request received: {len(request.employees)} employees, {len(request.shifts)} shifts")
        
        # Convert Pydantic models to dicts for optimization engine
        employees_data = [emp.model_dump() for emp in request.employees]
        shifts_data = [shift.model_dump() for shift in request.shifts]
        
        # Convert date/time objects to strings for serialization
        for shift in shifts_data:
            shift['shift_date'] = str(shift['shift_date'])
            shift['start_time'] = str(shift['start_time'])
            shift['end_time'] = str(shift['end_time'])
        
        # Run optimization
        result = optimization_engine.optimize_shifts(
            employees=employees_data,
            shifts=shifts_data,
            constraints=request.constraints
        )
        
        # Save assignments to database
        if result['status'] in ['OPTIMAL', 'FEASIBLE']:
            for assignment in result['assignments']:
                shift_assignment = ShiftAssignment(
                    employee_id=assignment['employee_id'],
                    shift_id=assignment['shift_id'],
                    assignment_type='OPTIMIZED',
                    status='ASSIGNED'
                )
                db.add(shift_assignment)
            
            db.commit()
            logger.info(f"Saved {len(result['assignments'])} assignments to database")
        
        return OptimizationResponse(**result)
        
    except Exception as e:
        logger.error(f"Optimization error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/assignments/{shift_id}")
async def get_shift_assignments(shift_id: int, db: Session = Depends(get_db)):
    """
    Get all employees assigned to a specific shift
    """
    assignments = db.query(ShiftAssignment).filter(
        ShiftAssignment.shift_id == shift_id
    ).all()
    
    result = []
    for assignment in assignments:
        employee = db.query(Employee).filter(Employee.id == assignment.employee_id).first()
        if employee:
            result.append({
                'assignment_id': assignment.id,
                'employee_id': employee.id,
                'employee_name': f"{employee.first_name} {employee.last_name}",
                'status': assignment.status
            })
    
    return {'shift_id': shift_id, 'assignments': result}
