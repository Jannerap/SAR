import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  FileText,
  Clock,
  AlertTriangle,
  CheckCircle,
  TrendingUp,
  Plus,
  Calendar,
  BarChart3,
  ArrowRight
} from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

interface DashboardData {
  total_cases: number;
  pending_cases: number;
  overdue_cases: number;
  completed_cases: number;
  escalated_cases: number;
  upcoming_deadlines: number;
  overdue_deadlines: number;
}

interface DeadlineInfo {
  sar_case_id: number;
  case_reference: string;
  organization_name: string;
  deadline_date: string;
  days_remaining: number;
  is_overdue: boolean;
  deadline_type: string;
}

interface OrganizationPerformance {
  organization_name: string;
  total_sars: number;
  responded_on_time: number;
  responded_late: number;
  ignored: number;
  average_response_time: number | null;
  compliance_rating: number | null;
}

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [upcomingDeadlines, setUpcomingDeadlines] = useState<DeadlineInfo[]>([]);
  const [organizationPerformance, setOrganizationPerformance] = useState<OrganizationPerformance[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch dashboard overview
      try {
        const overviewResponse = await axios.get('/dashboard/overview');
        console.log('Dashboard overview response:', overviewResponse.data);
        setDashboardData(overviewResponse.data);
      } catch (overviewError) {
        console.error('Dashboard overview error:', overviewError);
        // Set default data if API fails
        setDashboardData({
          total_cases: 0,
          pending_cases: 0,
          overdue_cases: 0,
          completed_cases: 0,
          escalated_cases: 0,
          upcoming_deadlines: 0,
          overdue_deadlines: 0
        });
      }
      
      // Fetch upcoming deadlines
      try {
        const deadlinesResponse = await axios.get('/dashboard/deadlines?days=7');
        console.log('Deadlines response:', deadlinesResponse.data);
        setUpcomingDeadlines(deadlinesResponse.data);
      } catch (deadlinesError) {
        console.error('Deadlines error:', deadlinesError);
        setUpcomingDeadlines([]);
      }
      
      // Fetch organization performance
      try {
        const performanceResponse = await axios.get('/dashboard/organization-performance');
        console.log('Performance response:', performanceResponse.data);
        setOrganizationPerformance(performanceResponse.data);
      } catch (performanceError) {
        console.error('Performance error:', performanceError);
        setOrganizationPerformance([]);
      }
      
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'pending':
        return 'text-warning-600 bg-warning-100';
      case 'overdue':
        return 'text-danger-600 bg-danger-100';
      case 'complete':
        return 'text-success-600 bg-success-100';
      case 'escalated':
        return 'text-purple-600 bg-purple-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getDeadlineColor = (daysRemaining: number, isOverdue: boolean) => {
    if (isOverdue) return 'text-danger-600 bg-danger-100';
    if (daysRemaining <= 1) return 'text-danger-600 bg-danger-100';
    if (daysRemaining <= 3) return 'text-warning-600 bg-warning-100';
    return 'text-success-600 bg-success-100';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome back, {user?.full_name || user?.username}!
        </h1>
        <p className="text-gray-600 mt-2">
          Here's an overview of your Subject Access Request cases and upcoming deadlines.
        </p>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Link
          to="/cases/new"
          className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow group"
        >
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
                <Plus className="w-5 h-5 text-primary-600" />
              </div>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-900 group-hover:text-primary-600">
                New SAR Case
              </h3>
              <p className="text-xs text-gray-500">Create a new request</p>
            </div>
          </div>
        </Link>

        <Link
          to="/calendar"
          className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow group"
        >
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-warning-100 rounded-lg flex items-center justify-center">
                <Calendar className="w-5 h-5 text-warning-600" />
              </div>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-900 group-hover:text-warning-600">
                View Calendar
              </h3>
              <p className="text-xs text-gray-500">Check deadlines</p>
            </div>
          </div>
        </Link>

        <Link
          to="/reports"
          className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow group"
        >
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-success-100 rounded-lg flex items-center justify-center">
                <BarChart3 className="w-5 h-5 text-success-600" />
              </div>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-900 group-hover:text-success-600">
                Generate Reports
              </h3>
              <p className="text-xs text-gray-500">Export case data</p>
            </div>
          </div>
        </Link>

        <Link
          to="/cases"
          className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow group"
        >
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                <FileText className="w-5 h-5 text-purple-600" />
              </div>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-900 group-hover:text-purple-600">
                View All Cases
              </h3>
              <p className="text-xs text-gray-500">Manage cases</p>
            </div>
          </div>
        </Link>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                <FileText className="w-5 h-5 text-blue-600" />
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Cases</p>
              <p className="text-2xl font-bold text-gray-900">{dashboardData?.total_cases || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-warning-100 rounded-lg flex items-center justify-center">
                <Clock className="w-5 h-5 text-warning-600" />
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Pending</p>
              <p className="text-2xl font-bold text-gray-900">{dashboardData?.pending_cases || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-danger-100 rounded-lg flex items-center justify-center">
                <AlertTriangle className="w-5 h-5 text-danger-600" />
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Overdue</p>
              <p className="text-2xl font-bold text-gray-900">{dashboardData?.overdue_cases || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-success-100 rounded-lg flex items-center justify-center">
                <CheckCircle className="w-5 h-5 text-success-600" />
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Completed</p>
              <p className="text-2xl font-bold text-gray-900">{dashboardData?.completed_cases || 0}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Upcoming Deadlines */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">Upcoming Deadlines</h3>
            <Link
              to="/calendar"
              className="text-sm text-primary-600 hover:text-primary-500 flex items-center"
            >
              View all
              <ArrowRight className="ml-1 w-4 h-4" />
            </Link>
          </div>
        </div>
        <div className="p-6">
          {upcomingDeadlines.length === 0 ? (
            <p className="text-gray-500 text-center py-4">No upcoming deadlines</p>
          ) : (
            <div className="space-y-3">
              {upcomingDeadlines.slice(0, 5).map((deadline) => (
                <div
                  key={deadline.sar_case_id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDeadlineColor(deadline.days_remaining, deadline.is_overdue)}`}>
                        {deadline.is_overdue ? 'Overdue' : `${deadline.days_remaining} days`}
                      </span>
                      <span className="text-sm font-medium text-gray-900">
                        {deadline.case_reference}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">
                      {deadline.organization_name} • {deadline.deadline_type} deadline
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900">
                      {new Date(deadline.deadline_date).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Organization Performance */}
      {organizationPerformance.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Organization Performance</h3>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {organizationPerformance.slice(0, 3).map((org) => (
                <div key={org.organization_name} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium text-gray-900">{org.organization_name}</h4>
                    {org.compliance_rating !== null && (
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        org.compliance_rating >= 80 ? 'bg-success-100 text-success-800' :
                        org.compliance_rating >= 60 ? 'bg-warning-100 text-warning-800' :
                        'bg-danger-100 text-danger-800'
                      }`}>
                        {org.compliance_rating.toFixed(0)}% compliant
                      </span>
                    )}
                  </div>
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <p className="text-gray-500">Total SARs</p>
                      <p className="font-medium text-gray-900">{org.total_sars}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">On Time</p>
                      <p className="font-medium text-success-600">{org.responded_on_time}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Late/Ignored</p>
                      <p className="font-medium text-danger-600">{org.responded_late + org.ignored}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
