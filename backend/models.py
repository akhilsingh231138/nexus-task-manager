from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="Admin")

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    admin_email = Column(String)

class ProjectMember(Base):
    __tablename__ = "project_members"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer)
    user_email = Column(String)

class PatientRecord(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(String, unique=True, index=True)
    patient_name = Column(String, index=True)
    age = Column(Float)
    bmi = Column(Float)
    risk_level = Column(String)
    details = Column(String)
    recorded_by = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    due_date = Column(String)
    priority = Column(String)
    assigned_to = Column(String)
    status = Column(String, default="To Do")    