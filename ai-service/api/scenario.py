"""
FastAPI router for workforce scenario simulations
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from database import get_db
from engines.scenario_engine import scenario_engine
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class SimulationRequest(BaseModel):
    department_id: Optional[int] = None
    ot_delta_percent: float = 0
    night_shift_delta_percent: float = 0
    salary_delta_percent: float = 0

@router.post("/simulate")
async def simulate_scenario(request: SimulationRequest, db: Session = Depends(get_db)):
    """
    Run a What-If simulation based on provided deltas
    """
    try:
        result = scenario_engine.simulate_department_changes(
            db,
            department_id=request.department_id,
            ot_delta_percent=request.ot_delta_percent,
            night_shift_delta_percent=request.night_shift_delta_percent,
            salary_delta_percent=request.salary_delta_percent
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
            
        return result
    except Exception as e:
        logger.error(f"Simulation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config")
async def get_simulation_config():
    """
    Get supported simulation parameters
    """
    return {
        "parameters": [
            {
                "name": "ot_delta_percent",
                "label": "Overtime Change (%)",
                "min": -100,
                "max": 100,
                "default": 0,
                "description": "Adjust average monthly overtime hours"
            },
            {
                "name": "night_shift_delta_percent",
                "label": "Night Shift Change (%)",
                "min": -50,
                "max": 50,
                "default": 0,
                "description": "Adjust frequency of night shift assignments"
            },
            {
                "name": "salary_delta_percent",
                "label": "Salary Adjustment (%)",
                "min": -10,
                "max": 30,
                "default": 0,
                "description": "Hypothetical salary changes (affects cost and retention)"
            }
        ]
    }
