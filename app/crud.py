from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional
from datetime import datetime, date, timedelta
import uuid
import os
from app.database import SessionLocal
from app.models import (
    User, SARCase, CaseUpdate, CaseFile, ICOEscalation, 
    Reminder, Organization
)
from app.schemas_compatible import (
    SARCreate, SARUpdate, CaseUpdateCreate, ICOEscalationCreate,
    ReminderCreate
)

# SAR Case CRUD operations
def create_sar_case_db(sar_data: SARCreate, user_id: int) -> SARCase:
    """Create a new SAR case."""
    db = SessionLocal()
    
    # Generate case reference
    case_reference = f"SAR-{datetime.now().strftime('%Y%m')}-{uuid.uuid4().hex[:8].upper()}"
    
    # Calculate statutory deadline based on request type
    if sar_data.request_type.value == "FOIA":
        # FOIA requests have 20 working days deadline
        statutory_deadline = sar_data.submission_date + timedelta(days=20)
    else:
        # SAR requests have 28 days deadline
        statutory_deadline = sar_data.submission_date + timedelta(days=28)
    
    # Create SAR case
    db_sar = SARCase(
        user_id=user_id,
        case_reference=case_reference,
        organization_name=sar_data.organization_name,
        organization_address=sar_data.organization_address,
        organization_email=sar_data.organization_email,
        organization_phone=sar_data.organization_phone,
        data_administrator_name=sar_data.data_administrator_name,
        data_controller_name=sar_data.data_controller_name,
        request_type=sar_data.request_type.value,
        request_description=sar_data.request_description,
        submission_date=sar_data.submission_date,
        submission_method=sar_data.submission_method.value,
        statutory_deadline=statutory_deadline,
        custom_deadline=sar_data.custom_deadline
    )
    
    db.add(db_sar)
    db.commit()
    db.refresh(db_sar)
    
    # Create automatic reminder for deadline
    create_deadline_reminder(db_sar.id, user_id, statutory_deadline)
    
    return db_sar

def get_sar_cases_db(
    user_id: int, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[str] = None,
    organization: Optional[str] = None
) -> List[SARCase]:
    """Get SAR cases for a user with optional filtering."""
    db = SessionLocal()
    
    query = db.query(SARCase).filter(SARCase.user_id == user_id)
    
    if status:
        query = query.filter(SARCase.status == status)
    
    if organization:
        query = query.filter(SARCase.organization_name.ilike(f"%{organization}%"))
    
    return query.offset(skip).limit(limit).all()

def get_sar_case_db(sar_id: int, user_id: int) -> Optional[SARCase]:
    """Get a specific SAR case by ID."""
    db = SessionLocal()
    return db.query(SARCase).filter(
        and_(SARCase.id == sar_id, SARCase.user_id == user_id)
    ).first()

def update_sar_case_db(sar_id: int, sar_data: SARUpdate, user_id: int) -> Optional[SARCase]:
    """Update a SAR case."""
    db = SessionLocal()
    sar_case = get_sar_case_db(sar_id, user_id)
    
    if not sar_case:
        return None
    
    # Update fields
    update_data = sar_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sar_case, field, value)
    
    # Update status based on response received
    if sar_data.response_received:
        sar_case.status = "Responded"
    
    # Check if overdue
    current_date = date.today()
    deadline = sar_case.extended_deadline or sar_case.custom_deadline or sar_case.statutory_deadline
    
    if current_date > deadline and sar_case.status == "Pending":
        sar_case.status = "Overdue"
    
    sar_case.updated_at = datetime.now()
    db.commit()
    db.refresh(sar_case)
    
    return sar_case

