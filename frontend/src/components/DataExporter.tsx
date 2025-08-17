import React from 'react';
import { Download, FileText, Database } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const DataExporter: React.FC = () => {
  const { localData, isLocalMode } = useAuth();

  const exportToJSON = () => {
    if (!localData) return;

    const dataStr = JSON.stringify(localData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `sar-data-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const exportToCSV = () => {
    if (!localData?.sar_cases) return;

    const cases = localData.sar_cases;
    if (cases.length === 0) return;

    // Get headers from first case
    const headers = Object.keys(cases[0]);
    
    // Create CSV content
    const csvContent = [
      headers.join(','),
      ...cases.map((caseItem) => 
        headers.map(header => {
          const value = caseItem[header as keyof typeof caseItem];
          if (value === null || value === undefined) return '';
          if (typeof value === 'object') return JSON.stringify(value);
          return String(value).replace(/"/g, '""');
        }).join(',')
      )
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `sar-cases-${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  if (!isLocalMode || !localData) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Export Your Data</h3>
      
      <div className="space-y-3">
        <button
          onClick={exportToJSON}
          className="w-full flex items-center justify-center space-x-2 px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <FileText className="w-4 h-4" />
          <span>Export as JSON</span>
        </button>
        
        <button
          onClick={exportToCSV}
          className="w-full flex items-center justify-center space-x-2 px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <Database className="w-4 h-4" />
          <span>Export as CSV</span>
        </button>
      </div>
      
      <div className="mt-4 text-xs text-gray-500">
        <p>Export your data to backup or share with others.</p>
        <p>JSON format preserves all data structure, CSV is good for spreadsheet analysis.</p>
      </div>
    </div>
  );
};

export default DataExporter;
