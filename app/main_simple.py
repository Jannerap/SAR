from fastapi import FastAPI, Depends, HTTPException, status, Form, Request, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import os
from datetime import datetime, timedelta, date
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
from fastapi.responses import Response

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
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:8000",
        "https://jannerap.github.io",
        "https://jannerap.github.io/SAR"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Mount static files for uploads
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway deployment."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Add this function for debugging
async def get_current_user_debug(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Get the current authenticated user from JWT token with debugging."""
    print(f"DEBUG: Received credentials: {credentials}")
    print(f"DEBUG: Token: {credentials.credentials}")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(credentials.credentials)
        print(f"DEBUG: Token payload: {payload}")
        if payload is None:
            print("DEBUG: Token verification failed")
            raise credentials_exception
        username: str = payload.get("sub")
        if username is None:
            print("DEBUG: No username in token")
            raise credentials_exception
        print(f"DEBUG: Username from token: {username}")
    except Exception as e:
        print(f"DEBUG: Exception in token verification: {e}")
        raise credentials_exception
    
    # Get user from database
    db = next(get_db())
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        print(f"DEBUG: User not found in database: {username}")
        raise credentials_exception
    
    print(f"DEBUG: User authenticated successfully: {user.username}")
    return user

async def get_current_user_custom(request: Request) -> User:
    """Custom authentication dependency that manually extracts the Authorization header."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Extract Authorization header manually
        auth_header = request.headers.get("Authorization")
        print(f"DEBUG: Auth header: {auth_header}")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            print("DEBUG: No Bearer token in Authorization header")
            raise credentials_exception
        
        token = auth_header.split(" ")[1]
        print(f"DEBUG: Extracted token: {token[:20]}...")
        
        # Verify token
        payload = verify_token(token)
        if payload is None:
            print("DEBUG: Token verification failed")
            raise credentials_exception
        
        username: str = payload.get("sub")
        if username is None:
            print("DEBUG: No username in token")
            raise credentials_exception
        
        print(f"DEBUG: Username from token: {username}")
        
        # Get user from database - fix the session management
        from app.database import SessionLocal
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == username).first()
            if user is None:
                print(f"DEBUG: User not found in database: {username}")
                raise credentials_exception
            
            print(f"DEBUG: User authenticated successfully: {user.username}")
            return user
        finally:
            db.close()
        
    except Exception as e:
        print(f"DEBUG: Exception in custom auth: {e}")
        raise credentials_exception

async def get_mock_user() -> User:
    """Mock authentication dependency for testing."""
    print("DEBUG: Mock user dependency called")
    return User(
        id=1,
        username="admin",
        email="admin@sartracker.com",
        full_name="System Administrator",
        hashed_password="",
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

async def get_current_user_simple(request: Request) -> User:
    """Simple authentication dependency that manually extracts and verifies JWT tokens."""
    try:
        # Extract Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid Authorization header"
            )
        
        token = auth_header.split(" ")[1]
        
        # Verify token using the working function
        from app.auth import verify_token
        payload = verify_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        username = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Get user from database
        from app.database import SessionLocal
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == username).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            return user
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )

@app.get("/")
async def root():
    return {"message": "SAR Tracking System API", "version": "1.0.0"}

# Authentication endpoints
@app.post("/auth/login")
async def login(request: Request):
    """Login endpoint."""
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
        return {"access_token": access_token, "user": user}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@app.post("/auth/register")
async def register(
    username: str = Form(...),
    email: str = Form(...),
    full_name: str = Form(...),
    password: str = Form(...)
):
    user_data = type('obj', (object,), {
        'username': username,
        'email': email,
        'full_name': full_name,
        'password': password
    })()
    return create_user(user_data)

