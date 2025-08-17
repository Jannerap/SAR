import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { 
  Home, 
  FileText, 
  Plus, 
  Calendar, 
  BarChart3, 
  User,
  LogOut,
  Menu,
  X,
  Download
} from 'lucide-react';

const TopNav: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  console.log('TopNav rendering with user:', user); // Debug log

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: Home },
    { name: 'SAR Cases', href: '/cases', icon: FileText },
    { name: 'New Case', href: '/cases/new', icon: Plus },
    { name: 'Calendar', href: '/calendar', icon: Calendar },
    { name: 'Reports', href: '/reports', icon: BarChart3 },
    { name: 'User Report', href: '/user-report', icon: User },
  ];

  const handleLogout = () => {
    console.log('Logout clicked'); // Debug log
    logout();
    navigate('/login');
  };

  const handleSaveToJSON = async () => {
    try {
      // Get current data from the backend
      const response = await fetch('https://web-production-055e.up.railway.app/sar/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch data');
      }
      
      const sarCases = await response.json();
      
      // Create export data structure
      const exportData = {
        metadata: {
          version: "1.0.0",
          created: new Date().toISOString(),
          description: "SAR data exported from online mode",
          exported_by: user?.username || 'admin',
          total_cases: sarCases.length
        },
        sar_cases: sarCases,
        settings: {
          default_deadline_days: 30,
          reminder_days_before: 7,
          auto_extensions: true
        }
      };
      
      // Create and download the file
      const dataStr = JSON.stringify(exportData, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `sar-data-export-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      console.log('Data exported successfully');
    } catch (error) {
      console.error('Export failed:', error);
      alert('Failed to export data. Please try again.');
    }
  };

  const isActive = (href: string) => {
    return location.pathname === href;
  };

  // Force re-render to ensure component is visible
  React.useEffect(() => {
    console.log('TopNav mounted and visible');
  }, []);

  return (
    <div className="bg-white shadow-sm border-b border-gray-200" style={{ zIndex: 1000 }}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Brand */}
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <FileText className="w-5 h-5 text-white" />
              </div>
            </div>
            <div className="ml-3">
              <h1 className="text-xl font-bold text-gray-900">SAR Tracker v2.2</h1>
            </div>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex space-x-8">
            {navigation.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.name}
                  onClick={() => navigate(item.href)}
                  className={`flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                    isActive(item.href)
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {item.name}
                </button>
              );
            })}
          </nav>

          {/* User Menu and Mobile Menu Button */}
          <div className="flex items-center space-x-4">
            {/* Save to JSON Button */}
            <button
              onClick={handleSaveToJSON}
              className="hidden md:flex items-center px-3 py-2 text-sm font-medium text-green-600 hover:text-green-700 hover:bg-green-50 rounded-md transition-colors border border-green-200"
              title="Export current data as JSON for local mode"
            >
              <Download className="w-4 h-4 mr-2" />
              Save to JSON
            </button>

            {/* User Info */}
            <div className="hidden md:flex items-center space-x-3">
              <div className="flex-shrink-0">
                <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
                  <User className="h-4 w-4 text-blue-600" />
                </div>
              </div>
              <div className="text-sm">
                <p className="font-medium text-gray-900">
                  {user?.full_name || user?.username || 'User'}
                </p>
                <p className="text-gray-500">{user?.email || 'user@example.com'}</p>
              </div>
            </div>

            {/* Logout Button */}
            <button
              onClick={handleLogout}
              className="hidden md:flex items-center px-3 py-2 text-sm font-medium text-red-600 hover:text-red-700 hover:bg-red-50 rounded-md transition-colors border border-red-200"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </button>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="md:hidden p-2 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100"
            >
              {isMobileMenuOpen ? (
                <X className="w-6 h-6" />
              ) : (
                <Menu className="w-6 h-6" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-white border-t border-gray-200">
            {navigation.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.name}
                  onClick={() => {
                    navigate(item.href);
                    setIsMobileMenuOpen(false);
                  }}
                  className={`w-full flex items-center px-3 py-2 text-base font-medium rounded-md transition-colors ${
                    isActive(item.href)
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <Icon className="w-5 h-5 mr-3" />
                  {item.name}
                </button>
              );
            })}
            
            {/* Mobile Save to JSON Button */}
            <button
              onClick={() => {
                handleSaveToJSON();
                setIsMobileMenuOpen(false);
              }}
              className="w-full flex items-center px-3 py-2 text-base font-medium text-green-600 hover:text-green-700 hover:bg-green-50 rounded-md transition-colors border border-green-200"
            >
              <Download className="w-5 h-5 mr-3" />
              Save to JSON
            </button>
            
            {/* Mobile User Info */}
            <div className="pt-4 border-t border-gray-200">
              <div className="flex items-center px-3 py-2">
                <div className="flex-shrink-0">
                  <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
                    <User className="h-4 w-4 text-blue-600" />
                  </div>
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-900">
                    {user?.full_name || user?.username || 'User'}
                  </p>
                  <p className="text-xs text-gray-500">{user?.email || 'user@example.com'}</p>
                </div>
              </div>
              
              <button
                onClick={() => {
                  handleLogout();
                  setIsMobileMenuOpen(false);
                }}
                className="w-full flex items-center px-3 py-2 text-base font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors"
              >
                <LogOut className="w-5 h-5 mr-3" />
                Logout
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TopNav;
