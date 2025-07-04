import React from 'react';
import { useQuery } from '@tanstack/react-query';

function SystemHealth() {
  const { data: health, isLoading } = useQuery({
    queryKey: ['systemHealth'],
    queryFn: async () => {
      const response = await fetch('/api/health');
      if (!response.ok) throw new Error('Failed to fetch health');
      return response.json();
    },
    refetchInterval: 30000, // Poll every 30 seconds
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="spinner mr-2" />
        <span className="text-gray-500">Checking system health...</span>
      </div>
    );
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': return 'text-green-600';
      case 'degraded': return 'text-yellow-600';
      case 'unhealthy': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="space-y-6">
      {/* Overall Status */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">System Status</h3>
        <div className="flex items-center">
          <div className={`text-4xl font-bold ${getStatusColor(health?.status)}`}>
            {health?.status?.toUpperCase()}
          </div>
          <div className="ml-4">
            <p className="text-sm text-gray-500">
              {health?.guardrails_loaded} guardrails loaded
            </p>
          </div>
        </div>
      </div>

      {/* Component Status */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <div className="metric-card">
          <h4 className="text-sm font-medium text-gray-500 mb-2">Guardrails</h4>
          <div className="flex items-center">
            <span className={`status-badge ${health?.guardrails_loaded > 0 ? 'healthy' : 'unhealthy'}`}>
              {health?.guardrails_loaded > 0 ? 'Loaded' : 'Not Loaded'}
            </span>
            <span className="ml-2 text-sm text-gray-600">
              {health?.guardrails_loaded} active
            </span>
          </div>
        </div>

        <div className="metric-card">
          <h4 className="text-sm font-medium text-gray-500 mb-2">API Keys</h4>
          <span className={`status-badge ${health?.api_keys_valid ? 'healthy' : 'unhealthy'}`}>
            {health?.api_keys_valid ? 'Valid' : 'Invalid'}
          </span>
        </div>

        <div className="metric-card">
          <h4 className="text-sm font-medium text-gray-500 mb-2">Audit Trail</h4>
          <span className={`status-badge ${health?.audit_enabled ? 'healthy' : 'degraded'}`}>
            {health?.audit_enabled ? 'Enabled' : 'Disabled'}
          </span>
        </div>
      </div>

      {/* Errors */}
      {health?.errors?.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h4 className="text-sm font-medium text-red-800 mb-2">System Errors</h4>
          <ul className="list-disc list-inside space-y-1">
            {health.errors.map((error, index) => (
              <li key={index} className="text-sm text-red-700">{error}</li>
            ))}
          </ul>
        </div>
      )}

      {/* System Info */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">System Information</h3>
        <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <dt className="text-sm font-medium text-gray-500">Version</dt>
            <dd className="mt-1 text-sm text-gray-900">0.1.0a2</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Environment</dt>
            <dd className="mt-1 text-sm text-gray-900">Development</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Python Version</dt>
            <dd className="mt-1 text-sm text-gray-900">3.8+</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Console Port</dt>
            <dd className="mt-1 text-sm text-gray-900">8001</dd>
          </div>
        </dl>
      </div>
    </div>
  );
}

export default SystemHealth;