@app.get("/auth/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information."""
    return current_user

@app.get("/test-token")
async def test_token(token: str):
    """Test endpoint to manually verify JWT tokens."""
    try:
        from app.auth import verify_token
        payload = verify_token(token)
        if payload:
            return {"valid": True, "payload": payload}
        else:
            return {"valid": False, "error": "Token verification failed"}
    except Exception as e:
        return {"valid": False, "error": str(e)}

@app.get("/test-auth")
async def test_auth(request: Request):
    """Test endpoint that only verifies JWT token without database access."""
    try:
        # Extract Authorization header manually
        auth_header = request.headers.get("Authorization")
        print(f"DEBUG: Auth header: {auth_header}")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            return {"error": "No Bearer token in Authorization header"}
        
        token = auth_header.split(" ")[1]
        print(f"DEBUG: Extracted token: {token[:20]}...")
        
        # Verify token
        from app.auth import verify_token
        payload = verify_token(token)
        if payload is None:
            return {"error": "Token verification failed"}
        
        return {"success": True, "payload": payload}
        
    except Exception as e:
        print(f"DEBUG: Exception in test auth: {e}")
        return {"error": str(e)}

@app.get("/test-headers")
async def test_headers(request: Request):
    """Test endpoint to see all headers received."""
    headers = dict(request.headers)
    return {
        "headers": headers,
        "authorization": request.headers.get("Authorization"),
        "user_agent": request.headers.get("User-Agent")
    }

@app.get("/test-db")
async def test_database():
    """Test endpoint to check database connection and User table."""
    try:
        from app.database import SessionLocal
        from app.models import User
        
        db = SessionLocal()
        try:
            # Check if User table exists and has data
            users = db.query(User).all()
            user_count = len(users)
            
            # Get first user if exists
            first_user = db.query(User).first()
            if first_user:
                user_info = {
                    "id": first_user.id,
                    "username": first_user.username,
                    "email": first_user.email,
                    "full_name": first_user.full_name
                }
            else:
                user_info = None
            
            return {
                "success": True,
                "user_count": user_count,
                "first_user": user_info
            }
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"DEBUG: Database test error: {e}")
        return {"error": str(e)}

@app.get("/test-jwt")
async def test_jwt():
    """Test endpoint to verify JWT creation and verification process."""
    try:
        from app.auth import create_access_token, verify_token, SECRET_KEY
        
        # Create a test token
        test_data = {"sub": "testuser", "test": "data"}
        token = create_access_token(test_data)
        
        # Verify the token
        payload = verify_token(token)
        
        return {
            "success": True,
            "secret_key": SECRET_KEY,
            "created_token": token,
            "verified_payload": payload,
            "token_length": len(token)
        }
        
    except Exception as e:
        print(f"DEBUG: JWT test error: {e}")
        return {"error": str(e)}

