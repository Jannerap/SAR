import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';

// Note: API_BASE_URL is configured in axios defaults when needed

// Set up axios interceptor for authentication
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Set up axios interceptor for response errors
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 || error.response?.status === 403) {
      // Token expired or invalid, clear it
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

interface User {
  id: number;
  username: string;
  full_name?: string;
  email: string;
  is_admin: boolean;
}

interface SARCase {
  id: number;
  case_reference: string;
  organization_name: string;
  request_type: string;
  submission_date: string;
  status: string;
  statutory_deadline: string;
  custom_deadline?: string;
  extended_deadline?: string;
  request_description?: string;
  urgency?: string;
  data_volume?: string;
  special_considerations?: string;
  notes?: string;
  case_updates?: any[];
  files?: any[];
  reminders?: any[];
}

interface LocalData {
  metadata: {
    version: string;
    created: string;
    description: string;
  };
  sar_cases: SARCase[];
  settings?: {
    default_deadline_days: number;
    reminder_days_before: number;
    auto_extensions: boolean;
  };
}

interface AuthContextType {
  user: User | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  loading: boolean;
  isLocalMode: boolean;
  setLocalMode: (mode: boolean) => void;
  localData: LocalData | null;
  setLocalData: (data: LocalData | null) => void;
  loadLocalFile: (file: File) => Promise<LocalData>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [isLocalMode, setIsLocalMode] = useState(false);
  const [localData, setLocalData] = useState<LocalData | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        if (payload.exp * 1000 > Date.now()) {
          // Token is valid, try to get user info
          fetchUserInfo(token);
        } else {
          localStorage.removeItem('token');
          setLoading(false);
        }
      } catch (error) {
        console.error('Token decode error:', error);
        localStorage.removeItem('token');
        setLoading(false);
      }
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUserInfo = async (token: string) => {
    try {
      const response = await axios.get('/auth/me');
      setUser(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch user info:', error);
      localStorage.removeItem('token');
      setLoading(false);
    }
  };

  const login = async (username: string, password: string) => {
    try {
      const response = await axios.post('/auth/login', { username, password });
      const { access_token, user: userData } = response.data;
      
      // Store token
      localStorage.setItem('token', access_token);
      
      // Set user data
      setUser(userData);
      setIsLocalMode(false); // Online mode after login
      
      // Set axios default header for this session
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      console.log('Login successful, user:', userData);
      console.log('Token stored:', access_token);
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setIsLocalMode(false);
    setLocalData(null);
  };

  const setLocalMode = (mode: boolean) => {
    setIsLocalMode(mode);
  };

  const loadLocalFile = async (file: File) => {
    try {
      const text = await file.text();
      const data = JSON.parse(text);
      
      // Validate the JSON structure
      if (!data.sar_cases || !Array.isArray(data.sar_cases)) {
        throw new Error('Invalid SAR data format. File must contain "sar_cases" array.');
      }
      
      setLocalData(data);
      setIsLocalMode(true);
      setUser(null); // Clear online user
      localStorage.removeItem('token'); // Clear online token
      
      return data;
    } catch (error) {
      console.error('Error loading local file:', error);
      throw new Error('Failed to load file. Please ensure it\'s a valid SAR data JSON file.');
    }
  };

  const value: AuthContextType = {
    user,
    login,
    logout,
    isAuthenticated: !!user || isLocalMode,
    loading,
    isLocalMode,
    setLocalMode,
    localData,
    setLocalData,
    loadLocalFile
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
