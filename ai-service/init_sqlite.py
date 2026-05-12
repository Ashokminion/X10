"""
Initialize SQLite database for AI microservice with models and seed data.
"""
import os
from database import engine, Base, SessionLocal, Role, Department, Skill, Employee, AttritionScore
from datetime import date, datetime
import bcrypt

def seed_data():
    db = SessionLocal()
    try:
        # 1. Create Tables
        print("Creating tables in SQLite...")
        Base.metadata.create_all(bind=engine)
        
        # Check if already seeded
        if db.query(Department).first():
            print("Database already seeded.")
            return

        print("Seeding initial data...")

        # 2. Roles
        roles = [
            Role(name="ADMIN", description="System administrator with full access"),
            Role(name="HR_MANAGER", description="HR manager"),
            Role(name="OPERATIONS_MANAGER", description="Operations manager"),
            Role(name="WORKER", description="Worker")
        ]
        db.add_all(roles)
        db.commit()

        # 3. Departments
        depts = [
            Department(name="Manufacturing", description="Production and assembly operations"),
            Department(name="Healthcare", description="Nursing and patient care"),
            Department(name="Warehouse", description="Storage and logistics")
        ]
        db.add_all(depts)
        db.commit()

        # 4. Skills
        skills = [
            Skill(name="Forklift Operation", category="Warehouse"),
            Skill(name="Nursing", category="Healthcare"),
            Skill(name="Assembly", category="Manufacturing"),
            Skill(name="Machine Operation", category="Manufacturing")
        ]
        db.add_all(skills)
        db.commit()

        print("SQLite initialization complete.")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Ensure we use SQLite for this run
    os.environ["DB_TYPE"] = "sqlite"
    seed_data()