def update_sar_case_simple_db(sar_id: int, sar_data, user_id: int) -> Optional[SARCase]:
    """Update a SAR case with simplified data object."""
    db = SessionLocal()
    try:
        # Get the SAR case within the same session
        sar_case = db.query(SARCase).filter(
            and_(SARCase.id == sar_id, SARCase.user_id == user_id)
        ).first()
        
        if not sar_case:
            return None
        
        # Update fields directly from the generic object
        if hasattr(sar_data, 'organization_name'):
            sar_case.organization_name = sar_data.organization_name
        if hasattr(sar_data, 'organization_email'):
            sar_case.organization_email = sar_data.organization_email
        if hasattr(sar_data, 'organization_phone'):
            sar_case.organization_phone = sar_data.organization_phone
        if hasattr(sar_data, 'organization_address'):
            sar_case.organization_address = sar_data.organization_address
        if hasattr(sar_data, 'data_administrator_name'):
            sar_case.data_administrator_name = sar_data.data_administrator_name
        if hasattr(sar_data, 'data_controller_name'):
            sar_case.data_controller_name = sar_data.data_controller_name
        if hasattr(sar_data, 'request_description'):
            sar_case.request_description = sar_data.request_description
        if hasattr(sar_data, 'custom_deadline'):
            sar_case.custom_deadline = sar_data.custom_deadline
        
        # Update status based on deadlines
        current_date = date.today()
        deadline = sar_case.extended_deadline or sar_case.custom_deadline or sar_case.statutory_deadline
        
        if deadline and current_date > deadline and sar_case.status == "Pending":
            sar_case.status = "Overdue"
        
        sar_case.updated_at = datetime.now()
        db.commit()
        db.refresh(sar_case)
        
        return sar_case
    finally:
        db.close()

def delete_sar_case_db(sar_id: int, user_id: int) -> bool:
    """Delete a SAR case."""
    db = SessionLocal()
    try:
        # Get the SAR case within the same session
        sar_case = db.query(SARCase).filter(
            and_(SARCase.id == sar_id, SARCase.user_id == user_id)
        ).first()
        
        if not sar_case:
            return False
        
        db.delete(sar_case)
        db.commit()
        return True
    finally:
        db.close()

# Case Update CRUD operations
def create_case_update(sar_id: int, update_data: CaseUpdateCreate, user_id: int) -> CaseUpdate:
    """Create a case update."""
    db = SessionLocal()
    
    # Verify SAR case exists and belongs to user
    sar_case = get_sar_case_db(sar_id, user_id)
    if not sar_case:
        raise ValueError("SAR case not found")
    
    db_update = CaseUpdate(
        sar_case_id=sar_id,
        user_id=user_id,
        update_type=update_data.update_type.value,
        title=update_data.title,
        content=update_data.content,
        correspondence_date=update_data.correspondence_date,
        correspondence_method=update_data.correspondence_method,
        correspondence_summary=update_data.correspondence_summary,
        call_duration=update_data.call_duration,
        call_participants=update_data.call_participants,
        call_transcript=update_data.call_transcript
    )
    
    db.add(db_update)
    db.commit()
    db.refresh(db_update)
    
    return db_update

def get_case_updates_db(sar_id: int, user_id: int) -> List[CaseUpdate]:
    """Get case updates for a SAR case."""
    db = SessionLocal()
    
    # Verify SAR case belongs to user
    sar_case = get_sar_case_db(sar_id, user_id)
    if not sar_case:
        return []
    
    return db.query(CaseUpdate).filter(
        CaseUpdate.sar_case_id == sar_id
    ).order_by(desc(CaseUpdate.created_at)).all()

