import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';

function LogExplorer() {
  const [filters, setFilters] = useState({
    event_type: '',
    guardrail: '',
    decision: ''
  });

  const { data: logs, isLoading } = useQuery({
    queryKey: ['auditLogs', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
      const response = await fetch(`/api/audit/search?${params}`);
      if (!response.ok) throw new Error('Failed to fetch logs');
      return response.json();
    },
  });

  // Export logs to CSV
  const exportToCSV = () => {
    if (!logs || logs.length === 0) return;

    const headers = ['Timestamp', 'Event Type', 'Conversation ID', 'Guardrail', 'Decision', 'Reason'];
    const rows = logs.map(log => [
      log.timestamp,
      log.event_type,
      log.conversation_id || '',
      log.guardrail || '',
      log.decision || '',
      log.reason || ''
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `stinger-audit-logs-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <select
            value={filters.event_type}
            onChange={(e) => setFilters({...filters, event_type: e.target.value})}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          >
            <option value="">All Events</option>
            <option value="guardrail_decision">Guardrail Decision</option>
            <option value="user_prompt">User Prompt</option>
            <option value="llm_response">LLM Response</option>
          </select>

          <select
            value={filters.decision}
            onChange={(e) => setFilters({...filters, decision: e.target.value})}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          >
            <option value="">All Decisions</option>
            <option value="block">Blocked</option>
            <option value="warn">Warning</option>
            <option value="allow">Allowed</option>
          </select>

          <div className="flex gap-2">
            <button
              onClick={() => setFilters({ event_type: '', guardrail: '', decision: '' })}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
            >
              Clear Filters
            </button>
            <button
              onClick={exportToCSV}
              disabled={!logs || logs.length === 0}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Export CSV
            </button>
          </div>
        </div>
      </div>

      {/* Logs */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        {isLoading ? (
          <div className="p-6 text-center">
            <div className="spinner mx-auto" />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Event</th>
                  <th>Conversation</th>
                  <th>Guardrail</th>
                  <th>Decision</th>
                  <th>Reason</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {logs?.map((log, index) => (
                  <tr key={index}>
                    <td className="text-xs">{new Date(log.timestamp).toLocaleString()}</td>
                    <td>{log.event_type}</td>
                    <td className="text-xs">{log.conversation_id}</td>
                    <td>{log.guardrail || '-'}</td>
                    <td>
                      {log.decision && (
                        <span className={`status-badge ${
                          log.decision === 'block' ? 'bg-red-100 text-red-800' :
                          log.decision === 'warn' ? 'degraded' :
                          'healthy'
                        }`}>
                          {log.decision}
                        </span>
                      )}
                    </td>
                    <td className="text-xs">{log.reason || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default LogExplorer;