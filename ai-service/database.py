"""
Database connection and models for AI microservice
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, Boolean, ForeignKey, Enum, DECIMAL, Text, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DB_TYPE = os.getenv("DB_TYPE", "mysql")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
DB_NAME = os.getenv("DB_NAME", "workforce_optimization")

if DB_TYPE == "sqlite":
    DATABASE_URL = "sqlite:///./workforce.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# SQLAlchemy Models (simplified for AI service needs)
class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))

class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_code = Column(String(50), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    hourly_wage = Column(DECIMAL(10, 2), nullable=False)
    base_salary = Column(DECIMAL(12, 2), nullable=False)
    overtime_rate = Column(DECIMAL(5, 2), default=1.5)
    night_shift_allowance = Column(DECIMAL(8, 2), default=0)
    is_available = Column(Boolean, default=True)
    max_weekly_hours = Column(Integer, default=48)

class Shift(Base):
    __tablename__ = "shifts"
    
    id = Column(Integer, primary_key=True, index=True)
    shift_code = Column(String(50), unique=True, nullable=False)
    shift_name = Column(String(100), nullable=False)
    shift_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    shift_type = Column(String(20), nullable=False)  # MORNING, AFTERNOON, NIGHT
    required_workers = Column(Integer, default=1)
    required_skill_id = Column(Integer, ForeignKey("skills.id"))
    department_id = Column(Integer, ForeignKey("departments.id"))
    status = Column(String(20), default="PLANNED")

class ShiftAssignment(Base):
    __tablename__ = "shift_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=False)
    assignment_type = Column(String(20), default="OPTIMIZED")
    duration_hours = Column(DECIMAL(5, 2))
    status = Column(String(20), default="ASSIGNED")

class AttritionScore(Base):
    __tablename__ = "attrition_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    prediction_date = Column(Date, nullable=False)
    risk_score = Column(DECIMAL(5, 4), nullable=False)
    risk_level = Column(String(10), nullable=False)  # LOW, MEDIUM, HIGH
    overtime_hours_3m = Column(DECIMAL(8, 2))
    night_shifts_count_3m = Column(Integer)
    performance_score = Column(DECIMAL(5, 2))
    absenteeism_rate = Column(DECIMAL(5, 2))
    tenure_months = Column(Integer)
    model_version = Column(String(50))

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message_type = Column(String(10), nullable=False)  # USER, BOT
    message_text = Column(Text, nullable=False)
    intent_detected = Column(String(100))
    response_time_ms = Column(Integer)
    created_at = Column(DateTime)

class Department(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)

class Skill(Base):
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(50))
