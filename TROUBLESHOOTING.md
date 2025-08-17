# SAR Tracking System - Troubleshooting Guide

## 🚨 Current Issue: Python 3.13 + Pydantic Dependencies

You're experiencing issues with Python 3.13.3 and `pydantic-core` which requires Rust compilation. Here are the solutions:

## 🔧 Solution 1: Use Simplified Version (Recommended)

The simplified version removes complex dependencies and should work with Python 3.13:

```bash
# 1. Test the system first
python test_system.py

# 2. If tests pass, initialize database
python init_db.py

# 3. Start the simplified version
python run_simple.py
```

## 🔧 Solution 2: Fix Dependencies

If you want to use the full version, try these steps:

### Option A: Use Compatible Python Version
```bash
# Install Python 3.11 (more compatible)
pyenv install 3.11.7
pyenv local 3.11.7
python --version  # Should show 3.11.7
```

### Option B: Install Rust (for pydantic-core)
```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env

# Then try installing requirements again
pip install -r requirements.txt
```

### Option C: Use Minimal Requirements
```bash
# Install only essential packages
pip install -r requirements-simple.txt
```

## 🧪 Testing the System

### Step 1: Run System Test
```bash
python test_system.py
```

This will test:
- ✅ Basic Python functionality
- ✅ File operations
- ✅ Module imports
- ✅ Database operations

### Step 2: Check Python Version
```bash
python --version
# Should be 3.8+ but 3.13 may have compatibility issues
```

### Step 3: Test Individual Imports
```bash
python -c "import fastapi; print('FastAPI OK')"
python -c "import uvicorn; print('Uvicorn OK')"
python -c "import sqlalchemy; print('SQLAlchemy OK')"
```

## 🚀 Quick Start (Simplified Version)

### 1. Install Dependencies
```bash
# Install minimal requirements
pip install fastapi uvicorn sqlalchemy python-multipart python-jose passlib python-dateutil jinja2 aiofiles
```

### 2. Test System
```bash
python test_system.py
```

### 3. Initialize Database
```bash
python init_db.py
```

### 4. Start Server
```bash
python run_simple.py
```

### 5. Access System
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:3000 (after setup)

## 🔍 Common Error Messages

### "Rust not found, installing into a temporary directory"
**Cause**: pydantic-core requires Rust to compile
**Solution**: Use simplified version or install Rust

### "Failed building wheel for pydantic-core"
**Cause**: Compilation failure
**Solution**: Use Python 3.11 or simplified version

### "ModuleNotFoundError: No module named 'fastapi'"
**Cause**: Dependencies not installed
**Solution**: Run `pip install -r requirements-simple.txt`

### "Port already in use"
**Cause**: Another service using port 8000
**Solution**: Change port or stop conflicting service
```bash
# Change port
PORT=8001 python run_simple.py
```

## 🛠️ Alternative Setup Methods

### Method 1: Virtual Environment
```bash
# Create virtual environment
python -m venv sar_env

# Activate (macOS/Linux)
source sar_env/bin/activate

# Activate (Windows)
sar_env\Scripts\activate

# Install dependencies
pip install -r requirements-simple.txt
```

### Method 2: Conda Environment
```bash
# Create conda environment
conda create -n sar_env python=3.11

# Activate
conda activate sar_env

# Install packages
conda install -c conda-forge fastapi uvicorn sqlalchemy
pip install python-multipart python-jose passlib python-dateutil jinja2 aiofiles
```

### Method 3: Docker (if available)
```bash
# Create Dockerfile
cat > Dockerfile << EOF
FROM python:3.11-slim
WORKDIR /app
COPY requirements-simple.txt .
RUN pip install -r requirements-simple.txt
COPY . .
CMD ["python", "run_simple.py"]
EOF

# Build and run
docker build -t sar-tracker .
docker run -p 8000:8000 sar-tracker
```

## 📱 Frontend Setup

After backend is working:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## 🔒 Security Note

The simplified version uses basic form handling instead of Pydantic validation. For production use:
1. Add input validation
2. Implement proper error handling
3. Add rate limiting
4. Use HTTPS

## 📞 Getting Help

If you're still having issues:

1. **Check Python version**: `python --version`
2. **Check pip version**: `pip --version`
3. **Run system test**: `python test_system.py`
4. **Check error logs**: Look for specific error messages
5. **Try simplified version**: `python run_simple.py`

## 🎯 Success Indicators

You'll know it's working when:
- ✅ `python test_system.py` shows all tests passed
- ✅ `python run_simple.py` starts without errors
- ✅ http://localhost:8000 shows "SAR Tracking System API"
- ✅ http://localhost:8000/docs shows FastAPI documentation

## 🚀 Next Steps After Success

1. **Create first user**: Use the admin/admin123 credentials
2. **Test API endpoints**: Use the interactive docs at /docs
3. **Set up frontend**: Navigate to frontend directory
4. **Customize system**: Modify templates and configurations
5. **Add features**: Extend functionality as needed

---

**Remember**: The simplified version provides core functionality without complex dependencies. It's perfect for testing and development, and you can gradually add features as needed.
