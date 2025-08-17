# SAR Tracking System - Setup Guide

This guide will walk you through setting up the complete SAR Tracking System on your local machine.

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 16+** - [Download Node.js](https://nodejs.org/)
- **Git** - [Download Git](https://git-scm.com/)

### 1. Clone and Setup Backend

```bash
# Navigate to your project directory
cd SAR

# Install Python dependencies
pip install -r requirements.txt

# Initialize the database
python init_db.py
```

### 2. Start the Backend

```bash
# Start the FastAPI server
python run.py
```

The backend will be available at: http://localhost:8000
API documentation: http://localhost:8000/docs

### 3. Setup Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Start the React development server
npm start
```

The frontend will be available at: http://localhost:3000

### 4. Login

- **Username**: `admin`
- **Password**: `admin123`

⚠️ **Important**: Change the default password after first login!

## 🔧 Detailed Setup

### Backend Configuration

The system uses environment variables for configuration. Create a `.env` file in the root directory:

```bash
# Database Configuration
DATABASE_URL=sqlite:///./sar_tracking.db

# Security
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Upload Configuration
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760

# Application Settings
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### Database Options

**SQLite (Default - Development)**
```bash
DATABASE_URL=sqlite:///./sar_tracking.db
```

**PostgreSQL (Production)**
```bash
DATABASE_URL=postgresql://username:password@localhost/sar_tracking
```

### File Storage

The system stores uploaded files in the `uploads/` directory:
- Case files: `uploads/sar_{case_id}/`
- Reports: `uploads/reports/`

## 📱 Features Overview

### Core Features
- ✅ **SAR Case Management** - Create, track, and manage Subject Access Requests
- ✅ **Deadline Tracking** - Automatic calculation of 28-day statutory deadlines
- ✅ **Case Updates** - Add notes, correspondence, and file uploads
- ✅ **ICO Escalations** - Track complaints to the Information Commissioner's Office
- ✅ **Template System** - Pre-built templates for SAR requests and follow-ups
- ✅ **Report Generation** - Export case data to PDF and Word formats

### Advanced Features
- ✅ **Dashboard Analytics** - Overview of case status and organization performance
- ✅ **Calendar View** - Visual representation of deadlines and reminders
- ✅ **Organization Tracking** - Monitor compliance patterns across organizations
- ✅ **File Management** - Secure storage and organization of case documents
- ✅ **Audit Trail** - Complete history of all case activities

## 🛠️ Development

### Project Structure

```
SAR/
├── app/                    # Backend application
│   ├── __init__.py
│   ├── main.py            # FastAPI application
│   ├── database.py        # Database configuration
│   ├── models.py          # SQLAlchemy models
│   ├── schemas.py         # Pydantic schemas
│   ├── crud.py            # Database operations
│   ├── auth.py            # Authentication system
│   ├── templates.py       # Email/document templates
│   └── reports.py         # Report generation
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Page components
│   │   ├── contexts/      # React contexts
│   │   └── App.tsx        # Main application
│   ├── package.json
│   └── tailwind.config.js
├── uploads/               # File storage
├── requirements.txt       # Python dependencies
├── run.py                 # Backend startup script
└── init_db.py            # Database initialization
```

### API Endpoints

#### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration

#### SAR Cases
- `GET /sar/` - List all cases
- `POST /sar/` - Create new case
- `GET /sar/{id}` - Get case details
- `PUT /sar/{id}` - Update case
- `DELETE /sar/{id}` - Delete case

#### Case Updates
- `POST /sar/{id}/updates/` - Add case update
- `GET /sar/{id}/updates/` - Get case updates

#### File Management
- `POST /sar/{id}/files/` - Upload file
- `GET /sar/{id}/files/` - Get case files

#### ICO Escalations
- `POST /sar/{id}/ico-escalation/` - Create ICO escalation
- `GET /ico-escalations/` - List ICO escalations

#### Reports
- `GET /sar/{id}/report/pdf` - Generate PDF report
- `GET /sar/{id}/report/word` - Generate Word report

#### Dashboard
- `GET /dashboard/overview` - Dashboard overview
- `GET /dashboard/organization-performance` - Organization performance
- `GET /dashboard/deadlines` - Upcoming deadlines

### Database Schema

The system includes the following main tables:

- **users** - User accounts and authentication
- **sar_cases** - Main SAR case information
- **case_updates** - Case notes and correspondence
- **case_files** - Uploaded documents and files
- **ico_escalations** - ICO complaint tracking
- **reminders** - Deadline and action reminders
- **organizations** - Organization performance tracking

## 🚨 Troubleshooting

### Common Issues

**Backend won't start**
```bash
# Check Python version
python --version

# Verify dependencies
pip list | grep fastapi

# Check port availability
lsof -i :8000
```

**Frontend won't start**
```bash
# Check Node.js version
node --version

# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

**Database errors**
```bash
# Reinitialize database
python init_db.py

# Check file permissions
ls -la sar_tracking.db
```

**File upload issues**
```bash
# Check upload directory
ls -la uploads/

# Verify permissions
chmod 755 uploads/
```

### Logs

Backend logs are displayed in the console when running `python run.py`.

Frontend logs are available in the browser console (F12 → Console).

## 🔒 Security Considerations

### Production Deployment

1. **Change default credentials** immediately after setup
2. **Use strong SECRET_KEY** for JWT tokens
3. **Enable HTTPS** in production
4. **Restrict file uploads** to trusted sources
5. **Implement rate limiting** for API endpoints
6. **Use environment variables** for sensitive configuration
7. **Regular security updates** for dependencies

### Data Protection

- All user data is encrypted at rest
- JWT tokens have configurable expiration
- File uploads are validated and sanitized
- Database queries use parameterized statements

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [UK GDPR Information](https://ico.org.uk/for-organisations/guide-to-data-protection/guide-to-the-general-data-protection-regulation-gdpr/)
- [ICO Subject Access Request Guide](https://ico.org.uk/for-organisations/guide-to-data-protection/guide-to-the-general-data-protection-regulation-gdpr/individual-rights/right-of-access/)

## 🤝 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the logs for error messages
3. Verify all prerequisites are installed
4. Check file permissions and paths
5. Ensure ports are not in use by other services

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

---

**Note**: This system is designed to help track and manage Subject Access Requests. It is not legal advice and should not be used as a substitute for professional legal consultation. Users are responsible for ensuring compliance with applicable data protection laws and regulations.
