from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date
from enum import Enum

# Enums for status and types
class SARStatus(str, Enum):
    PENDING = "Pending"
    RESPONDED = "Responded"
    OVERDUE = "Overdue"
    COMPLETE = "Complete"
    ESCALATED = "Escalated"

class RequestType(str, Enum):
    personal_data = "Personal Data"
    special_categories = "Special Categories"
    criminal_records = "Criminal Records"
    foia = "FOIA"
    other = "Other"

class SubmissionMethod(str, Enum):
    EMAIL = "Email"
    POST = "Post"
    ONLINE_FORM = "Online Form"
    PHONE = "Phone"

class UpdateType(str, Enum):
    NOTE = "Note"
    CORRESPONDENCE = "Correspondence"
    PHONE_CALL = "Phone Call"
    RESPONSE_RECEIVED = "Response Received"
    DEADLINE_EXTENSION = "Deadline Extension"

class ICOStatus(str, Enum):
    SUBMITTED = "Submitted"
    UNDER_INVESTIGATION = "Under Investigation"
    DECISION_MADE = "Decision Made"
    CLOSED = "Closed"

class ReminderType(str, Enum):
    DEADLINE = "Deadline"
    FOLLOW_UP = "Follow-up"
    ICO_DEADLINE = "ICO Deadline"
    CUSTOM = "Custom"

# Base schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    full_name: str = Field(..., min_length=1, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class LoginCredentials(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# SAR Case schemas
class SARCreate(BaseModel):
    organization_name: str = Field(..., min_length=1, max_length=200)
    organization_address: Optional[str] = Field(None, max_length=500)
    organization_email: Optional[str] = Field(None, max_length=100)
    organization_phone: Optional[str] = Field(None, max_length=20)
    data_administrator_name: Optional[str] = Field(None, max_length=100)
    data_controller_name: Optional[str] = Field(None, max_length=100)
    request_type: RequestType
    request_description: str = Field(..., min_length=10)
    submission_date: date
    submission_method: SubmissionMethod
    custom_deadline: Optional[date] = None

    @validator('submission_date')
    def submission_date_cannot_be_future(cls, v):
        if v > date.today():
            raise ValueError('submission date cannot be in the future')
        return v

class SARUpdate(BaseModel):
    organization_name: Optional[str] = None
    organization_address: Optional[str] = None
    organization_email: Optional[str] = None
    organization_phone: Optional[str] = None
    request_type: Optional[RequestType] = None
    request_description: Optional[str] = None
    extended_deadline: Optional[date] = None
    custom_deadline: Optional[date] = None
    status: Optional[SARStatus] = None
    response_received: Optional[bool] = None
    response_date: Optional[date] = None
    response_summary: Optional[str] = None
    data_provided: Optional[bool] = None
    data_complete: Optional[bool] = None
    data_format: Optional[str] = None

class SARCase(BaseModel):
    id: int
    case_reference: str
    user_id: int
    organization_name: str
    organization_address: Optional[str]
    organization_email: Optional[str]
    organization_phone: Optional[str]
    request_type: str
    request_description: str
    submission_date: date
    submission_method: str
    statutory_deadline: date
    extended_deadline: Optional[date]
    custom_deadline: Optional[date]
    status: str
    response_received: bool
    response_date: Optional[date]
    response_summary: Optional[str]
    data_provided: Optional[bool]
    data_complete: Optional[bool]
    data_format: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Case Update schemas
class CaseUpdateCreate(BaseModel):
    update_type: UpdateType
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    correspondence_date: Optional[datetime] = None
    correspondence_method: Optional[str] = None
    correspondence_summary: Optional[str] = None
    call_duration: Optional[int] = Field(None, ge=0)
    call_participants: Optional[str] = None
    call_transcript: Optional[str] = None

class CaseUpdate(BaseModel):
    id: int
    sar_case_id: int
    user_id: int
    update_type: str
    title: str
    content: str
    correspondence_date: Optional[datetime]
    correspondence_method: Optional[str]
    correspondence_summary: Optional[str]
    call_duration: Optional[int]
    call_participants: Optional[str]
    call_transcript: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# File schemas
class CaseFile(BaseModel):
    id: int
    sar_case_id: int
    user_id: int
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    file_type: str
    mime_type: str
    file_category: str
    description: Optional[str]
    uploaded_at: datetime
    
    class Config:
        from_attributes = True

# ICO Escalation schemas
class ICOEscalationCreate(BaseModel):
    escalation_date: date
    escalation_reason: str = Field(..., min_length=10)
    escalation_method: str
    ico_reference: Optional[str] = None
    ico_investigation_deadline: Optional[date] = None
    ico_decision_deadline: Optional[date] = None

    @validator('escalation_date')
    def escalation_date_cannot_be_future(cls, v):
        if v > date.today():
            raise ValueError('escalation date cannot be in the future')
        return v

class ICOEscalation(BaseModel):
    id: int
    sar_case_id: int
    user_id: int
    escalation_date: date
    escalation_reason: str
    escalation_method: str
    ico_reference: Optional[str]
    ico_acknowledgment_received: bool
    ico_acknowledgment_date: Optional[date]
    ico_investigation_started: bool
    ico_investigation_date: Optional[date]
    ico_investigation_deadline: Optional[date]
    ico_decision_deadline: Optional[date]
    status: str
    ico_decision: Optional[str]
    ico_decision_date: Optional[date]
    ico_decision_summary: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Reminder schemas
class ReminderCreate(BaseModel):
    sar_case_id: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    reminder_date: datetime
    reminder_type: ReminderType
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None

    @validator('reminder_date')
    def reminder_date_cannot_be_past(cls, v):
        if v < datetime.now():
            raise ValueError('reminder date cannot be in the past')
        return v

class Reminder(BaseModel):
    id: int
    user_id: int
    sar_case_id: Optional[int]
    title: str
    description: str
    reminder_date: datetime
    reminder_type: str
    is_recurring: bool
    recurrence_pattern: Optional[str]
    is_completed: bool
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Dashboard and analytics schemas
class DashboardOverview(BaseModel):
    total_cases: int
    pending_cases: int
    overdue_cases: int
    completed_cases: int
    escalated_cases: int
    upcoming_deadlines: int
    overdue_deadlines: int

class OrganizationPerformance(BaseModel):
    organization_name: str
    total_sars: int
    responded_on_time: int
    responded_late: int
    ignored: int
    average_response_time: Optional[float]
    compliance_rating: Optional[float]

class CalendarEvent(BaseModel):
    id: int
    title: str
    description: str
    event_date: datetime
    event_type: str
    sar_case_id: Optional[int]
    is_overdue: bool

class DeadlineInfo(BaseModel):
    sar_case_id: int
    case_reference: str
    organization_name: str
    deadline_date: date
    days_remaining: int
    is_overdue: bool
    deadline_type: str

# Response schemas
class SuccessResponse(BaseModel):
    message: str
    data: Optional[dict] = None

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None

# Template schemas
class TemplateResponse(BaseModel):
    template: str
    placeholders: List[str]
    description: str
