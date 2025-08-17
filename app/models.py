from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    sar_cases = relationship("SARCase", back_populates="user")
    reminders = relationship("Reminder", back_populates="user")

class SARCase(Base):
    __tablename__ = "sar_cases"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Basic case information
    case_reference = Column(String, unique=True, index=True)
    organization_name = Column(String, nullable=False)
    organization_address = Column(String)
    organization_email = Column(String)
    organization_phone = Column(String)
    data_administrator_name = Column(String)
    data_controller_name = Column(String)
    
    # Request details
    request_type = Column(String, nullable=False)  # e.g., "Personal Data", "Special Categories", "Criminal Records"
    request_description = Column(Text)
    submission_date = Column(Date, index=True)
    submission_method = Column(String)  # e.g., "Email", "Post", "Online Form"
    
    # Deadlines
    statutory_deadline = Column(Date, index=True)  # 28 days from submission
    extended_deadline = Column(Date, nullable=True)  # If organization claims extension
    custom_deadline = Column(Date, nullable=True)  # If organization gives specific date
    
    # Status tracking
    status = Column(String, default="Pending", index=True)  # Pending, Responded, Overdue, Complete, Escalated
    response_received = Column(Boolean, default=False)
    response_date = Column(Date, nullable=True)
    
    # Response details
    response_summary = Column(Text, nullable=True)
    data_provided = Column(Boolean, nullable=True)
    data_complete = Column(Boolean, nullable=True)
    data_format = Column(String, nullable=True)  # e.g., "PDF", "Hard Copy", "CD"
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="sar_cases")
    updates = relationship("CaseUpdate", back_populates="sar_case", cascade="all, delete-orphan")
    files = relationship("CaseFile", back_populates="sar_case", cascade="all, delete-orphan")
    ico_escalations = relationship("ICOEscalation", back_populates="sar_case", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="sar_case", cascade="all, delete-orphan")

class CaseUpdate(Base):
    __tablename__ = "case_updates"
    
    id = Column(Integer, primary_key=True, index=True)
    sar_case_id = Column(Integer, ForeignKey("sar_cases.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    update_type = Column(String)  # e.g., "Note", "Correspondence", "Phone Call", "Response Received"
    title = Column(String)
    content = Column(Text)
    
    # For correspondence tracking
    correspondence_date = Column(DateTime, nullable=True)
    correspondence_method = Column(String, nullable=True)  # e.g., "Email", "Phone", "Post"
    correspondence_summary = Column(Text, nullable=True)
    
    # For phone calls
    call_duration = Column(Integer, nullable=True)  # in minutes
    call_participants = Column(String, nullable=True)
    call_transcript = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    sar_case = relationship("SARCase", back_populates="updates")
    user = relationship("User")

class CaseFile(Base):
    __tablename__ = "case_files"
    
    id = Column(Integer, primary_key=True, index=True)
    sar_case_id = Column(Integer, ForeignKey("sar_cases.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    filename = Column(String)
    original_filename = Column(String)
    file_path = Column(String)
    file_size = Column(Integer)  # in bytes
    file_type = Column(String)  # e.g., "pdf", "docx", "jpg"
    mime_type = Column(String)
    
    # File categorization
    file_category = Column(String)  # e.g., "Request", "Response", "Correspondence", "Evidence"
    description = Column(Text, nullable=True)
    
    # Timestamps
    uploaded_at = Column(DateTime, default=func.now())
    
    # Relationships
    sar_case = relationship("SARCase", back_populates="files")
    user = relationship("User")

class ICOEscalation(Base):
    __tablename__ = "ico_escalations"
    
    id = Column(Integer, primary_key=True, index=True)
    sar_case_id = Column(Integer, ForeignKey("sar_cases.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Escalation details
    escalation_date = Column(Date, index=True)
    escalation_reason = Column(Text)
    escalation_method = Column(String)  # e.g., "Online Form", "Email", "Post"
    ico_reference = Column(String, unique=True, index=True)
    
    # ICO response tracking
    ico_acknowledgment_received = Column(Boolean, default=False)
    ico_acknowledgment_date = Column(Date, nullable=True)
    ico_investigation_started = Column(Boolean, default=False)
    ico_investigation_date = Column(Date, nullable=True)
    
    # ICO deadlines
    ico_investigation_deadline = Column(Date, nullable=True)  # ICO should investigate within X time
    ico_decision_deadline = Column(Date, nullable=True)
    
    # Status
    status = Column(String, default="Submitted", index=True)  # Submitted, Under Investigation, Decision Made, Closed
    
    # Decision details
    ico_decision = Column(String, nullable=True)  # e.g., "Upheld", "Partially Upheld", "Not Upheld"
    ico_decision_date = Column(Date, nullable=True)
    ico_decision_summary = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    sar_case = relationship("SARCase", back_populates="ico_escalations")
    user = relationship("User")

class Reminder(Base):
    __tablename__ = "reminders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    sar_case_id = Column(Integer, ForeignKey("sar_cases.id"), nullable=True)
    
    title = Column(String)
    description = Column(Text)
    reminder_date = Column(DateTime, index=True)
    reminder_type = Column(String)  # e.g., "Deadline", "Follow-up", "ICO Deadline", "Custom"
    
    # Recurring reminders
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String, nullable=True)  # e.g., "Daily", "Weekly", "Monthly"
    
    # Status
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="reminders")
    sar_case = relationship("SARCase", back_populates="reminders")

class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    address = Column(Text)
    email = Column(String)
    phone = Column(String)
    website = Column(String, nullable=True)
    
    # Performance tracking
    total_sars_received = Column(Integer, default=0)
    sars_responded_on_time = Column(Integer, default=0)
    sars_responded_late = Column(Integer, default=0)
    sars_ignored = Column(Integer, default=0)
    average_response_time = Column(Float, nullable=True)  # in days
    
    # Compliance rating
    compliance_rating = Column(Float, nullable=True)  # 0-100 scale
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
