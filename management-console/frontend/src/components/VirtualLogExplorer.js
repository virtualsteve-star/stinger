import React, { useState, useCallback, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { FixedSizeList as List } from 'react-window';

function VirtualLogExplorer() {
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
      const response = await fetch(`/api/audit/search?${params}&limit=1000`);
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

  // Memoize row renderer
  const Row = useCallback(({ index, style }) => {
    const log = logs[index];
    const isEvenRow = index % 2 === 0;
    
    return (
      <div 
        style={style} 
        className={`flex items-center px-4 py-2 border-b border-gray-100 hover:bg-gray-50 ${isEvenRow ? 'bg-gray-50' : 'bg-white'}`}
      >
        <div className="flex-1 grid grid-cols-6 gap-4 text-sm">
          <div className="text-xs text-gray-600">
            {new Date(log.timestamp).toLocaleString()}
          </div>
          <div className="font-medium">{log.event_type}</div>
          <div className="text-xs text-gray-500">{log.conversation_id || '-'}</div>
          <div>{log.guardrail || '-'}</div>
          <div>
            {log.decision && (
              <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                log.decision === 'block' ? 'bg-red-100 text-red-800' :
                log.decision === 'warn' ? 'bg-yellow-100 text-yellow-800' :
                'bg-green-100 text-green-800'
              }`}>
                {log.decision}
              </span>
            )}
          </div>
          <div className="text-xs text-gray-600 truncate" title={log.reason}>
            {log.reason || '-'}
          </div>
        </div>
      </div>
    );
  }, [logs]);

  // Calculate list height
  const listHeight = useMemo(() => {
    const maxHeight = window.innerHeight - 400; // Leave room for header/filters
    return Math.min(maxHeight, 600);
  }, []);

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

      {/* Virtual Scrolling Logs Table */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        {/* Table Header */}
        <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
          <div className="grid grid-cols-6 gap-4 text-xs font-medium text-gray-500 uppercase tracking-wider">
            <div>Timestamp</div>
            <div>Event</div>
            <div>Conversation</div>
            <div>Guardrail</div>
            <div>Decision</div>
            <div>Reason</div>
          </div>
        </div>

        {/* Table Body with Virtual Scrolling */}
        {isLoading ? (
          <div className="p-6 text-center">
            <div className="spinner mx-auto" />
          </div>
        ) : logs && logs.length > 0 ? (
          <List
            height={listHeight}
            itemCount={logs.length}
            itemSize={48}
            width="100%"
          >
            {Row}
          </List>
        ) : (
          <div className="p-6 text-center text-gray-500">
            No logs found matching the current filters
          </div>
        )}

        {/* Log Count */}
        {logs && logs.length > 0 && (
          <div className="bg-gray-50 px-4 py-2 border-t border-gray-200 text-sm text-gray-600">
            Showing {logs.length} log entries
            {logs.length >= 1000 && ' (limit reached)'}
          </div>
        )}
      </div>
    </div>
  );
}

export default VirtualLogExplorer;