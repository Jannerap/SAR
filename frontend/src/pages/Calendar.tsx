import React, { useState, useEffect, useCallback } from 'react';
import { Calendar as CalendarIcon, Plus, AlertTriangle, Clock, FileText } from 'lucide-react';
import axios from 'axios';

interface CalendarEvent {
  id: number;
  title: string;
  date: string;
  type: 'deadline' | 'reminder' | 'followup' | 'ico_deadline' | 'Case Creation';
  sar_case_id?: number;
  case_reference?: string;
  organization_name?: string;
  is_overdue: boolean;
  days_remaining: number;
  priority: 'high' | 'medium' | 'low';
}

interface CalendarDay {
  date: Date;
  events: CalendarEvent[];
  isCurrentMonth: boolean;
  isToday: boolean;
}

const Calendar: React.FC = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    console.log('Events state updated:', events);
  }, [events]);

  const fetchCalendarEvents = useCallback(async () => {
    try {
      setLoading(true);
      const startDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
      const endDate = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);
      
      // Try to fetch real calendar events from backend
      try {
        const response = await axios.get('/calendar/events', {
          params: {
            start_date: startDate.toISOString().split('T')[0],
            end_date: endDate.toISOString().split('T')[0]
          }
        });
        
        console.log('Calendar events response:', response.data);
        if (response.data && response.data.length > 0) {
          // Transform calendar events to match our event format
          const calendarEvents = response.data.map((event: any, index: number) => {
            // Parse the event date and convert to YYYY-MM-DD format
            let eventDate = event.event_date;
            if (typeof eventDate === 'string') {
              if (eventDate.includes('T')) {
                eventDate = eventDate.split('T')[0];
              }
            }
            
            console.log('Processing calendar event:', event.title, 'with date:', eventDate);
            
            return {
              id: event.id || index + 1,
              title: event.title,
              date: eventDate,
              type: event.event_type === 'Deadline' ? 'deadline' : 
                    event.event_type === 'Reminder' ? 'reminder' : 
                    event.event_type === 'Case Creation' ? 'Case Creation' : 'followup',
              sar_case_id: event.sar_case_id,
              case_reference: event.sar_case_id ? `SAR-${event.sar_case_id}` : undefined,
              organization_name: event.description || 'Unknown',
              is_overdue: event.is_overdue || false,
              days_remaining: event.days_remaining || 0,
              priority: event.is_overdue ? 'high' : 'medium'
            };
          });
          
          console.log('Transformed calendar events:', calendarEvents);
          setEvents(calendarEvents);
          return;
        }
      } catch (apiError) {
        console.log('Calendar API not available, using dashboard data');
      }
      
      // Fallback: Fetch dashboard data to get real case deadlines
      try {
        const dashboardResponse = await axios.get('/dashboard/deadlines?days=60');
        console.log('Dashboard deadlines response:', dashboardResponse.data);
        if (dashboardResponse.data && dashboardResponse.data.length > 0) {
          const realEvents = dashboardResponse.data.map((deadline: any, index: number) => {
            // Ensure the date is properly formatted
            let eventDate = deadline.deadline_date;
            console.log('Processing deadline:', deadline.case_reference, 'with date:', eventDate, 'type:', typeof eventDate);
            
            if (typeof eventDate === 'string') {
              // If it's already a string, ensure it's in YYYY-MM-DD format
              if (eventDate.includes('T')) {
                eventDate = eventDate.split('T')[0];
              }
            }
            
            console.log('Processed date:', eventDate);
            
            return {
              id: index + 1,
              title: `${deadline.deadline_type} Deadline`,
              date: eventDate,
              type: "deadline",
              sar_case_id: deadline.sar_case_id,
              case_reference: deadline.case_reference,
              organization_name: deadline.organization_name,
              is_overdue: deadline.is_overdue,
              days_remaining: deadline.days_remaining,
              priority: deadline.is_overdue ? 'high' : deadline.days_remaining <= 7 ? 'high' : deadline.days_remaining <= 14 ? 'medium' : 'low'
            };
          });
          console.log('Created real events:', realEvents);
          setEvents(realEvents);
          return;
        }
      } catch (dashboardError) {
        console.log('Dashboard API not available, using sample data');
      }
      
      // Final fallback: Load sample data for demonstration
      loadSampleEvents();
    } catch (error) {
      console.error('Error fetching calendar events:', error);
      // Load sample data for demonstration
      loadSampleEvents();
    } finally {
      setLoading(false);
    }
  }, [currentDate]);



  const loadSampleEvents = useCallback(() => {
    const sampleEvents: CalendarEvent[] = [
      {
        id: 1,
        title: "SAR Response Deadline",
        date: new Date(currentDate.getFullYear(), currentDate.getMonth(), 15).toISOString().split('T')[0],
        type: "deadline",
        sar_case_id: 1,
        case_reference: "SAR-2024-001",
        organization_name: "Tech Corp Ltd",
        is_overdue: false,
        days_remaining: 5,
        priority: "high"
      },
      {
        id: 2,
        title: "Follow-up Reminder",
        date: new Date(currentDate.getFullYear(), currentDate.getMonth(), 20).toISOString().split('T')[0],
        type: "followup",
        sar_case_id: 2,
        case_reference: "SAR-2024-002",
        organization_name: "Data Solutions Inc",
        is_overdue: false,
        days_remaining: 10,
        priority: "medium"
      },
      {
        id: 3,
        title: "ICO Escalation Deadline",
        date: new Date(currentDate.getFullYear(), currentDate.getMonth(), 25).toISOString().split('T')[0],
        type: "ico_deadline",
        sar_case_id: 3,
        case_reference: "SAR-2024-003",
        organization_name: "Global Services",
        is_overdue: false,
        days_remaining: 15,
        priority: "high"
      }
    ];
    setEvents(sampleEvents);
  }, [currentDate]);

  useEffect(() => {
    fetchCalendarEvents();
  }, [fetchCalendarEvents]);

  const getCalendarDays = (): CalendarDay[] => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    const firstDay = new Date(year, month, 1);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDay.getDay());
    
    const days: CalendarDay[] = [];
    const currentDateObj = new Date();
    
    for (let i = 0; i < 42; i++) {
      const date = new Date(startDate);
      date.setDate(startDate.getDate() + i);
      
      const dayEvents = events.filter(event => {
        try {
          // Ensure we have a valid date string
          if (!event.date || typeof event.date !== 'string') {
            return false;
          }
          
          // Parse the event date safely
          const eventDate = new Date(event.date);
          if (isNaN(eventDate.getTime())) {
            console.warn('Invalid event date:', event.date);
            return false;
          }
          
          return eventDate.toDateString() === date.toDateString();
        } catch (error) {
          console.warn('Error parsing event date:', event.date, error);
          return false;
        }
      });
      
      days.push({
        date,
        events: dayEvents,
        isCurrentMonth: date.getMonth() === month,
        isToday: date.toDateString() === currentDateObj.toDateString()
      });
    }
    
    return days;
  };

  const getEventTypeIcon = (type: string) => {
    switch (type) {
      case 'deadline':
        return <Clock className="w-4 h-4" />;
      case 'reminder':
        return <AlertTriangle className="w-4 h-4" />;
      case 'followup':
        return <Plus className="w-4 h-4" />;
      case 'ico_deadline':
        return <AlertTriangle className="w-4 h-4" />;
      case 'Case Creation':
        return <FileText className="w-4 h-4" />;
      default:
        return <CalendarIcon className="w-4 h-4" />;
    }
  };

  const getEventTypeColor = (type: string) => {
    switch (type) {
      case 'deadline':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'reminder':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'followup':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'ico_deadline':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'Case Creation':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'border-l-4 border-l-red-500';
      case 'medium':
        return 'border-l-4 border-l-yellow-500';
      case 'low':
        return 'border-l-4 border-l-green-500';
      default:
        return '';
    }
  };

  const navigateMonth = (direction: 'prev' | 'next') => {
    setCurrentDate(prev => {
      const newDate = new Date(prev);
      if (direction === 'prev') {
        newDate.setMonth(prev.getMonth() - 1);
      } else {
        newDate.setMonth(prev.getMonth() + 1);
      }
      return newDate;
    });
  };

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', { 
      month: 'long', 
      year: 'numeric' 
    });
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
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Calendar</h1>
          <p className="text-gray-600 mt-1">Track deadlines, reminders, and important dates</p>
        </div>
        <button
          className="btn-primary flex items-center"
        >
          <Plus className="w-4 h-4 mr-2" />
          Add Event
        </button>
      </div>

      {/* Calendar Navigation */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <button
            onClick={() => navigateMonth('prev')}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          
          <h2 className="text-lg font-semibold text-gray-900">
            {formatDate(currentDate)}
          </h2>
          
          <button
            onClick={() => navigateMonth('next')}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>

      {/* Calendar Grid */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        {/* Day Headers */}
        <div className="grid grid-cols-7 bg-gray-50 border-b border-gray-200">
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
            <div key={day} className="px-3 py-2 text-center text-sm font-medium text-gray-500">
              {day}
            </div>
          ))}
        </div>
        
        {/* Calendar Days */}
        <div className="grid grid-cols-7">
          {getCalendarDays().map((day, index) => (
            <div
              key={index}
              className={`min-h-[120px] p-2 border-r border-b border-gray-200 ${
                !day.isCurrentMonth ? 'bg-gray-50' : ''
              } ${day.isToday ? 'bg-blue-50' : ''}`}
            >
              <div className={`text-sm font-medium mb-1 ${
                day.isCurrentMonth ? 'text-gray-900' : 'text-gray-400'
              } ${day.isToday ? 'text-blue-600' : ''}`}>
                {day.date.getDate()}
              </div>
              
              {/* Events for this day */}
              <div className="space-y-1">
                {day.events.slice(0, 3).map(event => {
                  console.log('Rendering event:', event.title, 'for date:', event.date);
                  return (
                    <div
                      key={event.id}
                      className={`text-xs p-1 rounded border ${getEventTypeColor(event.type)} ${getPriorityColor(event.priority)} cursor-pointer hover:opacity-80 transition-opacity`}

                    >
                      <div className="flex items-center space-x-1">
                        {getEventTypeIcon(event.type)}
                        <span className="truncate">{event.title}</span>
                      </div>
                      {event.is_overdue && (
                        <div className="text-red-600 font-medium">OVERDUE</div>
                      )}
                    </div>
                  );
                })}
                
                {day.events.length > 3 && (
                  <div className="text-xs text-gray-500 text-center">
                    +{day.events.length - 3} more
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Upcoming Deadlines */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Upcoming Deadlines</h3>
        </div>
        <div className="p-6">
          {events
            .filter(event => !event.is_overdue)
            .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
            .slice(0, 5)
            .map(event => (
              <div key={event.id} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-b-0">
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-lg ${getEventTypeColor(event.type)}`}>
                    {getEventTypeIcon(event.type)}
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">{event.title}</div>
                    <div className="text-sm text-gray-500">
                      {event.case_reference} • {event.organization_name}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium text-gray-900">
                    {new Date(event.date).toLocaleDateString()}
                  </div>
                  <div className="text-xs text-gray-500">
                    {event.days_remaining} days remaining
                  </div>
                </div>
              </div>
            ))}
        </div>
      </div>

      {/* Overdue Items */}
      {events.filter(event => event.is_overdue).length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-3">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            <h3 className="text-lg font-medium text-red-900">Overdue Items</h3>
          </div>
          <div className="space-y-2">
            {events
              .filter(event => event.is_overdue)
              .map(event => (
                <div key={event.id} className="flex items-center justify-between p-3 bg-white rounded-lg border border-red-200">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-red-100 rounded-lg">
                      {getEventTypeIcon(event.type)}
                    </div>
                    <div>
                      <div className="font-medium text-red-900">{event.title}</div>
                      <div className="text-sm text-red-600">
                        {event.case_reference} • {event.organization_name}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium text-red-900">
                      {new Date(event.date).toLocaleDateString()}
                    </div>
                    <div className="text-xs text-red-600">OVERDUE</div>
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Calendar;
