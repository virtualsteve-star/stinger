import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

function DataRetention() {
  const queryClient = useQueryClient();
  const [retentionDays, setRetentionDays] = useState(7);
  const [metricsSampleRate, setMetricsSampleRate] = useState(100);

  // Get current retention settings
  const { data: settings } = useQuery({
    queryKey: ['retentionSettings'],
    queryFn: async () => {
      const response = await fetch('/api/settings/retention');
      if (!response.ok) throw new Error('Failed to fetch settings');
      return response.json();
    },
    onSuccess: (data) => {
      if (data) {
        setRetentionDays(data.retention_days || 7);
        setMetricsSampleRate(data.metrics_sample_rate || 100);
      }
    }
  });

  // Update retention settings
  const updateSettings = useMutation({
    mutationFn: async (newSettings) => {
      const response = await fetch('/api/settings/retention', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newSettings)
      });
      if (!response.ok) throw new Error('Failed to update settings');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['retentionSettings']);
      alert('Retention settings updated successfully');
    }
  });

  // Clear old data
  const clearOldData = useMutation({
    mutationFn: async () => {
      const response = await fetch('/api/maintenance/clear-old-data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ older_than_days: retentionDays })
      });
      if (!response.ok) throw new Error('Failed to clear data');
      return response.json();
    },
    onSuccess: (data) => {
      alert(`Cleared ${data.logs_deleted || 0} log entries and ${data.metrics_deleted || 0} metric records`);
    }
  });

  const handleSave = () => {
    updateSettings.mutate({
      retention_days: retentionDays,
      metrics_sample_rate: metricsSampleRate
    });
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Retention Settings */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Data Retention Settings</h3>
        
        <div className="space-y-4">
          {/* Log Retention */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Audit Log Retention (days)
            </label>
            <div className="flex items-center space-x-4">
              <input
                type="range"
                min="1"
                max="90"
                value={retentionDays}
                onChange={(e) => setRetentionDays(Number(e.target.value))}
                className="flex-1"
              />
              <span className="w-12 text-center font-medium">{retentionDays}</span>
            </div>
            <p className="mt-1 text-sm text-gray-500">
              Audit logs older than {retentionDays} days will be automatically deleted
            </p>
          </div>

          {/* Metrics Sample Rate */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Metrics Sample Rate (%)
            </label>
            <div className="flex items-center space-x-4">
              <input
                type="range"
                min="10"
                max="100"
                step="10"
                value={metricsSampleRate}
                onChange={(e) => setMetricsSampleRate(Number(e.target.value))}
                className="flex-1"
              />
              <span className="w-12 text-center font-medium">{metricsSampleRate}%</span>
            </div>
            <p className="mt-1 text-sm text-gray-500">
              Sample {metricsSampleRate}% of requests for detailed metrics collection
            </p>
          </div>

          {/* Save Button */}
          <div className="pt-4">
            <button
              onClick={handleSave}
              disabled={updateSettings.isLoading}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
            >
              {updateSettings.isLoading ? 'Saving...' : 'Save Settings'}
            </button>
          </div>
        </div>
      </div>

      {/* Data Management */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Data Management</h3>
        
        <div className="space-y-4">
          {/* Storage Stats */}
          <div className="bg-gray-50 rounded p-4">
            <h4 className="font-medium text-gray-700 mb-2">Storage Usage</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Audit Logs:</span>
                <span className="font-medium">2.4 GB</span>
              </div>
              <div className="flex justify-between">
                <span>Metrics Data:</span>
                <span className="font-medium">156 MB</span>
              </div>
              <div className="flex justify-between">
                <span>Total Usage:</span>
                <span className="font-medium">2.56 GB</span>
              </div>
            </div>
          </div>

          {/* Manual Cleanup */}
          <div>
            <h4 className="font-medium text-gray-700 mb-2">Manual Cleanup</h4>
            <p className="text-sm text-gray-600 mb-3">
              Manually clear data older than {retentionDays} days
            </p>
            <button
              onClick={() => {
                if (window.confirm(`This will delete all data older than ${retentionDays} days. Continue?`)) {
                  clearOldData.mutate();
                }
              }}
              disabled={clearOldData.isLoading}
              className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 disabled:opacity-50"
            >
              {clearOldData.isLoading ? 'Clearing...' : 'Clear Old Data'}
            </button>
          </div>
        </div>
      </div>

      {/* Retention Policy */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-medium text-blue-900 mb-2">📋 Retention Policy</h4>
        <ul className="space-y-1 text-sm text-blue-800">
          <li>• Audit logs are retained for {retentionDays} days</li>
          <li>• Metrics are aggregated hourly after 24 hours</li>
          <li>• Aggregated metrics are retained for 90 days</li>
          <li>• Automatic cleanup runs daily at 2 AM</li>
        </ul>
      </div>
    </div>
  );
}

export default DataRetention;