# SAR Case endpoints
@app.post("/sar/")
async def create_sar_case(request: Request, current_user: User = Depends(get_current_user)):
    try:
        # Parse JSON body manually
        body = await request.body()
        if not body:
            raise HTTPException(status_code=400, detail="Request body is empty")
        
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON")
        
        # Extract required fields
        organization_name = data.get("organization_name")
        request_type = data.get("request_type")
        request_description = data.get("request_description")
        submission_date = data.get("submission_date")
        submission_method = data.get("submission_method")
        custom_deadline = data.get("custom_deadline")
        
        # Validate required fields
        if not all([organization_name, request_type, request_description, submission_date, submission_method]):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Parse date strings
        try:
            submission_date_parsed = datetime.strptime(submission_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid submission date format")
        
        custom_deadline_parsed = None
        if custom_deadline:
            try:
                custom_deadline_parsed = datetime.strptime(custom_deadline, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid custom deadline format")
        
        # Create SAR data object
        sar_data = type('obj', (object,), {
            'organization_name': organization_name,
            'organization_address': data.get("organization_address", ""),
            'organization_email': data.get("organization_email", ""),
            'organization_phone': data.get("organization_phone", ""),
            'data_administrator_name': data.get("data_administrator_name", ""),
            'data_controller_name': data.get("data_controller_name", ""),
            'request_type': type('obj', (object,), {'value': request_type})(),
            'request_description': request_description,
            'submission_date': submission_date_parsed,
            'submission_method': type('obj', (object,), {'value': submission_method})(),
            'custom_deadline': custom_deadline_parsed
        })()
        
        print(f"Creating SAR case for organization: {organization_name}")
        return create_sar_case_db(sar_data, current_user.id)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Case creation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create case: {str(e)}"
        )

@app.get("/sar/")
async def get_sar_cases(
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    organization: Optional[str] = None
):
    return get_sar_cases_db(current_user.id, skip, limit, status, organization)

@app.get("/sar/{sar_id}")
async def get_sar_case(
    sar_id: int,
    current_user: User = Depends(get_current_user)
):
    sar = get_sar_case_db(sar_id, current_user.id)
    if not sar:
        raise HTTPException(status_code=404, detail="SAR case not found")
    return sar

@app.put("/sar/{sar_id}")
async def update_sar_case(
    sar_id: int,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    try:
        body = await request.body()
        if not body:
            raise HTTPException(status_code=400, detail="Request body is empty")
        
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON")
        
        # Create update data object
        update_data = type('obj', (object,), {
            'organization_name': data.get('organization_name', ''),
            'organization_email': data.get('organization_email', ''),
            'organization_phone': data.get('organization_phone', ''),
            'organization_address': data.get('organization_address', ''),
            'data_administrator_name': data.get('data_administrator_name', ''),
            'data_controller_name': data.get('data_controller_name', ''),
            'request_description': data.get('request_description', ''),
            'custom_deadline': datetime.strptime(data.get('custom_deadline'), '%Y-%m-%d').date() if data.get('custom_deadline') else None
        })()
        
        print(f"Updating SAR case {sar_id}")
        return update_sar_case_simple_db(sar_id, update_data, current_user.id)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Case update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update case: {str(e)}"
        )

@app.delete("/sar/{sar_id}")
async def delete_sar_case(
    sar_id: int,
    current_user: User = Depends(get_current_user)
):
    try:
        print(f"Deleting SAR case {sar_id}")
        success = delete_sar_case_db(sar_id, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="SAR case not found")
        return {"message": "Case deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Case deletion error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete case: {str(e)}"
        )

# Case Update endpoints
@app.post("/sar/{sar_id}/updates")
async def create_case_update(
    sar_id: int,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    try:
        body = await request.body()
        if not body:
            raise HTTPException(status_code=400, detail="Request body is empty")
        
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON")
        
        # Create update data object
        update_data = type('obj', (object,), {
            'sar_case_id': sar_id,
            'update_type': data.get('update_type', 'Correspondence'),
            'title': data.get('title', ''),
            'content': data.get('content', ''),
            'correspondence_date': datetime.strptime(data.get('correspondence_date'), '%Y-%m-%d').date() if data.get('correspondence_date') else date.today()
        })()
        
        print(f"Creating case update for SAR {sar_id}")
        return create_case_update_db(update_data, current_user.id)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Case update creation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create case update: {str(e)}"
        )

@app.post("/sar/{sar_id}/files")
async def upload_case_file(
    sar_id: int,
    file: UploadFile = File(...),
    update_id: int = Form(...),
    current_user: User = Depends(get_current_user)
):
    """Upload a file for a case update."""
    try:
        # Validate file type
        allowed_extensions = {'.pdf', '.png', '.jpg', '.jpeg', '.gif', '.doc', '.docx', '.txt', '.eml', '.msg'}
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {file_extension} not allowed. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Validate file size (max 10MB)
        if file.size and file.size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size too large. Maximum size is 10MB.")
        
        # Create uploads directory if it doesn't exist
        upload_dir = f"uploads/sar_{sar_id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename.replace(' ', '_')}"
        file_path = os.path.join(upload_dir, safe_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Create file record in database
        file_data = type('obj', (object,), {
            'sar_case_id': sar_id,
            'update_id': update_id,
            'filename': file.filename,
            'file_path': file_path,
            'file_size': file.size or len(content),
            'file_type': file_extension,
            'uploaded_by': current_user.id
        })()
        
        print(f"Uploading file {file.filename} for SAR {sar_id}")
        return create_case_file_db(file_data, current_user.id)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"File upload error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )

@app.get("/sar/{sar_id}/updates")
async def get_case_updates(
    sar_id: int,
    current_user: User = Depends(get_current_user)
):
    updates = get_case_updates_db(sar_id, current_user.id)
    return updates

# Case File endpoints
@app.get("/sar/{sar_id}/files")
async def get_case_files(
    sar_id: int,
    current_user: User = Depends(get_current_user)
):
    files = get_case_files_db(sar_id, current_user.id)
    return files

# Dashboard and analytics
@app.get("/dashboard/overview")
async def get_dashboard_overview(
    current_user: User = Depends(get_current_user_simple)
):
    """Dashboard overview endpoint with simple authentication."""
    print(f"DEBUG: Dashboard endpoint called successfully for user: {current_user.username}")
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
    """Get calendar events for a date range."""
    return get_calendar_events_data(current_user.id, start_date, end_date)

# Reports endpoints
@app.get("/reports/overall")
async def generate_overall_report(
    current_user: User = Depends(get_current_user)
):
    """Generate overall system report."""
    try:
        # Get dashboard data for the report
        dashboard_data = get_dashboard_data(current_user.id)
        organization_data = get_organization_performance_data(current_user.id)
        
        # Create a simple report structure
        report_data = {
            "user_id": current_user.id,
            "username": current_user.username,
            "generated_at": datetime.now().isoformat(),
            "dashboard_summary": dashboard_data,
            "organization_performance": organization_data
        }
        
        # For now, return JSON data (we can enhance this to generate PDF later)
        return report_data
        
    except Exception as e:
        print(f"Error generating overall report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate overall report: {str(e)}"
        )

@app.get("/reports/case/{sar_id}")
async def generate_case_report(
    sar_id: int,
    current_user: User = Depends(get_current_user)
):
    """Generate individual case report."""
    try:
        # Get the SAR case
        sar_case = get_sar_case_db(sar_id, current_user.id)
        if not sar_case:
            raise HTTPException(status_code=404, detail="SAR case not found")
        
        # Get case updates and files
        updates = get_case_updates_db(sar_id, current_user.id)
        files = get_case_files_db(sar_id, current_user.id)
        
        # Create case report data
        case_report = {
            "case_id": sar_case.id,
            "case_reference": sar_case.case_reference,
            "organization_name": sar_case.organization_name,
            "request_type": sar_case.request_type,
            "submission_date": sar_case.submission_date.isoformat() if sar_case.submission_date else None,
            "status": sar_case.status,
            "deadlines": {
                "statutory": sar_case.statutory_deadline.isoformat() if sar_case.statutory_deadline else None,
                "custom": sar_case.custom_deadline.isoformat() if sar_case.custom_deadline else None,
                "extended": sar_case.extended_deadline.isoformat() if sar_case.extended_deadline else None
            },
            "updates": [{"date": u.created_at.isoformat(), "description": u.description} for u in updates] if updates else [],
            "files": [{"filename": f.filename, "uploaded_at": f.uploaded_at.isoformat()} for f in files] if files else [],
            "generated_at": datetime.now().isoformat()
        }
        
        return case_report
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating case report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate case report: {str(e)}"
        )

@app.get("/reports/sar-letter/{sar_id}")
async def generate_sar_letter(
    sar_id: int,
    format: str = "txt",
    current_user: User = Depends(get_current_user)
):
    """Generate SAR letter for a case in specified format."""
    try:
        # Get the SAR case
        sar_case = get_sar_case_db(sar_id, current_user.id)
        if not sar_case:
            raise HTTPException(status_code=404, detail="SAR case not found")
        
        if format.lower() == "pdf":
            # Generate PDF
            try:
                from reportlab.lib.pagesizes import letter
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.units import inch
                from reportlab.lib import colors
                from io import BytesIO
                
                # Create PDF buffer
                buffer = BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=letter)
                story = []
                styles = getSampleStyleSheet()
                
                # Custom styles
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=16,
                    spaceAfter=20,
                    alignment=1  # Center
                )
                
                header_style = ParagraphStyle(
                    'Header',
                    parent=styles['Heading2'],
                    fontSize=14,
                    spaceAfter=12
                )
                
                normal_style = ParagraphStyle(
                    'Normal',
                    parent=styles['Normal'],
                    fontSize=11,
                    spaceAfter=6
                )
                
                # Add content
                story.append(Paragraph("SUBJECT ACCESS REQUEST", title_style))
                story.append(Spacer(1, 20))
                
                # Date and recipient
                current_date = datetime.now().strftime("%B %d, %Y")
                story.append(Paragraph(f"Date: {current_date}", normal_style))
                story.append(Paragraph(f"To: {sar_case.organization_name}", normal_style))
                story.append(Paragraph(f"Case Reference: {sar_case.case_reference}", normal_style))
                story.append(Spacer(1, 20))
                
                # Greeting
                story.append(Paragraph("Dear Sir/Madam,", normal_style))
                story.append(Spacer(1, 12))
                
                # Main content
                story.append(Paragraph(
                    "I am writing to make a formal Subject Access Request (SAR) under the Data Protection Act 2018 and UK GDPR Article 15.",
                    normal_style
                ))
                story.append(Spacer(1, 12))
                
                story.append(Paragraph("I hereby request that you provide me with the following information:", header_style))
                
                # Data points
                data_points = [
                    "1. Confirmation that you are processing my personal data",
                    "2. The legal basis for processing my personal data",
                    "3. The categories of personal data you hold about me",
                    "4. The source of the personal data",
                    "5. The purposes for which the data is being processed",
                    "6. Any third parties with whom you share my personal data",
                    "7. The retention period for my personal data",
                    "8. My rights under data protection law",
                    "9. Any automated decision-making processes",
                    "10. A copy of my personal data in a structured, commonly used format"
                ]
                
                for point in data_points:
                    story.append(Paragraph(point, normal_style))
                
                story.append(Spacer(1, 12))
                
                # Request details
                story.append(Paragraph("Request Details:", header_style))
                story.append(Paragraph(f"• Request Type: {sar_case.request_type}", normal_style))
                story.append(Paragraph(f"• Case Reference: {sar_case.case_reference}", normal_style))
                if sar_case.submission_date:
                    story.append(Paragraph(f"• Submission Date: {sar_case.submission_date.strftime('%B %d, %Y')}", normal_style))
                
                if sar_case.request_description:
                    story.append(Paragraph(f"• Request Description: {sar_case.request_description}", normal_style))
                
                story.append(Spacer(1, 12))
                
                # Legal basis
                story.append(Paragraph(
                    "This request is made under Article 15 of the UK GDPR and Section 45 of the Data Protection Act 2018. "
                    "You are required to respond to this request within one calendar month of receipt.",
                    normal_style
                ))
                story.append(Spacer(1, 12))
                
                story.append(Paragraph(
                    "If you require additional information to identify me or locate the relevant data, please contact me immediately. "
                    "If you need to extend the response period, you must inform me within one month of receiving this request.",
                    normal_style
                ))
                story.append(Spacer(1, 12))
                
                story.append(Paragraph(
                    "I look forward to receiving your response within the statutory timeframe.",
                    normal_style
                ))
                story.append(Spacer(1, 20))
                
                # Closing
                story.append(Paragraph("Yours faithfully,", normal_style))
                story.append(Spacer(1, 20))
                story.append(Paragraph(f"{current_user.full_name or current_user.username}", normal_style))
                story.append(Spacer(1, 20))
                
                # Footer
                story.append(Paragraph("---", normal_style))
                story.append(Paragraph("Generated by SAR Tracking System", normal_style))
                story.append(Paragraph(f"Case: {sar_case.case_reference}", normal_style))
                story.append(Paragraph(f"Date: {current_date}", normal_style))
                
                # Build PDF
                doc.build(story)
                buffer.seek(0)
                
                return Response(
                    content=buffer.getvalue(),
                    media_type="application/pdf",
                    headers={
                        "Content-Disposition": f"attachment; filename={sar_case.case_reference}-SAR-Letter.pdf"
                    }
                )
                
            except Exception as pdf_error:
                print(f"PDF generation failed, falling back to text: {str(pdf_error)}")
                # Fallback to text if PDF generation fails
                letter_content = generate_sar_letter_content(sar_case, current_user)
                return Response(
                    content=letter_content,
                    media_type="text/plain",
                    headers={
                        "Content-Disposition": f"attachment; filename={sar_case.case_reference}-SAR-Letter.txt"
                    }
                )
        else:
            # Generate text format
            letter_content = generate_sar_letter_content(sar_case, current_user)
            return Response(
                content=letter_content,
                media_type="text/plain",
                headers={
                    "Content-Disposition": f"attachment; filename={sar_case.case_reference}-SAR-Letter.txt"
                }
            )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating SAR letter: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate SAR letter: {str(e)}"
        )

