import React from 'react';
import { useQuery } from '@tanstack/react-query';

function GuardrailMetrics() {
  const { data: metrics, isLoading } = useQuery({
    queryKey: ['guardrailMetrics'],
    queryFn: async () => {
      const response = await fetch('/api/guardrails/metrics');
      if (!response.ok) throw new Error('Failed to fetch metrics');
      return response.json();
    },
    refetchInterval: 10000, // Poll every 10 seconds
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="spinner mr-2" />
        <span className="text-gray-500">Loading guardrail metrics...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <table className="data-table">
          <thead>
            <tr>
              <th>Guardrail</th>
              <th>Type</th>
              <th>Status</th>
              <th>Total Checks</th>
              <th>Blocks</th>
              <th>Warnings</th>
              <th>Avg Response</th>
              <th>Error Rate</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {metrics?.map((metric) => (
              <tr key={metric.name}>
                <td className="font-medium">{metric.name}</td>
                <td>
                  <span className={`status-badge ${metric.type === 'ai' ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'}`}>
                    {metric.type}
                  </span>
                </td>
                <td>
                  <span className={`status-badge ${metric.enabled ? 'healthy' : 'bg-gray-100 text-gray-800'}`}>
                    {metric.enabled ? 'Enabled' : 'Disabled'}
                  </span>
                </td>
                <td className="text-center">{metric.total_checks}</td>
                <td className="text-center text-red-600">{metric.blocks}</td>
                <td className="text-center text-yellow-600">{metric.warnings}</td>
                <td className="text-center">{metric.avg_response_ms.toFixed(1)}ms</td>
                <td className="text-center">{(metric.error_rate * 100).toFixed(1)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Top Blockers</h3>
          <div className="space-y-3">
            {metrics?.filter(m => m.blocks > 0)
              .sort((a, b) => b.blocks - a.blocks)
              .slice(0, 5)
              .map(metric => (
                <div key={metric.name} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">{metric.name}</span>
                  <div className="flex items-center">
                    <div className="w-32 bg-gray-200 rounded-full h-2 mr-2">
                      <div 
                        className="bg-red-500 h-2 rounded-full"
                        style={{ width: `${(metric.blocks / Math.max(...metrics.map(m => m.blocks))) * 100}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium">{metric.blocks}</span>
                  </div>
                </div>
              ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Performance Leaders</h3>
          <div className="space-y-3">
            {metrics?.filter(m => m.enabled)
              .sort((a, b) => a.avg_response_ms - b.avg_response_ms)
              .slice(0, 5)
              .map(metric => (
                <div key={metric.name} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">{metric.name}</span>
                  <span className="text-sm font-medium text-green-600">
                    {metric.avg_response_ms.toFixed(1)}ms
                  </span>
                </div>
              ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default GuardrailMetrics;