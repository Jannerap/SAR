#!/usr/bin/env python3
"""
Simple SAR Tracking System Startup Script
"""

import uvicorn
import os

if __name__ == "__main__":
    # Get configuration from environment or use defaults
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    print(f"🚀 Starting Simple SAR Tracking System...")
    print(f"📍 Server: http://{host}:{port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"📚 API docs: http://{host}:{port}/docs")
    
    # Start the server with the simple version
    uvicorn.run(
        "app.main_simple:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
