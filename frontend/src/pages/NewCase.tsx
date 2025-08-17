import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Save, ArrowLeft, Calendar, FileText, Building, Mail, Phone, AlertTriangle } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const NewCase: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    organization_name: '',
    organization_address: '',
    organization_email: '',
    organization_phone: '',
    organization_website: '',
    data_administrator_name: '',
    data_controller_name: '',
    request_type: 'Personal Data',
    request_description: '',
    submission_date: new Date().toISOString().split('T')[0],
    submission_method: 'Email',
    custom_deadline: '',
    urgency_level: 'Normal',
    estimated_data_volume: 'Small',
    special_categories: false,
    criminal_records: false,
    third_party_data: false,
    notes: ''
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<{[key: string]: string}>({});

  const validateForm = () => {
    const newErrors: {[key: string]: string} = {};
    
    if (!formData.organization_name.trim()) {
      newErrors.organization_name = 'Organization name is required';
    }
    
    if (!formData.request_description.trim()) {
      newErrors.request_description = 'Request description is required';
    }
    
    if (formData.request_description.trim().length < 20) {
      newErrors.request_description = 'Description must be at least 20 characters';
    }
    
    if (formData.organization_email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.organization_email)) {
      newErrors.organization_email = 'Invalid email format';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      toast.error('Please fix the errors in the form');
      return;
    }

    setLoading(true);

    try {
      const response = await axios.post('/sar/', formData);
      toast.success('SAR case created successfully!');
      navigate(`./cases/${response.data.id}`);
    } catch (error: any) {
      console.error('Error creating case:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to create case';
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'High':
        return 'text-red-600 bg-red-100';
      case 'Medium':
        return 'text-yellow-600 bg-yellow-100';
      case 'Normal':
        return 'text-green-600 bg-green-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getDataVolumeColor = (volume: string) => {
    switch (volume) {
      case 'Large':
        return 'text-red-600 bg-red-100';
      case 'Medium':
        return 'text-yellow-600 bg-yellow-100';
      case 'Small':
        return 'text-green-600 bg-green-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('./cases')}
            className="btn-secondary flex items-center"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Cases
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Create New SAR Case</h1>
            <p className="text-gray-600 mt-1">Submit a comprehensive Subject Access Request</p>
          </div>
        </div>
      </div>

      {/* Form */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Organization Information */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <Building className="w-5 h-5 mr-2 text-primary-600" />
              Organization Information
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="organization_name" className="label">
                  Organization Name *
                </label>
                <input
                  id="organization_name"
                  type="text"
                  required
                  className={`input ${errors.organization_name ? 'border-red-300' : ''}`}
                  value={formData.organization_name}
                  onChange={(e) => setFormData({...formData, organization_name: e.target.value})}
                  placeholder="e.g., Tech Corp Ltd"
                />
                {errors.organization_name && (
                  <p className="text-red-600 text-sm mt-1">{errors.organization_name}</p>
                )}
              </div>
              
              <div>
                <label htmlFor="organization_email" className="label">
                  Organization Email
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Mail className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="organization_email"
                    type="email"
                    className={`input pl-10 ${errors.organization_email ? 'border-red-300' : ''}`}
                    value={formData.organization_email}
                    onChange={(e) => setFormData({...formData, organization_email: e.target.value})}
                    placeholder="contact@organization.com"
                  />
                </div>
                {errors.organization_email && (
                  <p className="text-red-600 text-sm mt-1">{errors.organization_email}</p>
                )}
              </div>
              
              <div>
                <label htmlFor="organization_phone" className="label">
                  Organization Phone
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Phone className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="organization_phone"
                    type="tel"
                    className="input pl-10"
                    value={formData.organization_phone}
                    onChange={(e) => setFormData({...formData, organization_phone: e.target.value})}
                    placeholder="+44 123 456 7890"
                  />
                </div>
              </div>
              
              <div>
                <label htmlFor="organization_website" className="label">
                  Organization Website
                </label>
                <input
                  id="organization_website"
                  type="url"
                  className="input"
                  value={formData.organization_website}
                  onChange={(e) => setFormData({...formData, organization_website: e.target.value})}
                  placeholder="https://www.organization.com"
                />
              </div>
              
              <div className="md:col-span-2">
                <label htmlFor="organization_address" className="label">
                  Organization Address
                </label>
                <textarea
                  id="organization_address"
                  rows={3}
                  className="input"
                  value={formData.organization_address}
                  onChange={(e) => setFormData({...formData, organization_address: e.target.value})}
                  placeholder="Full address including postal code"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Data Administrator Name
                </label>
                <input
                  type="text"
                  name="data_administrator_name"
                  value={formData.data_administrator_name}
                  onChange={(e) => setFormData({...formData, data_administrator_name: e.target.value})}
                  className="input-field"
                  placeholder="John Smith"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Data Controller Name
                </label>
                <input
                  type="text"
                  name="data_controller_name"
                  value={formData.data_controller_name}
                  onChange={(e) => setFormData({...formData, data_controller_name: e.target.value})}
                  className="input-field"
                  placeholder="Jane Doe"
                />
              </div>
            </div>
          </div>

          {/* Request Details */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <FileText className="w-5 h-5 mr-2 text-primary-600" />
              Request Details
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="request_type" className="label">Request Type *</label>
                <select
                  id="request_type"
                  required
                  className="input"
                  value={formData.request_type}
                  onChange={(e) => setFormData({...formData, request_type: e.target.value})}
                >
                  <option value="Personal Data">Personal Data</option>
                  <option value="Special Categories">Special Categories</option>
                  <option value="Criminal Records">Criminal Records</option>
                  <option value="Third Party Data">Third Party Data</option>
                  <option value="FOIA">FOIA</option>
                  <option value="Other">Other</option>
                </select>
              </div>
              
              <div>
                <label htmlFor="submission_method" className="label">Submission Method *</label>
                <select
                  id="submission_method"
                  required
                  className="input"
                  value={formData.submission_method}
                  onChange={(e) => setFormData({...formData, submission_method: e.target.value})}
                >
                  <option value="Email">Email</option>
                  <option value="Post">Post</option>
                  <option value="Online Form">Online Form</option>
                  <option value="Phone">Phone</option>
                  <option value="In Person">In Person</option>
                </select>
              </div>
              
              <div>
                <label htmlFor="urgency_level" className="label">Urgency Level</label>
                <select
                  id="urgency_level"
                  className="input"
                  value={formData.urgency_level}
                  onChange={(e) => setFormData({...formData, urgency_level: e.target.value})}
                >
                  <option value="Normal">Normal</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                </select>
              </div>
              
              <div>
                <label htmlFor="estimated_data_volume" className="label">Estimated Data Volume</label>
                <select
                  id="estimated_data_volume"
                  className="input"
                  value={formData.estimated_data_volume}
                  onChange={(e) => setFormData({...formData, estimated_data_volume: e.target.value})}
                >
                  <option value="Small">Small (&lt; 100 records)</option>
                  <option value="Medium">Medium (100-1000 records)</option>
                  <option value="Large">Large (&gt; 1000 records)</option>
                </select>
              </div>
              
              <div>
                <label htmlFor="submission_date" className="label">Submission Date *</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Calendar className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="submission_date"
                    type="date"
                    required
                    className="input pl-10"
                    value={formData.submission_date}
                    onChange={(e) => setFormData({...formData, submission_date: e.target.value})}
                  />
                </div>
              </div>
              
              <div>
                <label htmlFor="custom_deadline" className="label">Custom Deadline (Optional)</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Calendar className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="custom_deadline"
                    type="date"
                    className="input pl-10"
                    value={formData.custom_deadline}
                    onChange={(e) => setFormData({...formData, custom_deadline: e.target.value})}
                  />
                </div>
              </div>
              
              <div className="md:col-span-2">
                <label htmlFor="request_description" className="label">Request Description *</label>
                <textarea
                  id="request_description"
                  rows={4}
                  required
                  className={`input ${errors.request_description ? 'border-red-300' : ''}`}
                  placeholder="Describe in detail what personal data you are requesting access to, including specific categories, time periods, and any other relevant details..."
                  value={formData.request_description}
                  onChange={(e) => setFormData({...formData, request_description: e.target.value})}
                />
                {errors.request_description && (
                  <p className="text-red-600 text-sm mt-1">{errors.request_description}</p>
                )}
                <p className="text-sm text-gray-500 mt-1">
                  Minimum 20 characters. Be specific about what data you're requesting.
                </p>
              </div>
            </div>
          </div>

          {/* Special Considerations */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <AlertTriangle className="w-5 h-5 mr-2 text-yellow-600" />
              Special Considerations
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  checked={formData.special_categories}
                  onChange={(e) => setFormData({...formData, special_categories: e.target.checked})}
                />
                <span className="text-sm text-gray-700">Special Categories Data</span>
              </label>
              
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  checked={formData.criminal_records}
                  onChange={(e) => setFormData({...formData, criminal_records: e.target.checked})}
                />
                <span className="text-sm text-gray-700">Criminal Records</span>
              </label>
              
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  checked={formData.third_party_data}
                  onChange={(e) => setFormData({...formData, third_party_data: e.target.checked})}
                />
                <span className="text-sm text-gray-700">Third Party Data</span>
              </label>
            </div>
          </div>

          {/* Additional Notes */}
          <div>
            <label htmlFor="notes" className="label">Additional Notes</label>
            <textarea
              id="notes"
              rows={3}
              className="input"
              placeholder="Any additional information, context, or special requests..."
              value={formData.notes}
              onChange={(e) => setFormData({...formData, notes: e.target.value})}
            />
          </div>

          {/* Form Summary */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-3">Form Summary</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-gray-500">Urgency:</span>
                <span className={`ml-2 px-2 py-1 rounded-full text-xs font-medium ${getUrgencyColor(formData.urgency_level)}`}>
                  {formData.urgency_level}
                </span>
              </div>
              <div>
                <span className="text-gray-500">Data Volume:</span>
                <span className={`ml-2 px-2 py-1 rounded-full text-xs font-medium ${getDataVolumeColor(formData.estimated_data_volume)}`}>
                  {formData.estimated_data_volume}
                </span>
              </div>
              <div>
                <span className="text-gray-500">Type:</span>
                <span className="ml-2 font-medium">{formData.request_type}</span>
              </div>
              <div>
                <span className="text-gray-500">Method:</span>
                <span className="ml-2 font-medium">{formData.submission_method}</span>
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end space-x-3">
                          <button
                type="button"
                onClick={() => navigate('./cases')}
                className="btn-secondary"
              >
                Cancel
              </button>
            <button
              type="submit"
              disabled={loading}
              className="btn-primary flex items-center"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Creating Case...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4 mr-2" />
                  Create SAR Case
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default NewCase;
