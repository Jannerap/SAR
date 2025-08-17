from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import os
from datetime import datetime, timedelta
from typing import Optional, List
import json

from app.database import engine, Base
from app.models import *
from app.schemas_compatible import *
from app.crud import *
from app.auth import get_current_user, create_access_token, verify_password, authenticate_user
from app.reports import generate_pdf_report, generate_word_report
from app.templates import get_sar_template, get_followup_template, get_ico_escalation_template
from fastapi import UploadFile

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SAR Tracking System",
    description="Comprehensive Subject Access Request tracking and accountability system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Mount static files for uploads
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
async def root():
    return {"message": "SAR Tracking System API", "version": "1.0.0"}

# Authentication endpoints
@app.post("/auth/login")
async def login(request: Request):
    try:
        # Parse JSON body manually
        body = await request.body()
        if not body:
            raise HTTPException(status_code=400, detail="Request body is empty")
        
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON")
        
        username = data.get("username")
        password = data.get("password")
        
        if not username or not password:
            raise HTTPException(status_code=400, detail="Username and password are required")
        
        print(f"Login attempt for username: {username}")
        user = authenticate_user(username, password)
        if not user:
            print(f"Authentication failed for user: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        print(f"Authentication successful for user: {username}")
        access_token = create_access_token(data={"sub": user.username})
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@app.post("/auth/register")
async def register(user_data: UserCreate):
    return create_user(user_data)

# SAR Case endpoints
@app.post("/sar/", response_model=SARCase)
async def create_sar_case(
    sar_data: SARCreate,
    current_user: User = Depends(get_current_user)
):
    return create_sar_case_db(sar_data, current_user.id)

@app.get("/sar/", response_model=List[SARCase])
async def get_sar_cases(
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    organization: Optional[str] = None
):
    return get_sar_cases_db(current_user.id, skip, limit, status, organization)

@app.get("/sar/{sar_id}", response_model=SARCase)
async def get_sar_case(
    sar_id: int,
    current_user: User = Depends(get_current_user)
):
    sar = get_sar_case_db(sar_id, current_user.id)
    if not sar:
        raise HTTPException(status_code=404, detail="SAR case not found")
    return sar

@app.put("/sar/{sar_id}", response_model=SARCase)
async def update_sar_case(
    sar_id: int,
    sar_data: SARUpdate,
    current_user: User = Depends(get_current_user)
):
    return update_sar_case_db(sar_id, sar_data, current_user.id)

@app.delete("/sar/{sar_id}")
async def delete_sar_case(
    sar_id: int,
    current_user: User = Depends(get_current_user)
):
    return delete_sar_case_db(sar_id, current_user.id)

# Case updates and correspondence
@app.post("/sar/{sar_id}/updates/", response_model=CaseUpdate)
async def add_case_update(
    sar_id: int,
    update_data: CaseUpdateCreate,
    current_user: User = Depends(get_current_user)
):
    return create_case_update(sar_id, update_data, current_user.id)

@app.get("/sar/{sar_id}/updates/", response_model=List[CaseUpdate])
async def get_case_updates(
    sar_id: int,
    current_user: User = Depends(get_current_user)
):
    return get_case_updates_db(sar_id, current_user.id)

# File uploads
@app.post("/sar/{sar_id}/files/")
async def upload_file(
    sar_id: int,
    file: UploadFile,
    current_user: User = Depends(get_current_user)
):
    return upload_case_file(sar_id, file, current_user.id)

@app.get("/sar/{sar_id}/files/", response_model=List[CaseFile])
async def get_case_files(
    sar_id: int,
    current_user: User = Depends(get_current_user)
):
    return get_case_files_db(sar_id, current_user.id)

# ICO escalations
@app.post("/sar/{sar_id}/ico-escalation/", response_model=ICOEscalation)
async def create_ico_escalation(
    sar_id: int,
    escalation_data: ICOEscalationCreate,
    current_user: User = Depends(get_current_user)
):
    return create_ico_escalation_db(sar_id, escalation_data, current_user.id)

@app.get("/ico-escalations/", response_model=List[ICOEscalation])
async def get_ico_escalations(
    current_user: User = Depends(get_current_user)
):
    return get_ico_escalations_db(current_user.id)

# Templates
@app.get("/templates/sar")
async def get_sar_template_endpoint():
    return {"template": get_sar_template()}

@app.get("/templates/followup")
async def get_followup_template_endpoint():
    return {"template": get_followup_template()}

@app.get("/templates/ico-escalation")
async def get_ico_escalation_template_endpoint():
    return {"template": get_ico_escalation_template()}

# Reports
@app.get("/sar/{sar_id}/report/pdf")
async def generate_sar_pdf_report(
    sar_id: int,
    current_user: User = Depends(get_current_user)
):
    return generate_pdf_report(sar_id, current_user.id)

@app.get("/sar/{sar_id}/report/word")
async def generate_sar_word_report(
    sar_id: int,
    current_user: User = Depends(get_current_user)
):
    return generate_word_report(sar_id, current_user.id)

# Dashboard and analytics
@app.get("/dashboard/overview")
async def get_dashboard_overview(
    current_user: User = Depends(get_current_user)
):
    return get_dashboard_data(current_user.id)

@app.get("/dashboard/organization-performance")
async def get_organization_performance(
    current_user: User = Depends(get_current_user)
):
    return get_organization_performance_data(current_user.id)

@app.get("/dashboard/deadlines")
async def get_upcoming_deadlines(
    current_user: User = Depends(get_current_user),
    days: int = 30
):
    return get_upcoming_deadlines_data(current_user.id, days)

# Calendar and reminders
@app.get("/calendar/events")
async def get_calendar_events(
    current_user: User = Depends(get_current_user),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    return get_calendar_events_data(current_user.id, start_date, end_date)

@app.post("/reminders/set")
async def set_reminder(
    reminder_data: ReminderCreate,
    current_user: User = Depends(get_current_user)
):
    return create_reminder(reminder_data, current_user.id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
