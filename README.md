# 🚀 SAR Tracking System

A comprehensive Subject Access Request (SAR) tracking and accountability system that provides both **online** and **local** modes for data privacy and flexibility.

## 🌐 **Live Demo**

**GitHub Pages**: [https://jannerap.github.io/SAR](https://jannerap.github.io/SAR)

## ✨ **Features**

### 🔐 **Dual Mode System**
- **Online Mode**: Cloud-backed with user authentication and data persistence
- **Local Mode**: File-based with complete data privacy (no data stored on servers)

### 📊 **Core Functionality**
- **SAR Case Management**: Create, view, update, and delete SAR cases
- **Deadline Tracking**: Automatic deadline calculation with calendar integration
- **Case Updates**: Track progress with notes and file attachments
- **Reporting**: Generate comprehensive reports and SAR letters (PDF/TXT)
- **Dashboard**: Multi-case overview with performance metrics
- **Calendar View**: Visual deadline management and reminders

### 🎯 **Advanced Features**
- **Template Automation**: Pre-built templates for common request types
- **Evidence Handling**: File uploads with audit trails
- **Accountability Metrics**: Organization performance tracking
- **ICO Workflow**: Regulatory compliance features
- **Export Options**: JSON and CSV data export

## 🚀 **Quick Start**

### **Option 1: Use Online (Recommended for Teams)**
1. Visit [https://jannerap.github.io/SAR](https://jannerap.github.io/SAR)
2. Click "Online Mode"
3. Login with your credentials
4. Start managing your SAR cases

### **Option 2: Use Local (Recommended for Privacy)**
1. Visit [https://jannerap.github.io/SAR](https://jannerap.github.io/SAR)
2. Click "Local Mode"
3. Download the sample template: [sar-template.json](public/sar-template.json)
4. Customize with your data and upload
5. Your data stays completely private on your device

## 🛠️ **Local Development**

### **Prerequisites**
- Node.js 18+ 
- Python 3.9+
- Git

### **Frontend Setup**
```bash
cd frontend
npm install
npm start
```

### **Backend Setup**
```bash
# Install Python dependencies
pip install -r requirements-simple.txt

# Run the backend
python run_simple.py
```

### **Database Setup**
The system automatically creates a SQLite database on first run. For production, update the `DATABASE_URL` in `app/database.py`.

## 🌍 **Deployment**

### **GitHub Pages (Frontend)**
The frontend automatically deploys to GitHub Pages when you push to the `main` branch.

### **Backend Deployment**
For production use, deploy the backend to:
- **Heroku**: Use the `requirements-simple.txt`
- **AWS**: Deploy to EC2 or Lambda
- **DigitalOcean**: Use App Platform
- **Vercel**: Deploy as serverless functions

Update the `API_BASE_URL` in `frontend/src/contexts/AuthContext.tsx` to point to your deployed backend.

## 📁 **Project Structure**

```
SAR/
├── frontend/                 # React TypeScript frontend
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/          # Page components
│   │   ├── contexts/       # React contexts
│   │   └── types/          # TypeScript type definitions
│   └── public/             # Static assets
├── app/                     # FastAPI backend
│   ├── main_simple.py      # Main application
│   ├── models.py           # Database models
│   ├── crud.py             # Database operations
│   ├── auth.py             # Authentication logic
│   └── reports.py          # Report generation
├── .github/workflows/       # GitHub Actions
└── README.md               # This file
```

## 🔧 **Configuration**

### **Environment Variables**
Create a `.env` file in the backend directory:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./sar_tracking.db
```

### **Customization**
- **Deadlines**: Update default deadline days in settings
- **Templates**: Modify report templates in `app/templates.py`
- **Styling**: Customize UI with Tailwind CSS classes

## 📊 **Data Format**

### **Local Mode JSON Structure**
```json
{
  "metadata": {
    "version": "1.0.0",
    "created": "2025-01-17",
    "description": "Your SAR data"
  },
  "sar_cases": [
    {
      "id": 1,
      "case_reference": "SAR-202501-001",
      "organization_name": "Your Company",
      "request_type": "personal_data",
      "submission_date": "2025-01-15",
      "status": "Pending",
      "case_updates": [],
      "files": [],
      "reminders": []
    }
  ],
  "settings": {
    "default_deadline_days": 28,
    "reminder_days_before": 7,
    "auto_extensions": false
  }
}
```

## 🔒 **Security Features**

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt password security
- **CORS Protection**: Cross-origin request security
- **Input Validation**: Comprehensive data validation
- **SQL Injection Protection**: SQLAlchemy ORM protection

## 📈 **Performance**

- **Connection Pooling**: Optimized database connections
- **Lazy Loading**: Efficient data loading
- **Caching**: Smart caching strategies
- **Compression**: Optimized asset delivery

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 **Support**

- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Join discussions in GitHub Discussions
- **Wiki**: Check the GitHub Wiki for detailed documentation

## 🎉 **Acknowledgments**

- Built with React, TypeScript, and FastAPI
- Styled with Tailwind CSS
- Icons from Lucide React
- Deployed with GitHub Actions

---

**Ready to streamline your SAR management?** 🚀

Visit [https://jannerap.github.io/SAR](https://jannerap.github.io/SAR) to get started!
