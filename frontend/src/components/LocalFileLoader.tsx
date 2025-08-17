import React, { useState, useRef } from 'react';
import { Upload, FileText, AlertCircle, CheckCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const LocalFileLoader: React.FC = () => {
  const { loadLocalFile, localData, isLocalMode } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      await loadLocalFile(file);
      setSuccess(true);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load file');
      setSuccess(false);
    } finally {
      setLoading(false);
    }
  };

  const handleDrop = async (event: React.DragEvent) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (!file) return;

    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      await loadLocalFile(file);
      setSuccess(true);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load file');
      setSuccess(false);
    } finally {
      setLoading(false);
    }
  };

  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault();
  };

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  if (isLocalMode && localData) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-center space-x-3">
          <CheckCircle className="w-5 h-5 text-green-600" />
          <div>
            <h3 className="text-sm font-medium text-green-800">Local File Loaded</h3>
            <p className="text-sm text-green-600">
              {localData.sar_cases?.length || 0} SAR cases loaded from local file
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
      <div className="space-y-4">
        <div className="flex justify-center">
          <FileText className="w-12 h-12 text-gray-400" />
        </div>
        
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Load Your SAR Data
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            Upload a JSON file containing your SAR cases to work offline
          </p>
        </div>

        <div
          className="border-2 border-dashed border-blue-300 rounded-lg p-6 bg-blue-50 hover:bg-blue-100 transition-colors cursor-pointer"
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onClick={openFileDialog}
        >
          <Upload className="w-8 h-8 text-blue-500 mx-auto mb-2" />
          <p className="text-sm text-blue-600 font-medium">
            Drop your JSON file here or click to browse
          </p>
          <p className="text-xs text-blue-500 mt-1">
            Supports .json files with SAR case data
          </p>
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept=".json"
          onChange={handleFileSelect}
          className="hidden"
        />

        {loading && (
          <div className="flex items-center justify-center space-x-2 text-blue-600">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
            <span className="text-sm">Loading file...</span>
          </div>
        )}

        {error && (
          <div className="flex items-center space-x-2 text-red-600 bg-red-50 p-3 rounded-lg">
            <AlertCircle className="w-4 h-4" />
            <span className="text-sm">{error}</span>
          </div>
        )}

        {success && (
          <div className="flex items-center space-x-2 text-green-600 bg-green-50 p-3 rounded-lg">
            <CheckCircle className="w-4 h-4" />
            <span className="text-sm">File loaded successfully!</span>
          </div>
        )}

        <div className="text-xs text-gray-500">
          <p>Your data stays on your device and is never uploaded to our servers.</p>
          <p>Expected format: JSON file with a "sar_cases" array containing your case data.</p>
          
          <div className="mt-3 pt-3 border-t border-gray-200">
            <button
              onClick={() => {
                const link = document.createElement('a');
                link.href = '/sar-template.json';
                link.download = 'sar-template.json';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
              }}
              className="text-blue-600 hover:text-blue-800 underline text-xs"
            >
              Download sample template
            </button>
            <span className="text-gray-400 mx-1">•</span>
            <span>Use this as a starting point for your data</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LocalFileLoader;
