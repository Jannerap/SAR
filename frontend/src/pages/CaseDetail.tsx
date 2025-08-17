import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  Edit, 
  Trash2, 
  Plus, 
  Clock, 
  AlertTriangle, 
  CheckCircle, 
  FileText, 
  Download,
  Upload,
  X,
  Phone,
  Mail,
  Globe,
  User,
  Calendar as CalendarIcon
} from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

interface SARCase {
  id: number;
  case_reference: string;
  organization_name: string;
  organization_address: string;
  organization_email: string;
  organization_phone: string;
  data_administrator_name: string;
  data_controller_name: string;
  request_type: string;
  request_description: string;
  submission_date: string;
  submission_method: string;
  statutory_deadline: string;
  extended_deadline?: string;
  custom_deadline?: string;
  status: string;
  response_received: boolean;
  response_date?: string;
  response_summary?: string;
  data_provided?: boolean;
  data_complete?: boolean;
  data_format?: string;
  created_at: string;
  updated_at: string;
}

interface CaseUpdate {
  id: number;
  update_type: string;
  title: string;
  content: string;
  correspondence_date: string;
  correspondence_method: string;
  correspondence_summary?: string;
  call_duration?: number;
  call_participants?: string;
  call_transcript?: string;
  created_at: string;
}

interface CaseFile {
  id: number;
  filename: string;
  file_path: string;
  file_type: string;
  file_size: number;
  uploaded_at: string;
}

const CaseDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [caseData, setCaseData] = useState<SARCase | null>(null);
  const [updates, setUpdates] = useState<CaseUpdate[]>([]);
  const [files, setFiles] = useState<CaseFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [showUpdateModal, setShowUpdateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [letterFormat, setLetterFormat] = useState<'pdf' | 'txt'>('pdf');
  const [uploadingFiles, setUploadingFiles] = useState(false);
  const [newUpdate, setNewUpdate] = useState({
    update_type: 'Correspondence',
    title: '',
    content: '',
    correspondence_date: new Date().toISOString().split('T')[0],
    correspondence_method: 'Email',
    correspondence_summary: '',
    call_duration: 0,
    call_participants: '',
    call_transcript: ''
  });
  const [editData, setEditData] = useState({
    organization_name: '',
    organization_email: '',
    organization_phone: '',
    organization_address: '',
    data_administrator_name: '',
    data_controller_name: '',
    request_description: '',
    custom_deadline: ''
  });



  const fetchCaseData = useCallback(async () => {
    try {
      const response = await axios.get(`/sar/${id}`);
      setCaseData(response.data);
    } catch (error) {
      console.error('Error fetching case data:', error);
      toast.error('Failed to load case details');
    } finally {
      setLoading(false);
    }
  }, [id]);

  const fetchCaseUpdates = useCallback(async () => {
    try {
      const response = await axios.get(`/sar/${id}/updates`);
      setUpdates(response.data);
    } catch (error) {
      console.error('Error fetching case updates:', error);
    }
  }, [id]);

  const fetchCaseFiles = useCallback(async () => {
    try {
      const response = await axios.get(`/sar/${id}/files`);
      setFiles(response.data);
    } catch (error) {
      console.error('Error fetching case files:', error);
    }
  }, [id]);

  useEffect(() => {
    if (id) {
      fetchCaseData();
      fetchCaseUpdates();
      fetchCaseFiles();
    }
  }, [id, fetchCaseData, fetchCaseUpdates, fetchCaseFiles]);

  const handleCreateUpdate = async () => {
    if (!caseData) return;
    
    try {
      const updateData = {
        sar_case_id: caseData.id,
        update_type: newUpdate.update_type,
        title: newUpdate.title,
        content: newUpdate.content,
        correspondence_date: newUpdate.correspondence_date
      };

      const response = await axios.post(`/sar/${caseData.id}/updates`, updateData);
      
      // If there are files, upload them
      if (selectedFiles.length > 0) {
        await uploadFiles(response.data.id);
      }

      // Refresh updates
      fetchCaseUpdates();
      
      // Reset form
      setNewUpdate({
        update_type: 'Correspondence',
        title: '',
        content: '',
        correspondence_date: new Date().toISOString().split('T')[0],
        correspondence_method: 'Email',
        correspondence_summary: '',
        call_duration: 0,
        call_participants: '',
        call_transcript: ''
      });
      setSelectedFiles([]);
      setShowUpdateModal(false);
      
      toast.success('Update created successfully');
    } catch (error) {
      console.error('Error creating update:', error);
      toast.error('Failed to create update');
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    setSelectedFiles(prev => [...prev, ...files]);
  };

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const uploadFiles = async (updateId: number) => {
    if (!caseData) return;
    
    setUploadingFiles(true);
    try {
      for (const file of selectedFiles) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('update_id', updateId.toString());
        
        await axios.post(`/sar/${caseData.id}/files`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
      }
      toast.success(`${selectedFiles.length} file(s) uploaded successfully`);
    } catch (error) {
      console.error('Error uploading files:', error);
      toast.error('Failed to upload some files');
    } finally {
      setUploadingFiles(false);
    }
  };

  const handleEditCase = async () => {
    try {
      await axios.put(`/sar/${id}`, editData);
      toast.success('Case updated successfully');
      setShowEditModal(false);
      fetchCaseData(); // Refresh case data
    } catch (error) {
      console.error('Error updating case:', error);
      toast.error('Failed to update case');
    }
  };

  const handleDeleteCase = async () => {
    try {
      await axios.delete(`/sar/${id}`);
      toast.success('Case deleted successfully');
      navigate('/cases'); // Redirect to cases list
    } catch (error) {
      console.error('Error deleting case:', error);
      toast.error('Failed to delete case');
    }
  };

  const openEditModal = () => {
    setEditData({
      organization_name: caseData?.organization_name || '',
      organization_email: caseData?.organization_email || '',
      organization_phone: caseData?.organization_phone || '',
      organization_address: caseData?.organization_address || '',
      data_administrator_name: caseData?.data_administrator_name || '',
      data_controller_name: caseData?.data_controller_name || '',
      request_description: caseData?.request_description || '',
      custom_deadline: caseData?.custom_deadline ? caseData.custom_deadline.split('T')[0] : ''
    });
    setShowEditModal(true);
  };

  const openDeleteModal = () => {
    setShowDeleteModal(true);
  };

  const generateCaseReport = async (caseData: SARCase) => {
    try {
      const response = await axios.get(`/reports/case/${caseData.id}`);
      
      // Create a formatted report from the JSON data
      const reportData = response.data;
      
      // Create a formatted text report
      const reportContent = `SAR CASE REPORT

Case Reference: ${reportData.case_reference}
Organization: ${reportData.organization_name}
Request Type: ${reportData.request_type}
Status: ${reportData.status}
Submission Date: ${reportData.submission_date ? new Date(reportData.submission_date).toLocaleDateString() : 'N/A'}

DEADLINES:
- Statutory Deadline: ${reportData.deadlines.statutory ? new Date(reportData.deadlines.statutory).toLocaleDateString() : 'N/A'}
- Custom Deadline: ${reportData.deadlines.custom ? new Date(reportData.deadlines.custom).toLocaleDateString() : 'N/A'}
- Extended Deadline: ${reportData.deadlines.extended ? new Date(reportData.deadlines.extended).toLocaleDateString() : 'N/A'}

CASE UPDATES:
${reportData.updates.length > 0 ? reportData.updates.map((update: any) => 
  `- ${new Date(update.date).toLocaleDateString()}: ${update.description}`
).join('\n') : 'No updates recorded'}

ATTACHED FILES:
${reportData.files.length > 0 ? reportData.files.map((file: any) => 
  `- ${file.filename} (uploaded: ${new Date(file.uploaded_at).toLocaleDateString()})`
).join('\n') : 'No files attached'}

---
Report generated: ${new Date(reportData.generated_at).toLocaleString()}
Generated by SAR Tracking System`;

      // Create and download the text file
      const blob = new Blob([reportContent], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${caseData.case_reference}-Report.txt`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success('Report generated successfully');
    } catch (error) {
      console.error('Error generating report:', error);
      toast.error('Failed to generate report');
    }
  };



  const generateSARLetter = async (caseData: SARCase) => {
    try {
      const response = await axios.get(`/reports/sar-letter/${caseData.id}?format=${letterFormat}`, {
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const extension = letterFormat === 'pdf' ? 'pdf' : 'txt';
      link.setAttribute('download', `${caseData.case_reference}-SAR-Letter.${extension}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success(`SAR Letter generated successfully as ${letterFormat.toUpperCase()}`);
    } catch (error) {
      console.error('Error generating SAR letter:', error);
      toast.error('Failed to generate SAR letter');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Pending': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'Overdue': return 'bg-red-100 text-red-800 border-red-200';
      case 'Complete': return 'bg-green-100 text-green-800 border-green-200';
      case 'Escalated': return 'bg-purple-100 text-purple-800 border-purple-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'Pending': return <Clock className="w-4 h-4" />;
      case 'Overdue': return <AlertTriangle className="w-4 h-4" />;
      case 'Complete': return <CheckCircle className="w-4 h-4" />;
      case 'Escalated': return <AlertTriangle className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  const calculateDaysRemaining = (deadline: string) => {
    const today = new Date();
    const deadlineDate = new Date(deadline);
    const diffTime = deadlineDate.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!caseData) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold text-gray-900">Case not found</h2>
        <p className="text-gray-600 mt-2">The requested case could not be found.</p>
        <button
          onClick={() => navigate('/cases')}
          className="btn-primary mt-4"
        >
          Back to Cases
        </button>
      </div>
    );
  }

  const daysRemaining = calculateDaysRemaining(caseData.statutory_deadline);
  const isOverdue = daysRemaining < 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/cases')}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {caseData.case_reference}
            </h1>
            <p className="text-gray-600">{caseData.organization_name}</p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getStatusColor(caseData.status)}`}>
            <div className="flex items-center space-x-1">
              {getStatusIcon(caseData.status)}
              <span>{caseData.status}</span>
            </div>
          </span>
          <button
            onClick={() => setShowUpdateModal(true)}
            className="btn-primary flex items-center"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Update
          </button>
        </div>
      </div>

      {/* Case Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Case Information */}
        <div className="lg:col-span-2 space-y-6">
          {/* Basic Details */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Case Details</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-500">Request Type</label>
                <p className="text-gray-900">{caseData.request_type}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">Submission Method</label>
                <p className="text-gray-900">{caseData.submission_method}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">Submission Date</label>
                <p className="text-gray-900">{formatDate(caseData.submission_date)}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">Status</label>
                <p className="text-gray-900">{caseData.status}</p>
              </div>
            </div>
            <div className="mt-4">
              <label className="text-sm font-medium text-gray-500">Request Description</label>
              <p className="text-gray-900 mt-1">{caseData.request_description}</p>
            </div>
          </div>

          {/* Organization Information */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Organization Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center space-x-2">
                <User className="w-4 h-4 text-gray-400" />
                <span className="text-gray-900">{caseData.organization_name}</span>
              </div>
              {caseData.organization_email && (
                <div className="flex items-center space-x-2">
                  <Mail className="w-4 h-4 text-gray-400" />
                  <span className="text-gray-900">{caseData.organization_email}</span>
                </div>
              )}
              {caseData.organization_phone && (
                <div className="flex items-center space-x-2">
                  <Phone className="w-4 h-4 text-gray-400" />
                  <span className="text-gray-900">{caseData.organization_phone}</span>
                </div>
              )}
              {caseData.organization_address && (
                <div className="flex items-center space-x-2">
                  <Globe className="w-4 h-4 text-gray-400" />
                  <span className="text-gray-900">{caseData.organization_address}</span>
                </div>
              )}
              {caseData.data_administrator_name && (
                <div className="flex items-center space-x-2">
                  <User className="w-4 h-4 text-gray-400" />
                  <span className="text-gray-900">Data Admin: {caseData.data_administrator_name}</span>
                </div>
              )}
              {caseData.data_controller_name && (
                <div className="flex items-center space-x-2">
                  <User className="w-4 h-4 text-gray-400" />
                  <span className="text-gray-900">Data Controller: {caseData.data_controller_name}</span>
                </div>
              )}
            </div>
          </div>

          {/* Case Updates */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">Case Updates</h3>
              <button
                onClick={() => setShowUpdateModal(true)}
                className="text-primary-600 hover:text-primary-700 text-sm font-medium"
              >
                View All
              </button>
            </div>
            <div className="space-y-4">
              {updates.slice(0, 3).map((update) => (
                <div key={update.id} className="border-l-4 border-l-primary-500 pl-4">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-gray-900">{update.title}</h4>
                    <span className="text-sm text-gray-500">{formatDate(update.created_at)}</span>
                  </div>
                  <p className="text-gray-600 text-sm mt-1">{update.content}</p>
                  <div className="flex items-center space-x-2 mt-2">
                    <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                      {update.update_type}
                    </span>
                    <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                      {update.correspondence_method}
                    </span>
                  </div>
                </div>
              ))}
              {updates.length === 0 && (
                <p className="text-gray-500 text-center py-4">No updates yet</p>
              )}
            </div>
          </div>

          {/* Case Files */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Case Files</h3>
            <div className="space-y-4">
              {files.length > 0 ? (
                files.map((file) => (
                  <div key={file.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <FileText className="w-4 h-4 text-gray-400" />
                      <span className="text-sm font-medium text-gray-900">{file.filename}</span>
                    </div>
                    <div className="text-xs text-gray-500">
                      {file.file_type} • {(file.file_size / 1024).toFixed(1)} KB
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-gray-500 text-center py-4">No files attached</p>
              )}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Deadlines */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Deadlines</h3>
            <div className="space-y-4">
              <div className={`p-3 rounded-lg border ${isOverdue ? 'bg-red-50 border-red-200' : 'bg-blue-50 border-blue-200'}`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <CalendarIcon className="w-4 h-4 text-blue-600" />
                    <span className="text-sm font-medium text-gray-900">Statutory Deadline</span>
                  </div>
                  <span className={`text-sm font-medium ${isOverdue ? 'text-red-600' : 'text-blue-600'}`}>
                    {formatDate(caseData.statutory_deadline)}
                  </span>
                </div>
                <div className="mt-2">
                  <span className={`text-xs ${isOverdue ? 'text-red-600' : 'text-blue-600'}`}>
                    {isOverdue ? `${Math.abs(daysRemaining)} days overdue` : `${daysRemaining} days remaining`}
                  </span>
                </div>
              </div>
              
              {caseData.custom_deadline && (
                <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-900">Custom Deadline</span>
                    <span className="text-sm text-yellow-600">{formatDate(caseData.custom_deadline)}</span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Response Status */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Response Status</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Response Received</span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  caseData.response_received 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {caseData.response_received ? 'Yes' : 'No'}
                </span>
              </div>
              {caseData.response_date && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Response Date</span>
                  <span className="text-sm text-gray-900">{formatDate(caseData.response_date)}</span>
                </div>
              )}
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Data Provided</span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  caseData.data_provided 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-gray-100 text-gray-600'
                }`}>
                  {caseData.data_provided ? 'Yes' : 'No'}
                </span>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <button 
                onClick={openEditModal}
                className="w-full btn-secondary flex items-center justify-center"
              >
                <Edit className="w-4 h-4 mr-2" />
                Edit Case
              </button>
              <button 
                onClick={() => generateCaseReport(caseData)}
                className="w-full btn-secondary flex items-center justify-center"
              >
                <FileText className="w-4 h-4 mr-2" />
                Generate Report
              </button>
              
              {/* SAR Letter Format Selector */}
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700 text-center">
                  SAR Letter Format
                </label>
                <div className="flex space-x-2">
                  <button
                    onClick={() => setLetterFormat('pdf')}
                    className={`flex-1 px-3 py-2 text-sm rounded-md border transition-colors ${
                      letterFormat === 'pdf'
                        ? 'bg-blue-600 text-white border-blue-600'
                        : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    PDF
                  </button>
                  <button
                    onClick={() => setLetterFormat('txt')}
                    className={`flex-1 px-3 py-2 text-sm rounded-md border transition-colors ${
                      letterFormat === 'txt'
                        ? 'bg-blue-600 text-white border-blue-600'
                        : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    TXT
                  </button>
                </div>
              </div>
              
              <button 
                onClick={() => generateSARLetter(caseData)}
                className="w-full btn-secondary flex items-center justify-center"
              >
                <FileText className="w-4 h-4 mr-2" />
                Generate SAR Letter ({letterFormat.toUpperCase()})
              </button>
              
              <button className="w-full btn-secondary flex items-center justify-center">
                <Download className="w-4 h-4 mr-2" />
                Export Data
              </button>
              <button 
                onClick={openDeleteModal}
                className="w-full bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors flex items-center justify-center"
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Delete Case
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Update Modal */}
      {showUpdateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl mx-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Add Case Update</h3>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Update Type</label>
                  <select
                    value={newUpdate.update_type}
                    onChange={(e) => setNewUpdate({...newUpdate, update_type: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  >
                    <option value="Correspondence">Correspondence</option>
                    <option value="Phone Call">Phone Call</option>
                    <option value="Meeting">Meeting</option>
                    <option value="Follow-up">Follow-up</option>
                    <option value="Escalation">Escalation</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Date</label>
                  <input
                    type="date"
                    value={newUpdate.correspondence_date}
                    onChange={(e) => setNewUpdate({...newUpdate, correspondence_date: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                <input
                  type="text"
                  value={newUpdate.title}
                  onChange={(e) => setNewUpdate({...newUpdate, title: e.target.value})}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Brief title for this update"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Content</label>
                <textarea
                  value={newUpdate.content}
                  onChange={(e) => setNewUpdate({...newUpdate, content: e.target.value})}
                  rows={4}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Detailed description of the update"
                />
              </div>
              
              {/* File Upload Section */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Attach Files</label>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-4">
                  <div className="text-center">
                    <Upload className="mx-auto h-8 w-8 text-gray-400 mb-2" />
                    <p className="text-sm text-gray-600 mb-2">
                      Drop files here or click to select
                    </p>
                    <input
                      type="file"
                      multiple
                      accept=".pdf,.png,.jpg,.jpeg,.gif,.doc,.docx,.txt,.eml,.msg"
                      onChange={handleFileSelect}
                      className="hidden"
                      id="file-upload"
                    />
                    <label
                      htmlFor="file-upload"
                      className="btn-secondary cursor-pointer inline-flex items-center"
                    >
                      <Upload className="w-4 h-4 mr-2" />
                      Select Files
                    </label>
                  </div>
                  
                  {/* Selected Files List */}
                  {selectedFiles.length > 0 && (
                    <div className="mt-4">
                      <h4 className="text-sm font-medium text-gray-700 mb-2">Selected Files:</h4>
                      <div className="space-y-2">
                        {selectedFiles.map((file, index) => (
                          <div key={index} className="flex items-center justify-between bg-gray-50 p-2 rounded">
                            <div className="flex items-center space-x-2">
                              <FileText className="w-4 h-4 text-gray-500" />
                              <span className="text-sm text-gray-700">{file.name}</span>
                              <span className="text-xs text-gray-500">
                                ({(file.size / 1024 / 1024).toFixed(2)} MB)
                              </span>
                            </div>
                            <button
                              onClick={() => removeFile(index)}
                              className="text-red-500 hover:text-red-700"
                            >
                              <X className="w-4 h-4" />
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
              
              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setShowUpdateModal(false)}
                  className="btn-secondary"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreateUpdate}
                  disabled={uploadingFiles}
                  className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {uploadingFiles ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Creating Update...
                    </>
                  ) : (
                    'Create Update'
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Edit Case Modal */}
      {showEditModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl mx-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Edit Case Details</h3>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Organization Name</label>
                  <input
                    type="text"
                    value={editData.organization_name}
                    onChange={(e) => setEditData({...editData, organization_name: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Organization Email</label>
                  <input
                    type="email"
                    value={editData.organization_email}
                    onChange={(e) => setEditData({...editData, organization_email: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Organization Phone</label>
                  <input
                    type="tel"
                    value={editData.organization_phone}
                    onChange={(e) => setEditData({...editData, organization_phone: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Custom Deadline</label>
                  <input
                    type="date"
                    value={editData.custom_deadline}
                    onChange={(e) => setEditData({...editData, custom_deadline: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Organization Address</label>
                <textarea
                  value={editData.organization_address}
                  onChange={(e) => setEditData({...editData, organization_address: e.target.value})}
                  rows={3}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Data Administrator Name</label>
                <input
                  type="text"
                  value={editData.data_administrator_name}
                  onChange={(e) => setEditData({...editData, data_administrator_name: e.target.value})}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="John Smith"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Data Controller Name</label>
                <input
                  type="text"
                  value={editData.data_controller_name}
                  onChange={(e) => setEditData({...editData, data_controller_name: e.target.value})}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Jane Doe"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Request Description</label>
                <textarea
                  value={editData.request_description}
                  onChange={(e) => setEditData({...editData, request_description: e.target.value})}
                  rows={4}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setShowEditModal(false)}
                  className="btn-secondary"
                >
                  Cancel
                </button>
                <button
                  onClick={handleEditCase}
                  className="btn-primary"
                >
                  Save Changes
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex items-center space-x-3 mb-4">
              <div className="p-2 bg-red-100 rounded-lg">
                <AlertTriangle className="w-6 h-6 text-red-600" />
              </div>
              <h3 className="text-lg font-medium text-gray-900">Delete Case</h3>
            </div>
            <p className="text-gray-600 mb-6">
              Are you sure you want to delete case <strong>{caseData?.case_reference}</strong>? 
              This action cannot be undone and will permanently remove all case data, updates, and files.
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowDeleteModal(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteCase}
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                Delete Case
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CaseDetail;
