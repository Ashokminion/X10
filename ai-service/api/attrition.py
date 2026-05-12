"""
FastAPI router for attrition prediction endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from database import get_db, Employee, AttritionScore
from sqlalchemy.orm import Session
from engines.attrition_model import attrition_predictor
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class AttritionPredictionRequest(BaseModel):
    employee_id: int
    overtime_hours_3m: float = 0
    night_shifts_count_3m: int = 0
    performance_score: float = 70
    absenteeism_rate: float = 0
    tenure_months: int = 12

class AttritionPredictionResponse(BaseModel):
    employee_id: int
    risk_score: float
    risk_level: str
    model_version: str
    prediction_date: date

@router.post("/predict", response_model=AttritionPredictionResponse)
async def predict_attrition(request: AttritionPredictionRequest, db: Session = Depends(get_db)):
    """
    Predict attrition risk for an employee using Random Forest model
    """
    try:
        # Get prediction
        prediction = attrition_predictor.predict(request.model_dump())
        
        # Save to database
        attrition_score = AttritionScore(
            employee_id=request.employee_id,
            prediction_date=date.today(),
            risk_score=prediction['risk_score'],
            risk_level=prediction['risk_level'],
            overtime_hours_3m=request.overtime_hours_3m,
            night_shifts_count_3m=request.night_shifts_count_3m,
            performance_score=request.performance_score,
            absenteeism_rate=request.absenteeism_rate,
            tenure_months=request.tenure_months,
            model_version=prediction['model_version']
        )
        
        db.add(attrition_score)
        db.commit()
        
        return AttritionPredictionResponse(
            employee_id=request.employee_id,
            risk_score=prediction['risk_score'],
            risk_level=prediction['risk_level'],
            model_version=prediction['model_version'],
            prediction_date=date.today()
        )
        
    except Exception as e:
        logger.error(f"Attrition prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict-batch")
async def predict_attrition_batch(requests: List[AttritionPredictionRequest], db: Session = Depends(get_db)):
    """
    Predict attrition risk for multiple employees
    """
    try:
        employees_data = [req.model_dump() for req in requests]
        predictions = attrition_predictor.predict_batch(employees_data)
        
        # Save all to database
        for pred in predictions:
            if 'error' not in pred:
                attrition_score = AttritionScore(
                    employee_id=pred['employee_id'],
                    prediction_date=date.today(),
                    risk_score=pred['risk_score'],
                    risk_level=pred['risk_level'],
                    model_version=pred['model_version']
                )
                db.add(attrition_score)
        
        db.commit()
        return {'predictions': predictions, 'count': len(predictions)}
        
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/high-risk")
async def get_high_risk_employees(db: Session = Depends(get_db)):
    """
    Get all employees with high attrition risk
    """
    high_risk = db.query(AttritionScore).filter(
        AttritionScore.risk_level == 'HIGH'
    ).order_by(AttritionScore.risk_score.desc()).all()
    
    result = []
    for score in high_risk:
        employee = db.query(Employee).filter(Employee.id == score.employee_id).first()
        if employee:
            result.append({
                'employee_id': employee.id,
                'employee_name': f"{employee.first_name} {employee.last_name}",
                'risk_score': float(score.risk_score),
                'risk_level': score.risk_level,
                'prediction_date': str(score.prediction_date)
            })
    
    return {'high_risk_employees': result, 'count': len(result)}
