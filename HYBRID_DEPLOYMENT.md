# 🌐 Hybrid Local/Online SAR System Deployment Guide

## Overview

This SAR Tracking System can operate in two modes:

1. **🔒 Local Mode**: Users load their own JSON files, no data stored online
2. **☁️ Online Mode**: Admin users with cloud storage and case management

## 🚀 Deployment Options

### Option 1: GitHub Pages (Frontend Only - Local Mode)

**Perfect for**: Users who want complete privacy and control over their data

**Features**:
- ✅ No server required
- ✅ Data stays on user's device
- ✅ Works offline after initial load
- ✅ Free hosting via GitHub Pages
- ✅ Custom domain support

**Setup**:
1. Fork this repository
2. Enable GitHub Pages in repository settings
3. Set source to "GitHub Actions"
4. Push to main branch - automatic deployment

**User Experience**:
- Users visit your GitHub Pages URL
- Choose "Local Mode" on login page
- Upload their JSON file with SAR data
- Work completely offline with their data
- Export data as JSON/CSV when needed

### Option 2: Full Online System (Frontend + Backend)

**Perfect for**: Organizations wanting cloud storage and multi-user access

**Features**:
- ✅ Cloud database storage
- ✅ Multi-user authentication
- ✅ Real-time collaboration
- ✅ Automated backups
- ✅ Admin dashboard

**Setup**:
1. Deploy backend to your preferred hosting (Heroku, AWS, DigitalOcean, etc.)
2. Deploy frontend to GitHub Pages or your hosting
3. Configure environment variables
4. Set up database

## 📁 Local Mode Data Format

Users need to provide JSON files with this structure:

```json
{
  "metadata": {
    "version": "1.0.0",
    "created": "2025-01-17",
    "description": "Your SAR data description"
  },
  "sar_cases": [
    {
      "id": 1,
      "case_reference": "SAR-202501-001",
      "organization_name": "Company Name",
      "request_type": "personal_data",
      "submission_date": "2025-01-15",
      "status": "Pending",
      // ... other fields
    }
  ]
}
```

## 🔧 Configuration

### Frontend Configuration

Update `frontend/src/config.ts`:

```typescript
export const config = {
  // For local mode only
  LOCAL_MODE_ONLY: false,
  
  // For online mode
  API_BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  
  // For GitHub Pages deployment
  BASE_URL: process.env.REACT_APP_BASE_URL || '/',
};
```

### Backend Configuration

Update `.env`:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/sar_db

# JWT Secret
SECRET_KEY=your-secret-key

# CORS Origins
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# File Upload
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760
```

## 🌍 GitHub Pages Deployment

### 1. Repository Setup

```bash
# Enable GitHub Pages
# Go to Settings > Pages
# Source: Deploy from a branch
# Branch: gh-pages
# Folder: / (root)
```

### 2. Automatic Deployment

The GitHub Actions workflow automatically:
- Builds the React app
- Deploys to GitHub Pages
- Updates on every push to main

### 3. Custom Domain (Optional)

1. Add your domain to repository settings
2. Update `CNAME` file in the workflow
3. Configure DNS records

## 🔐 Security Considerations

### Local Mode
- ✅ No data leaves user's device
- ✅ No server-side storage
- ✅ Complete privacy
- ⚠️ Users responsible for their own data security

### Online Mode
- ✅ JWT authentication
- ✅ Password hashing with bcrypt
- ✅ CORS protection
- ✅ Input validation
- ⚠️ Requires secure hosting and database

## 📱 User Experience

### Local Mode Users
1. Visit your GitHub Pages URL
2. Click "Local Mode"
3. Upload JSON file or download template
4. Work with their data offline
5. Export data when needed

### Online Mode Users
1. Visit your GitHub Pages URL
2. Click "Online Mode"
3. Login with credentials
4. Access cloud-stored data
5. Collaborate with team members

## 🚀 Quick Start

### For Local Mode Only
1. Fork repository
2. Enable GitHub Pages
3. Push to main branch
4. Share your GitHub Pages URL

### For Full System
1. Deploy backend to your hosting
2. Deploy frontend to GitHub Pages
3. Configure environment variables
4. Set up database
5. Test both modes

## 📊 Monitoring

### GitHub Pages
- Built-in analytics
- GitHub Insights
- Custom analytics (Google Analytics, etc.)

### Backend
- Application logs
- Database monitoring
- Performance metrics

## 🔄 Updates

### Frontend Updates
- Automatic deployment via GitHub Actions
- Users get updates immediately
- No manual intervention needed

### Backend Updates
- Manual deployment required
- Database migrations
- Environment variable updates

## 💡 Best Practices

1. **Regular Backups**: For online mode, backup database regularly
2. **Security Updates**: Keep dependencies updated
3. **User Education**: Provide clear instructions for local mode
4. **Template Updates**: Keep JSON template current
5. **Documentation**: Maintain clear user guides

## 🆘 Troubleshooting

### Common Issues

**GitHub Pages not loading**:
- Check Actions tab for build errors
- Verify repository settings
- Check branch permissions

**Local mode not working**:
- Verify JSON format
- Check browser console for errors
- Ensure file is valid JSON

**Online mode issues**:
- Check backend logs
- Verify environment variables
- Test database connection

## 📞 Support

For issues or questions:
1. Check existing GitHub Issues
2. Create new issue with details
3. Include error messages and steps to reproduce

---

**Note**: This system provides maximum flexibility - users can choose their preferred mode based on their privacy and collaboration needs.
