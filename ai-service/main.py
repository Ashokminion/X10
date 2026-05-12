"""
AI Workforce Intelligence Microservice
Complete backend with employee management, CSV upload, shift optimization,
attrition prediction, chatbot, and reporting for Indian Blue-Collar Workforce Companies
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import date, time, datetime
import uvicorn
import os
import csv
import io
import glob
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
from api import optimization, attrition, chatbot, reports, scenario

app = FastAPI(
    title="AI Workforce Intelligence Platform",
    description="AI-powered shift optimization for India's top blue-collar workforce companies: Swiggy, Zomato, Blinkit, Zepto, Amazon India, Flipkart, L&T",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── In-Memory Data Store ───────────────────────────────────────────────────
# Using in-memory store for instant startup (no DB setup needed)
EMPLOYEES_DB: Dict[str, dict] = {}
COMPANIES_DB: Dict[str, dict] = {}
SHIFTS_DB: Dict[str, dict] = {}
UPLOAD_HISTORY: List[dict] = []

COMPANY_INFO = {
    "Swiggy": {"sector": "Food Delivery", "color": "#FC8019", "icon": "🍕", "hq": "Bangalore"},
    "Zomato": {"sector": "Food Delivery", "color": "#E23744", "icon": "🍔", "hq": "Gurugram"},
    "Blinkit": {"sector": "Quick Commerce", "color": "#F8CB46", "icon": "⚡", "hq": "Gurugram"},
    "Zepto": {"sector": "Quick Commerce", "color": "#8B5CF6", "icon": "🚀", "hq": "Mumbai"},
    "Amazon India": {"sector": "E-commerce Warehouse", "color": "#FF9900", "icon": "📦", "hq": "Bangalore"},
    "Flipkart": {"sector": "E-commerce Logistics", "color": "#2974F0", "icon": "🛒", "hq": "Bangalore"},
    "Larsen & Toubro": {"sector": "Construction / Labour", "color": "#003B73", "icon": "🏗️", "hq": "Mumbai"},
}

# ─── Pydantic Models ────────────────────────────────────────────────────────
class EmployeeCreate(BaseModel):
    employee_code: str
    first_name: str
    last_name: str
    email: str
    phone: str = ""
    company: str
    department: str
    position: str
    hourly_wage: float = 0
    base_salary: float = 0
    date_of_joining: str = ""
    shift_type: str = "MORNING"
    weekly_hours: float = 48
    overtime_hours_3m: float = 0
    night_shifts_count_3m: int = 0
    performance_score: float = 70
    absenteeism_rate: float = 0
    tenure_months: int = 12
    attrition_risk: str = "LOW"
    skills: str = ""
    city: str = ""

class CompanyCreate(BaseModel):
    name: str
    sector: str
    color: str = "#6366f1"
    icon: str = "🏢"
    hq: str = "India"

class EmployeeResponse(BaseModel):
    employee_code: str
    first_name: str
    last_name: str
    full_name: str
    email: str
    phone: str
    company: str
    department: str
    position: str
    hourly_wage: float
    base_salary: float
    date_of_joining: str
    shift_type: str
    weekly_hours: float
    overtime_hours_3m: float
    night_shifts_count_3m: int
    performance_score: float
    absenteeism_rate: float
    tenure_months: int
    attrition_risk: str
    skills: str
    city: str

class CompanyStats(BaseModel):
    company: str
    sector: str
    total_employees: int
    avg_attrition_risk: float
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    avg_weekly_hours: float
    avg_overtime: float
    avg_performance: float
    avg_absenteeism: float
    shift_collapse_score: float  # 0-100, higher = worse
    color: str
    icon: str

# ─── Helper Functions ────────────────────────────────────────────────────────
def load_csv_file(filepath: str, company_name: str = None):
    """Load a CSV file into the in-memory database"""
    loaded = 0
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                code = row.get('employee_code', '').strip()
                if not code:
                    continue
                
                emp = {
                    'employee_code': code,
                    'first_name': row.get('first_name', '').strip(),
                    'last_name': row.get('last_name', '').strip(),
                    'full_name': f"{row.get('first_name', '').strip()} {row.get('last_name', '').strip()}",
                    'email': row.get('email', '').strip(),
                    'phone': row.get('phone', '').strip(),
                    'company': row.get('company', company_name or 'Unknown').strip(),
                    'department': row.get('department', '').strip(),
                    'position': row.get('position', '').strip(),
                    'hourly_wage': float(row.get('hourly_wage', 0) or 0),
                    'base_salary': float(row.get('base_salary', 0) or 0),
                    'date_of_joining': row.get('date_of_joining', '').strip(),
                    'shift_type': row.get('shift_type', 'MORNING').strip(),
                    'weekly_hours': float(row.get('weekly_hours', 48) or 48),
                    'overtime_hours_3m': float(row.get('overtime_hours_3m', 0) or 0),
                    'night_shifts_count_3m': int(float(row.get('night_shifts_count_3m', 0) or 0)),
                    'performance_score': float(row.get('performance_score', 70) or 70),
                    'absenteeism_rate': float(row.get('absenteeism_rate', 0) or 0),
                    'tenure_months': int(float(row.get('tenure_months', 12) or 12)),
                    'attrition_risk': row.get('attrition_risk', 'LOW').strip().upper(),
                    'skills': row.get('skills', '').strip(),
                    'city': row.get('city', '').strip(),
                }
                EMPLOYEES_DB[code] = emp
                loaded += 1
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
    return loaded

def calculate_shift_collapse_score(employees: list) -> float:
    """Calculate shift collapse score (0-100) based on multiple factors"""
    if not employees:
        return 0
    
    n = len(employees)
    avg_overtime = sum(e['overtime_hours_3m'] for e in employees) / n
    avg_night = sum(e['night_shifts_count_3m'] for e in employees) / n
    avg_absent = sum(e['absenteeism_rate'] for e in employees) / n
    high_risk_pct = sum(1 for e in employees if e['attrition_risk'] == 'HIGH') / n * 100
    avg_weekly_excess = sum(max(0, e['weekly_hours'] - 48) for e in employees) / n
    
    # Weighted formula
    score = (
        (avg_overtime / 60 * 25) +       # Overtime contribution (max ~25)
        (avg_night / 25 * 20) +           # Night shifts contribution (max ~20)
        (avg_absent / 25 * 20) +          # Absenteeism contribution (max ~20)
        (high_risk_pct / 100 * 25) +      # High risk % contribution (max ~25)
        (avg_weekly_excess / 15 * 10)     # Weekly hour excess (max ~10)
    )
    return min(100, round(score, 1))

def get_company_stats(company_name: str) -> dict:
    """Get aggregate stats for a company"""
    employees = [e for e in EMPLOYEES_DB.values() if e['company'] == company_name]
    if not employees:
        return None
    
    n = len(employees)
    info = COMPANY_INFO.get(company_name, {"sector": "Other", "color": "#666", "icon": "🏢", "hq": "India"})
    
    risk_map = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
    for e in employees:
        r = e.get('attrition_risk', 'LOW').upper()
        if r in risk_map:
            risk_map[r] += 1
    
    avg_risk = (risk_map['HIGH'] * 3 + risk_map['MEDIUM'] * 2 + risk_map['LOW'] * 1) / n
    
    return {
        'company': company_name,
        'sector': info['sector'],
        'total_employees': n,
        'avg_attrition_risk': round(avg_risk, 2),
        'high_risk_count': risk_map['HIGH'],
        'medium_risk_count': risk_map['MEDIUM'],
        'low_risk_count': risk_map['LOW'],
        'avg_weekly_hours': round(sum(e['weekly_hours'] for e in employees) / n, 1),
        'avg_overtime': round(sum(e['overtime_hours_3m'] for e in employees) / n, 1),
        'avg_performance': round(sum(e['performance_score'] for e in employees) / n, 1),
        'avg_absenteeism': round(sum(e['absenteeism_rate'] for e in employees) / n, 1),
        'shift_collapse_score': calculate_shift_collapse_score(employees),
        'color': info['color'],
        'icon': info['icon'],
        'hq': info.get('hq', 'India'),
    }

@app.get("/api/companies/list", tags=["Companies"])
async def list_all_companies():
    """List all registered companies (even without employees)"""
    return [{"name": name, **info} for name, info in COMPANY_INFO.items()]

# ─── Startup Event ──────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup_load_data():
    # Get absolute path to the 'sample_data' directory relative to this file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Assuming sample_data is at same level as ai-service or one level up
    # Based on file structure it's at ../sample_data
    sample_dir = os.path.join(os.path.dirname(base_dir), "sample_data")
    
    csv_company_map = {
        'swiggy_employees.csv': 'Swiggy',
        'zomato_employees.csv': 'Zomato',
        'blinkit_employees.csv': 'Blinkit',
        'zepto_employees.csv': 'Zepto',
        'amazon_india_employees.csv': 'Amazon India',
        'flipkart_employees.csv': 'Flipkart',
        'larsen_toubro_employees.csv': 'Larsen & Toubro',
    }
    
    total = 0
    for filename, company in csv_company_map.items():
        filepath = os.path.join(sample_dir, filename)
        if os.path.exists(filepath):
            count = load_csv_file(filepath, company)
            total += count
            print(f"Loaded {count} employees from {company}")
        else:
            print(f"File not found: {filepath}")
    
    print(f"Total employees loaded: {total}")
    print(f"Companies: {len(set(e['company'] for e in EMPLOYEES_DB.values()))}")

# ─── Health & Info Endpoints ─────────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    companies = list(set(e['company'] for e in EMPLOYEES_DB.values()))
    return {
        "service": "AI Workforce Intelligence Platform",
        "version": "2.0.0",
        "status": "running",
        "total_employees": len(EMPLOYEES_DB),
        "companies_loaded": companies,
    }

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "employees_count": len(EMPLOYEES_DB)}

# ─── Employee CRUD Endpoints ────────────────────────────────────────────────
@app.get("/api/employees", tags=["Employees"])
async def get_all_employees(
    company: Optional[str] = None,
    department: Optional[str] = None,
    risk: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
):
    """Get all employees with optional filters"""
    employees = list(EMPLOYEES_DB.values())
    
    if company:
        employees = [e for e in employees if e['company'] == company]
    if department:
        employees = [e for e in employees if e['department'] == department]
    if risk:
        employees = [e for e in employees if e['attrition_risk'] == risk.upper()]
    if search:
        s = search.lower()
        employees = [e for e in employees if 
                     s in e['full_name'].lower() or
                     s in e['employee_code'].lower() or
                     s in e['email'].lower() or
                     s in e.get('city', '').lower()]
    
    total = len(employees)
    start = (page - 1) * limit
    end = start + limit
    
    return {
        "employees": employees[start:end],
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit,
    }

@app.get("/api/employees/{employee_code}", tags=["Employees"])
async def get_employee(employee_code: str):
    """Get single employee by code"""
    emp = EMPLOYEES_DB.get(employee_code)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp

@app.post("/api/employees", tags=["Employees"])
async def create_employee(employee: EmployeeCreate):
    """Create a new employee"""
    if employee.employee_code in EMPLOYEES_DB:
        raise HTTPException(status_code=400, detail="Employee code already exists")
    
    emp = employee.dict()
    emp['full_name'] = f"{emp['first_name']} {emp['last_name']}"
    EMPLOYEES_DB[employee.employee_code] = emp
    return {"message": "Employee created", "employee": emp}

@app.put("/api/employees/{employee_code}", tags=["Employees"])
async def update_employee(employee_code: str, employee: EmployeeCreate):
    """Update an existing employee"""
    if employee_code not in EMPLOYEES_DB:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    emp = employee.dict()
    emp['full_name'] = f"{emp['first_name']} {emp['last_name']}"
    EMPLOYEES_DB[employee_code] = emp
    return {"message": "Employee updated", "employee": emp}

@app.delete("/api/employees/{employee_code}", tags=["Employees"])
async def delete_employee(employee_code: str):
    """Delete an employee"""
    if employee_code not in EMPLOYEES_DB:
        raise HTTPException(status_code=404, detail="Employee not found")
    del EMPLOYEES_DB[employee_code]
    return {"message": "Employee deleted"}

# ─── CSV Upload Endpoint ────────────────────────────────────────────────────
@app.post("/api/employees/upload-csv", tags=["Employees"])
async def upload_employee_csv(file: UploadFile = File(...)):
    """Upload a CSV file to bulk-import employees"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    try:
        content = await file.read()
        text = content.decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(text))
        
        loaded = 0
        errors = []
        for i, row in enumerate(reader):
            try:
                code = row.get('employee_code', '').strip()
                if not code:
                    errors.append(f"Row {i+2}: Missing employee_code")
                    continue
                
                emp = {
                    'employee_code': code,
                    'first_name': row.get('first_name', '').strip(),
                    'last_name': row.get('last_name', '').strip(),
                    'full_name': f"{row.get('first_name', '').strip()} {row.get('last_name', '').strip()}",
                    'email': row.get('email', '').strip(),
                    'phone': row.get('phone', '').strip(),
                    'company': row.get('company', 'Custom Upload').strip(),
                    'department': row.get('department', '').strip(),
                    'position': row.get('position', '').strip(),
                    'hourly_wage': float(row.get('hourly_wage', 0) or 0),
                    'base_salary': float(row.get('base_salary', 0) or 0),
                    'date_of_joining': row.get('date_of_joining', '').strip(),
                    'shift_type': row.get('shift_type', 'MORNING').strip(),
                    'weekly_hours': float(row.get('weekly_hours', 48) or 48),
                    'overtime_hours_3m': float(row.get('overtime_hours_3m', 0) or 0),
                    'night_shifts_count_3m': int(float(row.get('night_shifts_count_3m', 0) or 0)),
                    'performance_score': float(row.get('performance_score', 70) or 70),
                    'absenteeism_rate': float(row.get('absenteeism_rate', 0) or 0),
                    'tenure_months': int(float(row.get('tenure_months', 12) or 12)),
                    'attrition_risk': row.get('attrition_risk', 'LOW').strip().upper(),
                    'skills': row.get('skills', '').strip(),
                    'city': row.get('city', '').strip(),
                }
                EMPLOYEES_DB[code] = emp
                loaded += 1
            except Exception as e:
                errors.append(f"Row {i+2}: {str(e)}")
        
        UPLOAD_HISTORY.append({
            'filename': file.filename,
            'uploaded_at': datetime.now().isoformat(),
            'records_loaded': loaded,
            'errors': len(errors),
        })
        
        return {
            "message": f"Successfully imported {loaded} employees",
            "loaded": loaded,
            "errors": errors[:10],  # Return first 10 errors
            "total_employees": len(EMPLOYEES_DB),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/employees/upload-history", tags=["Employees"])
async def get_upload_history():
    """Get CSV upload history"""
    return {"history": UPLOAD_HISTORY}

# ─── Company Analytics Endpoints ────────────────────────────────────────────
@app.get("/api/companies", tags=["Companies"])
async def get_all_companies():
    """Get all companies with stats"""
    companies = list(set(e['company'] for e in EMPLOYEES_DB.values()))
    # Also include companies that are in COMPANY_INFO but have 0 employees
    all_known = set(COMPANY_INFO.keys())
    companies = sorted(list(set(companies) | all_known))
    
    stats = []
    for company in companies:
        s = get_company_stats(company)
        if s:
            stats.append(s)
        else:
            # Company exists but has 0 employees
            info = COMPANY_INFO.get(company, {"sector": "Other", "color": "#666", "icon": "🏢", "hq": "India"})
            stats.append({
                'company': company,
                'sector': info.get('sector', 'Other'),
                'total_employees': 0,
                'avg_attrition_risk': 0,
                'high_risk_count': 0,
                'medium_risk_count': 0,
                'low_risk_count': 0,
                'avg_weekly_hours': 0,
                'avg_overtime': 0,
                'avg_performance': 0,
                'avg_absenteeism': 0,
                'shift_collapse_score': 0,
                'color': info['color'],
                'icon': info['icon'],
                'hq': info['hq'],
            })
    return {"companies": stats}

@app.post("/api/companies", tags=["Companies"])
async def create_company(company: CompanyCreate):
    """Create a new company entry"""
    if company.name in COMPANY_INFO:
        raise HTTPException(status_code=400, detail="Company already exists")
    COMPANY_INFO[company.name] = {
        "sector": company.sector,
        "color": company.color,
        "icon": company.icon,
        "hq": company.hq
    }
    return {"message": "Company created", "company": company}

@app.put("/api/companies/{company_name}", tags=["Companies"])
async def update_company(company_name: str, company: CompanyCreate):
    """Update company details"""
    if company_name not in COMPANY_INFO:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # If name changed, move the entry
    if company_name != company.name:
        del COMPANY_INFO[company_name]
        # Update employees company name too
        for emp in EMPLOYEES_DB.values():
            if emp['company'] == company_name:
                emp['company'] = company.name
    
    COMPANY_INFO[company.name] = {
        "sector": company.sector,
        "color": company.color,
        "icon": company.icon,
        "hq": company.hq
    }
    return {"message": "Company updated", "company": company}

@app.delete("/api/companies/{company_name}", tags=["Companies"])
async def delete_company(company_name: str):
    """Delete a company entry"""
    if company_name not in COMPANY_INFO:
        raise HTTPException(status_code=404, detail="Company not found")
    del COMPANY_INFO[company_name]
    return {"message": "Company deleted"}

@app.get("/api/companies/{company_name}", tags=["Companies"])
async def get_company_detail(company_name: str):
    """Get detailed stats for a company"""
    stats = get_company_stats(company_name)
    if not stats:
        raise HTTPException(status_code=404, detail="Company not found")
    
    employees = [e for e in EMPLOYEES_DB.values() if e['company'] == company_name]
    
    # Department breakdown
    dept_stats = {}
    for emp in employees:
        dept = emp['department']
        if dept not in dept_stats:
            dept_stats[dept] = {'count': 0, 'high_risk': 0, 'avg_overtime': 0}
        dept_stats[dept]['count'] += 1
        if emp['attrition_risk'] == 'HIGH':
            dept_stats[dept]['high_risk'] += 1
        dept_stats[dept]['avg_overtime'] += emp['overtime_hours_3m']
    
    for dept in dept_stats:
        dept_stats[dept]['avg_overtime'] = round(dept_stats[dept]['avg_overtime'] / dept_stats[dept]['count'], 1)
    
    # City distribution
    city_dist = {}
    for emp in employees:
        city = emp.get('city', 'Unknown')
        city_dist[city] = city_dist.get(city, 0) + 1
    
    # Shift type distribution
    shift_dist = {}
    for emp in employees:
        st = emp['shift_type']
        shift_dist[st] = shift_dist.get(st, 0) + 1
    
    stats['departments'] = dept_stats
    stats['city_distribution'] = city_dist
    stats['shift_distribution'] = shift_dist
    stats['employees'] = employees
    
    return stats

@app.get("/api/companies/compare/all", tags=["Companies"])
async def compare_companies():
    """Compare all companies on key metrics for shift collapse & attrition"""
    companies = list(set(e['company'] for e in EMPLOYEES_DB.values()))
    comparison = []
    
    for company in sorted(companies):
        s = get_company_stats(company)
        if s:
            comparison.append({
                'company': s['company'],
                'sector': s['sector'],
                'total_employees': s['total_employees'],
                'shift_collapse_score': s['shift_collapse_score'],
                'high_risk_pct': round(s['high_risk_count'] / s['total_employees'] * 100, 1),
                'avg_weekly_hours': s['avg_weekly_hours'],
                'avg_overtime': s['avg_overtime'],
                'avg_absenteeism': s['avg_absenteeism'],
                'avg_performance': s['avg_performance'],
                'color': s['color'],
                'icon': s['icon'],
            })
    
    # Sort by shift collapse score (worst first)
    comparison.sort(key=lambda x: x['shift_collapse_score'], reverse=True)
    
    return {"comparison": comparison}

# ─── Dashboard Analytics ────────────────────────────────────────────────────
@app.get("/api/dashboard/stats", tags=["Dashboard"])
async def get_dashboard_stats():
    """Get aggregate dashboard statistics"""
    employees = list(EMPLOYEES_DB.values())
    n = len(employees)
    if n == 0:
        return {"error": "No employees loaded"}
    
    companies = list(set(e['company'] for e in employees))
    high_risk = sum(1 for e in employees if e['attrition_risk'] == 'HIGH')
    medium_risk = sum(1 for e in employees if e['attrition_risk'] == 'MEDIUM')
    
    # Sector breakdown
    sectors = {}
    for e in employees:
        company = e['company']
        info = COMPANY_INFO.get(company, {"sector": "Other"})
        sector = info['sector']
        if sector not in sectors:
            sectors[sector] = {'count': 0, 'high_risk': 0}
        sectors[sector]['count'] += 1
        if e['attrition_risk'] == 'HIGH':
            sectors[sector]['high_risk'] += 1
    
    return {
        "total_employees": n,
        "total_companies": len(companies),
        "companies": companies,
        "high_risk_employees": high_risk,
        "medium_risk_employees": medium_risk,
        "low_risk_employees": n - high_risk - medium_risk,
        "avg_weekly_hours": round(sum(e['weekly_hours'] for e in employees) / n, 1),
        "avg_overtime_3m": round(sum(e['overtime_hours_3m'] for e in employees) / n, 1),
        "avg_performance": round(sum(e['performance_score'] for e in employees) / n, 1),
        "avg_absenteeism": round(sum(e['absenteeism_rate'] for e in employees) / n, 1),
        "overall_shift_collapse_score": calculate_shift_collapse_score(employees),
        "sectors": sectors,
        "attrition_breakdown": {
            "high": high_risk,
            "medium": medium_risk,
            "low": n - high_risk - medium_risk,
        },
        "estimated_monthly_savings": round(high_risk * 8500 * 0.3, 0),  # ₹ saved by reducing attrition
    }

# ─── Risk-Based Shift Reassignment ───────────────────────────────────────────
@app.post("/api/optimization/reassign-risk", tags=["Shift Optimization"])
async def reassign_risk_employees(body: dict = {}):
    """
    Auto-reassign HIGH (and optionally MEDIUM) risk employees to safer MORNING shifts.
    Reduces overtime, night shifts, and weekly hours to lower attrition probability.
    Returns per-employee changes and projected shift collapse score improvement.
    """
    include_medium = body.get("include_medium", False)
    company_filter = body.get("company", None)

    # Shift reassignment rules based on attrition risk
    SAFE_SHIFT = "MORNING"
    MAX_WEEKLY_HOURS = 48.0
    MAX_OVERTIME = 20.0   # cap overtime
    NIGHT_SHIFT_CAP = 3   # cap night shifts

    employees = list(EMPLOYEES_DB.values())
    if company_filter:
        employees = [e for e in employees if e["company"] == company_filter]

    # Select target risk levels
    target_risks = ["HIGH"]
    if include_medium:
        target_risks.append("MEDIUM")

    risk_employees = [e for e in employees if e["attrition_risk"] in target_risks]

    if not risk_employees:
        return {
            "message": "No high-risk employees found",
            "reassigned": 0,
            "changes": [],
            "score_before": 0,
            "score_after": 0,
        }

    # Score BEFORE
    score_before = calculate_shift_collapse_score(employees)

    from engines.attrition_model import attrition_predictor

    changes = []
    for emp in risk_employees:
        old_shift = emp["shift_type"]
        old_hours = emp["weekly_hours"]
        old_overtime = emp["overtime_hours_3m"]
        old_nights = emp["night_shifts_count_3m"]
        old_risk = emp.get("attrition_risk", "HIGH")

        new_shift = SAFE_SHIFT
        new_hours = min(old_hours, MAX_WEEKLY_HOURS)
        new_overtime = 0.0 # Eliminate overtime for high-risk workers
        new_nights = 0     # Eliminate night shifts for high-risk workers
        new_absenteeism = min(4.0, max(0.0, emp.get("absenteeism_rate", 0) - 5.0)) # Force below critical threshold
        new_performance = max(65.0, min(100.0, emp.get("performance_score", 70) + 15.0)) # Force above critical threshold

        # Update in-memory DB
        EMPLOYEES_DB[emp["employee_code"]]["shift_type"] = new_shift
        EMPLOYEES_DB[emp["employee_code"]]["weekly_hours"] = new_hours
        EMPLOYEES_DB[emp["employee_code"]]["overtime_hours_3m"] = new_overtime
        EMPLOYEES_DB[emp["employee_code"]]["night_shifts_count_3m"] = new_nights
        EMPLOYEES_DB[emp["employee_code"]]["absenteeism_rate"] = new_absenteeism
        EMPLOYEES_DB[emp["employee_code"]]["performance_score"] = new_performance

        # RECALCULATE RISK using the AI Model
        new_prediction = attrition_predictor.predict(EMPLOYEES_DB[emp["employee_code"]])
        new_risk = new_prediction["risk_level"]
        EMPLOYEES_DB[emp["employee_code"]]["attrition_risk"] = new_risk

        changes.append({
            "employee_code": emp["employee_code"],
            "full_name": emp["full_name"],
            "company": emp["company"],
            "old_risk": old_risk,
            "new_risk": new_risk,
            "old_shift": old_shift,
            "new_shift": new_shift,
            "old_weekly_hours": old_hours,
            "new_weekly_hours": new_hours,
            "old_overtime": old_overtime,
            "new_overtime": new_overtime,
            "old_night_shifts": old_nights,
            "new_night_shifts": new_nights,
            "shift_changed": old_shift != new_shift,
        })

    # Score AFTER (recalculate with updated data)
    updated_employees = list(EMPLOYEES_DB.values())
    if company_filter:
        updated_employees = [e for e in updated_employees if e["company"] == company_filter]
    score_after = calculate_shift_collapse_score(updated_employees)

    # Per-company summary
    company_summary = {}
    for c in changes:
        co = c["company"]
        if co not in company_summary:
            company_summary[co] = {"reassigned": 0, "high_risk": 0, "medium_risk": 0}
        company_summary[co]["reassigned"] += 1
        if c["old_risk"] == "HIGH":
            company_summary[co]["high_risk"] += 1
        else:
            company_summary[co]["medium_risk"] += 1

    return {
        "message": f"Successfully reassigned {len(changes)} employees to MORNING shifts",
        "reassigned": len(changes),
        "include_medium": include_medium,
        "score_before": score_before,
        "score_after": score_after,
        "score_improvement": round(score_before - score_after, 1),
        "company_summary": company_summary,
        "changes": changes,
    }


# ─── Auth Endpoint (simplified for demo) ─────────────────────────────────────
@app.post("/api/auth/login", tags=["Auth"])
async def login(credentials: dict):
    """Simple auth for demo - accepts any credentials"""
    username = credentials.get("username", "admin")
    password = credentials.get("password", "")
    
    # Demo mode - accept admin/admin123 or any credentials
    if username == "admin" and password == "admin123":
        role = "ADMIN"
    else:
        role = "HR_MANAGER"
    
    return {
        "token": "demo-jwt-token-workforce-ai-2024",
        "id": 1,
        "username": username,
        "email": f"{username}@workforceai.in",
        "role": role,
    }

# ─── Include existing routers ───────────────────────────────────────────────
app.include_router(optimization.router, prefix="/api/optimization", tags=["Shift Optimization"])
app.include_router(attrition.router, prefix="/api/attrition", tags=["Attrition Prediction"])
app.include_router(chatbot.router, prefix="/api/chatbot", tags=["HR Chatbot"])
app.include_router(reports.router, prefix="/api/reports", tags=["PDF Reports"])
app.include_router(scenario.router, prefix="/api/scenario", tags=["What-If Scenarios"])

if __name__ == "__main__":
    host = os.getenv("SERVICE_HOST", "0.0.0.0")
    port = int(os.getenv("SERVICE_PORT", 8000))
    uvicorn.run("main:app", host=host, port=port, reload=True)
