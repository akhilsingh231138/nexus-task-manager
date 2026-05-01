from fastapi import FastAPI, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta
import uuid

from database import engine, Base, get_db
import models
from ml_service import predict, get_dataset_preview

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="NEXUS Medical System API")

SECRET_KEY = "cyberpunk_neon_secret"
ALGORITHM = "HS256"

class UserSignup(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class ProjectCreate(BaseModel):
    name: str
    description: str

class MemberAdd(BaseModel):
    user_email: str

class MLInput(BaseModel):
    features: list

class PatientRecordCreate(BaseModel):
    patient_name: str
    age: float
    bmi: float
    risk_level: str
    details: str
    recorded_by: str

def create_access_token(data: dict):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + timedelta(hours=1)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Token missing")
    try:
        token = authorization.split(" ")[1]
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/signup")
def signup(user: UserSignup, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Entity exists")
    db.add(models.User(name=user.name, email=user.email, password=user.password, role="Admin"))
    db.commit()
    return {"message": "Registered successfully"}

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or db_user.password != user.password:
        raise HTTPException(status_code=400, detail="Access Denied")
    token = create_access_token({"sub": db_user.email, "role": db_user.role, "name": db_user.name})
    return {"access_token": token, "token_type": "bearer", "role": db_user.role}

@app.post("/projects")
def create_project(project: ProjectCreate, user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    if user.get("role") != "Admin":
        raise HTTPException(status_code=403, detail="Admins only.")
    new_proj = models.Project(name=project.name, description=project.description, admin_email=user["sub"])
    db.add(new_proj)
    db.commit()
    db.refresh(new_proj)
    db.add(models.ProjectMember(project_id=new_proj.id, user_email=user["sub"]))
    db.commit()
    return {"message": "Project created", "id": new_proj.id}

@app.get("/projects")
def get_projects(user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    if user.get("role") == "Admin":
        return db.query(models.Project).all()
    member_links = db.query(models.ProjectMember).filter(models.ProjectMember.user_email == user["sub"]).all()
    return db.query(models.Project).filter(models.Project.id.in_([l.project_id for l in member_links])).all()

@app.post("/projects/{project_id}/members")
def add_member(project_id: int, member: MemberAdd, user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    if user.get("role") != "Admin":
        raise HTTPException(status_code=403, detail="Admins only.")
    if db.query(models.ProjectMember).filter(models.ProjectMember.project_id == project_id, models.ProjectMember.user_email == member.user_email).first():
        raise HTTPException(status_code=400, detail="Already a member.")
    db.add(models.ProjectMember(project_id=project_id, user_email=member.user_email))
    db.commit()
    return {"message": "Member added"}

@app.post("/patients")
def save_patient(record: PatientRecordCreate, user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    new_record = models.PatientRecord(record_id=f"PT-{str(uuid.uuid4())[:8].upper()}", **record.dict())
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return {"message": "Saved", "id": new_record.record_id}

@app.get("/patients")
def get_patients(name: str = None, risk: str = "All", user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    query = db.query(models.PatientRecord)
    if name:
        query = query.filter(models.PatientRecord.patient_name.ilike(f"%{name}%"))
    if risk != "All":
        query = query.filter(models.PatientRecord.risk_level == risk)
    return query.all()

@app.get("/ml/preview")
def preview_data(user: dict = Depends(verify_token)):
    return get_dataset_preview()

@app.post("/ml/predict")
def run_prediction(data: MLInput, user: dict = Depends(verify_token)):
    return predict(data.features)

class TaskCreate(BaseModel):
    title: str
    description: str
    due_date: str
    priority: str
    assigned_to: str
    status: str = "To Do" 
@app.post("/tasks")
def create_task(task: TaskCreate, user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    if user.get("role") != "Admin":
        raise HTTPException(status_code=403, detail="Admins only.")
    new_task = models.Task(**task.dict())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return {"message": "Task created", "id": new_task.id}

@app.get("/tasks")
def get_tasks(user: dict = Depends(verify_token), db: Session = Depends(get_db)): 
    if user.get("role") == "Admin":
        return db.query(models.Task).all()
    return db.query(models.Task).filter(models.Task.assigned_to == user["sub"]).all()

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    if user.get("role") != "Admin":
        raise HTTPException(status_code=403, detail="Admins only.")
    
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    db.delete(task)
    db.commit()
    return {"message": "Task deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)