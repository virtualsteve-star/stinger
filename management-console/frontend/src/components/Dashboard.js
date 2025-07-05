import React from 'react';
import { formatDistanceToNow } from 'date-fns';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { useMetricsHistory, useGuardrailMetrics } from '../hooks/useMetrics';

function Dashboard() {
  const { currentStats: stats, history } = useMetricsHistory(5000);
  const { data: guardrailMetrics } = useGuardrailMetrics();

  if (!stats) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="spinner mr-2" />
        <span className="text-gray-500">Loading dashboard...</span>
      </div>
    );
  }

  // Format chart data from history
  const chartData = history.length > 0 ? history.map((point, idx) => ({
    time: idx % 12 === 0 ? point.time : '', // Show time every minute
    requests: point.total,
    blocked: point.blocked,
  })) : [];

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div className="metric-card">
          <div className="metric-value">{stats?.total_requests || 0}</div>
          <div className="metric-label">Total Requests</div>
          {stats?.last_activity && (
            <div className="text-xs text-gray-400 mt-2">
              Last: {formatDistanceToNow(new Date(stats.last_activity))} ago
            </div>
          )}
        </div>

        <div className="metric-card">
          <div className="metric-value text-red-600">{stats?.blocked_requests || 0}</div>
          <div className="metric-label">Blocked Requests</div>
          <div className="text-sm text-gray-600 mt-2">
            {stats?.block_rate || 0}% block rate
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-value text-blue-600">{stats?.active_conversations || 0}</div>
          <div className="metric-label">Active Conversations</div>
        </div>

        <div className="metric-card">
          <div className="metric-value text-green-600">
            {stats?.uptime_seconds ? Math.floor(stats.uptime_seconds / 60) : 0}m
          </div>
          <div className="metric-label">Uptime</div>
        </div>
      </div>

      {/* Request Volume Chart */}
      <div className="chart-container">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Request Volume (Last Hour)</h3>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip />
            <Line 
              type="monotone" 
              dataKey="requests" 
              stroke="#3b82f6" 
              strokeWidth={2}
              name="Total"
            />
            <Line 
              type="monotone" 
              dataKey="blocked" 
              stroke="#ef4444" 
              strokeWidth={2}
              name="Blocked"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Additional Charts */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Guardrail Distribution */}
        <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Guardrail Types</h3>
          {guardrailMetrics && (
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={[
                    { name: 'AI-Powered', value: guardrailMetrics.filter(g => g.type === 'ai').length },
                    { name: 'Local', value: guardrailMetrics.filter(g => g.type === 'local').length },
                  ]}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  <Cell fill="#8b5cf6" />
                  <Cell fill="#3b82f6" />
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          )}
          <div className="flex justify-center gap-4 mt-4">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-purple-500 rounded-full mr-2" />
              <span className="text-sm">AI-Powered</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-blue-500 rounded-full mr-2" />
              <span className="text-sm">Local</span>
            </div>
          </div>
        </div>

        {/* Quick Insights */}
        <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Insights</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Total Guardrails</span>
              <span className="text-sm font-medium">{guardrailMetrics?.length || 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Enabled</span>
              <span className="text-sm font-medium">
                {guardrailMetrics?.filter(g => g.enabled).length || 0}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Block Rate Trend</span>
              <span className="text-sm font-medium">
                {history.length > 1 && 
                  (history[history.length - 1].block_rate > history[0].block_rate ? '↑' : '↓')
                } {stats.block_rate}%
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Uptime</span>
              <span className="text-sm font-medium">
                {Math.floor(stats.uptime_seconds / 3600)}h {Math.floor((stats.uptime_seconds % 3600) / 60)}m
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;