def generate_sar_letter_content(sar_case, user):
    """Generate SAR letter content."""
    current_date = datetime.now().strftime("%B %d, %Y")
    
    letter_content = f"""SUBJECT ACCESS REQUEST

Date: {current_date}

To: {sar_case.organization_name}
Case Reference: {sar_case.case_reference}

Dear Sir/Madam,

I am writing to make a formal Subject Access Request (SAR) under the Data Protection Act 2018 and UK GDPR Article 15.

I hereby request that you provide me with the following information:

1. Confirmation that you are processing my personal data
2. The legal basis for processing my personal data
3. The categories of personal data you hold about me
4. The source of the personal data
5. The purposes for which the data is being processed
6. Any third parties with whom you share my personal data
7. The retention period for my personal data
8. My rights under data protection law
9. Any automated decision-making processes
10. A copy of my personal data in a structured, commonly used format

Request Details:
- Request Type: {sar_case.request_type}
- Case Reference: {sar_case.case_reference}
- Submission Date: {sar_case.submission_date.strftime('%B %d, %Y') if sar_case.submission_date else 'N/A'}

{f"Request Description: {sar_case.request_description}" if sar_case.request_description else ""}

This request is made under Article 15 of the UK GDPR and Section 45 of the Data Protection Act 2018. You are required to respond to this request within one calendar month of receipt.

If you require additional information to identify me or locate the relevant data, please contact me immediately. If you need to extend the response period, you must inform me within one month of receiving this request.

I look forward to receiving your response within the statutory timeframe.

Yours faithfully,
{user.full_name or user.username}

---
Generated by SAR Tracking System
Case: {sar_case.case_reference}
Date: {current_date}
"""
    
    return letter_content.encode('utf-8')

@app.post("/init-db")
async def initialize_database():
    """Initialize database and create admin user."""
    try:
        from app.database import engine, Base
        from app.models import User
        from app.auth import get_password_hash
        from sqlalchemy.orm import Session
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        
        # Create admin user if it doesn't exist
        db = Session(engine)
        try:
            admin_user = db.query(User).filter(User.username == "admin").first()
            if not admin_user:
                admin_user = User(
                    username="admin",
                    email="admin@sar-system.com",
                    full_name="System Administrator",
                    hashed_password=get_password_hash("admin123"),
                    is_admin=True
                )
                db.add(admin_user)
                db.commit()
                return {"message": "Database initialized successfully. Admin user created: admin/admin123"}
            else:
                return {"message": "Database already initialized. Admin user exists: admin/admin123"}
        finally:
            db.close()
            
    except Exception as e:
        print(f"Database initialization error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database initialization failed: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