# File upload CRUD operations
def upload_case_file(sar_id: int, file, user_id: int) -> CaseFile:
    """Upload a file for a SAR case."""
    db = SessionLocal()
    
    # Verify SAR case exists and belongs to user
    sar_case = get_sar_case_db(sar_id, user_id)
    if not sar_case:
        raise ValueError("SAR case not found")
    
    # Create uploads directory if it doesn't exist
    upload_dir = f"uploads/sar_{sar_id}"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4().hex}{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        content = file.file.read()
        buffer.write(content)
    
    # Create file record
    db_file = CaseFile(
        sar_case_id=sar_id,
        user_id=user_id,
        filename=unique_filename,
        original_filename=file.filename,
        file_path=file_path,
        file_size=len(content),
        file_type=file_extension[1:].lower(),
        mime_type=file.content_type,
        file_category="Correspondence"  # Default category
    )
    
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    
    return db_file

def get_case_files_db(sar_id: int, user_id: int) -> List[CaseFile]:
    """Get files for a SAR case."""
    db = SessionLocal()
    
    # Verify SAR case belongs to user
    sar_case = get_sar_case_db(sar_id, user_id)
    if not sar_case:
        return []
    
    return db.query(CaseFile).filter(
        CaseFile.sar_case_id == sar_id
    ).order_by(desc(CaseFile.uploaded_at)).all()

# ICO Escalation CRUD operations
def create_ico_escalation_db(sar_id: int, escalation_data: ICOEscalationCreate, user_id: int) -> ICOEscalation:
    """Create an ICO escalation."""
    db = SessionLocal()
    
    # Verify SAR case exists and belongs to user
    sar_case = get_sar_case_db(sar_id, user_id)
    if not sar_case:
        raise ValueError("SAR case not found")
    
    # Generate ICO reference if not provided
    if not escalation_data.ico_reference:
        escalation_data.ico_reference = f"ICO-{datetime.now().strftime('%Y%m')}-{uuid.uuid4().hex[:8].upper()}"
    
    db_escalation = ICOEscalation(
        sar_case_id=sar_id,
        user_id=user_id,
        escalation_date=escalation_data.escalation_date,
        escalation_reason=escalation_data.escalation_reason,
        escalation_method=escalation_data.escalation_method,
        ico_reference=escalation_data.ico_reference,
        ico_investigation_deadline=escalation_data.ico_investigation_deadline,
        ico_decision_deadline=escalation_data.ico_decision_deadline
    )
    
    db.add(db_escalation)
    db.commit()
    db.refresh(db_escalation)
    
    # Update SAR case status to escalated
    sar_case.status = "Escalated"
    db.commit()
    
    # Create reminder for ICO investigation deadline if provided
    if escalation_data.ico_investigation_deadline:
        create_ico_deadline_reminder(sar_id, user_id, escalation_data.ico_investigation_deadline)
    
    return db_escalation

def get_ico_escalations_db(user_id: int) -> List[ICOEscalation]:
    """Get ICO escalations for a user."""
    db = SessionLocal()
    return db.query(ICOEscalation).filter(
        ICOEscalation.user_id == user_id
    ).order_by(desc(ICOEscalation.created_at)).all()

# Reminder CRUD operations
def create_reminder(reminder_data: ReminderCreate, user_id: int) -> Reminder:
    """Create a reminder."""
    db = SessionLocal()
    
    db_reminder = Reminder(
        user_id=user_id,
        sar_case_id=reminder_data.sar_case_id,
        title=reminder_data.title,
        description=reminder_data.description,
        reminder_date=reminder_data.reminder_date,
        reminder_type=reminder_data.reminder_type.value,
        is_recurring=reminder_data.is_recurring,
        recurrence_pattern=reminder_data.recurrence_pattern
    )
    
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    
    return db_reminder

def create_deadline_reminder(sar_id: int, user_id: int, deadline_date: date):
    """Create an automatic deadline reminder."""
    # Ensure reminder date is in the future
    current_date = date.today()
    if deadline_date <= current_date:
        # If deadline is in the past, set reminder to tomorrow
        reminder_date = datetime.combine(current_date + timedelta(days=1), datetime.min.time())
    else:
        # Set reminder to 1 day before deadline
        reminder_date = datetime.combine(deadline_date, datetime.min.time()) - timedelta(days=1)
    
    reminder_data = ReminderCreate(
        sar_case_id=sar_id,
        title=f"Deadline Reminder - SAR Case",
        description=f"Deadline for SAR case is tomorrow ({deadline_date})",
        reminder_date=reminder_date,
        reminder_type="Deadline"
    )
    
    return create_reminder(reminder_data, user_id)

def create_ico_deadline_reminder(sar_id: int, user_id: int, deadline_date: date):
    """Create an automatic ICO deadline reminder."""
    reminder_date = datetime.combine(deadline_date, datetime.min.time()) - timedelta(days=7)
    
    reminder_data = ReminderCreate(
        sar_case_id=sar_id,
        title=f"ICO Investigation Deadline Reminder",
        description=f"ICO investigation deadline is in 7 days ({deadline_date})",
        reminder_date=reminder_date,
        reminder_type="ICO Deadline"
    )
    
    return create_reminder(reminder_data, user_id)

# Dashboard and analytics functions
def get_dashboard_data(user_id: int) -> dict:
    """Get dashboard overview data."""
    db = SessionLocal()
    try:
        # Get case counts
        total_cases = db.query(SARCase).filter(SARCase.user_id == user_id).count()
        pending_cases = db.query(SARCase).filter(
            and_(SARCase.user_id == user_id, SARCase.status == "Pending")
        ).count()
        overdue_cases = db.query(SARCase).filter(
            and_(SARCase.user_id == user_id, SARCase.status == "Overdue")
        ).count()
        completed_cases = db.query(SARCase).filter(
            and_(SARCase.user_id == user_id, SARCase.status == "Complete")
        ).count()
        escalated_cases = db.query(SARCase).filter(
            and_(SARCase.user_id == user_id, SARCase.status == "Escalated")
        ).count()
        
        # Get deadline counts
        current_date = date.today()
        upcoming_deadlines = db.query(SARCase).filter(
            and_(
                SARCase.user_id == user_id,
                SARCase.status.in_(["Pending", "Overdue"]),
                or_(
                    SARCase.statutory_deadline >= current_date,
                    SARCase.extended_deadline >= current_date,
                    SARCase.custom_deadline >= current_date
                )
            )
        ).count()
        
        overdue_deadlines = db.query(SARCase).filter(
            and_(
                SARCase.user_id == user_id,
                SARCase.status.in_(["Pending", "Overdue"]),
                or_(
                    SARCase.statutory_deadline < current_date,
                    SARCase.extended_deadline < current_date,
                    SARCase.custom_deadline < current_date
                )
            )
        ).count()
        
        return {
            "total_cases": total_cases,
            "pending_cases": pending_cases,
            "overdue_cases": overdue_cases,
            "completed_cases": completed_cases,
            "escalated_cases": escalated_cases,
            "upcoming_deadlines": upcoming_deadlines,
            "overdue_deadlines": overdue_deadlines
        }
    finally:
        db.close()

def get_organization_performance_data(user_id: int) -> List[dict]:
    """Get organization performance data."""
    db = SessionLocal()
    try:
        # Get all organizations for the user
        organizations = db.query(SARCase.organization_name).filter(
            SARCase.user_id == user_id
        ).distinct().all()
        
        performance_data = []
        
        for org in organizations:
            org_name = org[0]
            
            # Get case counts for this organization
            total_sars = db.query(SARCase).filter(
                and_(SARCase.user_id == user_id, SARCase.organization_name == org_name)
            ).count()
            
            responded_on_time = db.query(SARCase).filter(
                and_(
                    SARCase.user_id == user_id,
                    SARCase.organization_name == org_name,
                    SARCase.response_received == True,
                    SARCase.response_date <= SARCase.statutory_deadline
                )
            ).count()
            
            responded_late = db.query(SARCase).filter(
                and_(
                    SARCase.user_id == user_id,
                    SARCase.organization_name == org_name,
                    SARCase.response_received == True,
                    SARCase.response_date > SARCase.statutory_deadline
                )
            ).count()
            
            ignored = db.query(SARCase).filter(
                and_(
                    SARCase.user_id == user_id,
                    SARCase.organization_name == org_name,
                    SARCase.response_received == False,
                    SARCase.statutory_deadline < date.today()
                )
            ).count()
            
            # Calculate average response time
            response_times = db.query(
                func.extract('day', SARCase.response_date - SARCase.submission_date)
            ).filter(
                and_(
                    SARCase.user_id == user_id,
                    SARCase.organization_name == org_name,
                    SARCase.response_received == True,
                    SARCase.response_date.isnot(None)
                )
            ).all()
            
            avg_response_time = None
            if response_times:
                avg_response_time = sum(rt[0] for rt in response_times if rt[0] is not None) / len(response_times)
            
            # Calculate compliance rating
            total_responded = responded_on_time + responded_late
            compliance_rating = None
            if total_sars > 0:
                compliance_rating = (responded_on_time / total_sars) * 100
            
            performance_data.append({
                "organization_name": org_name,
                "total_sars": total_sars,
                "responded_on_time": responded_on_time,
                "responded_late": responded_late,
                "ignored": ignored,
                "average_response_time": avg_response_time,
                "compliance_rating": compliance_rating
            })
        
        return performance_data
    finally:
        db.close()

def get_upcoming_deadlines_data(user_id: int, days: int = 30) -> List[dict]:
    """Get upcoming deadlines within specified days."""
    db = SessionLocal()
    try:
        current_date = date.today()
        
        # Get all pending/overdue cases with deadlines
        deadlines = db.query(SARCase).filter(
            and_(
                SARCase.user_id == user_id,
                SARCase.status.in_(["Pending", "Overdue"])
            )
        ).all()
        
        deadline_data = []
        for deadline in deadlines:
            # Determine which deadline to use
            actual_deadline = deadline.custom_deadline or deadline.extended_deadline or deadline.statutory_deadline
            if actual_deadline:
                days_remaining = (actual_deadline - current_date).days
                is_overdue = days_remaining < 0
                
                # Only include if within the specified range or if overdue
                if days_remaining <= days or is_overdue:
                    deadline_data.append({
                        "sar_case_id": deadline.id,
                        "case_reference": deadline.case_reference,
                        "organization_name": deadline.organization_name,
                        "deadline_date": actual_deadline.isoformat(),
                        "days_remaining": days_remaining,
                        "is_overdue": is_overdue,
                        "deadline_type": "Custom" if deadline.custom_deadline else "Extended" if deadline.extended_deadline else "Statutory"
                    })
        
        # Sort by deadline date (earliest first)
        deadline_data.sort(key=lambda x: x["deadline_date"])
        return deadline_data
    finally:
        db.close()

def get_calendar_events_data(user_id: int, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[dict]:
    """Get calendar events for a date range."""
    db = SessionLocal()
    
    # Parse date parameters
    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    else:
        start_date = date.today()
    
    if end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    else:
        end_date = start_date + timedelta(days=30)
    
    events = []
    
    # Get SAR case deadlines
    cases = db.query(SARCase).filter(
        and_(
            SARCase.user_id == user_id,
            SARCase.status.in_(["Pending", "Overdue"]),
            or_(
                and_(SARCase.statutory_deadline >= start_date, SARCase.statutory_deadline <= end_date),
                and_(SARCase.extended_deadline >= start_date, SARCase.extended_deadline <= end_date),
                and_(SARCase.custom_deadline >= start_date, SARCase.custom_deadline <= end_date)
            )
        )
    ).all()
    
    for case in cases:
        deadline_date = case.custom_deadline or case.extended_deadline or case.statutory_deadline
        deadline_type = "Custom" if case.custom_deadline else "Extended" if case.extended_deadline else "Statutory"
        
        events.append({
            "id": f"deadline_{case.id}",
            "title": f"Deadline: {case.case_reference}",
            "description": f"{deadline_type} deadline for {case.organization_name}",
            "event_date": datetime.combine(deadline_date, datetime.min.time()),
            "event_type": "Deadline",
            "sar_case_id": case.id,
            "is_overdue": deadline_date < date.today()
        })
    
    # Get SAR case creation dates
    creation_cases = db.query(SARCase).filter(
        and_(
            SARCase.user_id == user_id,
            SARCase.submission_date >= start_date,
            SARCase.submission_date <= end_date
        )
    ).all()
    
    for case in creation_cases:
        events.append({
            "id": f"creation_{case.id}",
            "title": f"SAR Created: {case.case_reference}",
            "description": f"SAR case submitted for {case.organization_name}",
            "event_date": datetime.combine(case.submission_date, datetime.min.time()),
            "event_type": "Case Creation",
            "sar_case_id": case.id,
            "is_overdue": False
        })
    
    # Get reminders
    reminders = db.query(Reminder).filter(
        and_(
            Reminder.user_id == user_id,
            Reminder.reminder_date >= datetime.combine(start_date, datetime.min.time()),
            Reminder.reminder_date <= datetime.combine(end_date, datetime.max.time()),
            Reminder.is_completed == False
        )
    ).all()
    
    for reminder in reminders:
        events.append({
            "id": f"reminder_{reminder.id}",
            "title": f"Reminder: {reminder.title}",
            "description": reminder.description,
            "event_date": reminder.reminder_date,
            "event_type": "Reminder",
            "sar_case_id": reminder.sar_case_id,
            "is_overdue": reminder.reminder_date < datetime.now()
        })
    
    # Sort events by date
    events.sort(key=lambda x: x["event_date"])
    
    return events
