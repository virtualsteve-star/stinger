import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  AreaChart, Area, BarChart, Bar, ScatterChart, Scatter,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  Legend, Cell, RadarChart, PolarGrid, PolarAngleAxis, 
  PolarRadiusAxis, Radar
} from 'recharts';

const COLORS = ['#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444'];

function AdvancedAnalytics() {
  const [timeRange, setTimeRange] = useState('24h');
  const [chartType, setChartType] = useState('performance');

  // Fetch analytics data
  const { data: analytics } = useQuery({
    queryKey: ['analytics', timeRange],
    queryFn: async () => {
      const response = await fetch(`/api/analytics/advanced?range=${timeRange}`);
      if (!response.ok) throw new Error('Failed to fetch analytics');
      return response.json();
    },
    refetchInterval: 30000, // Refresh every 30s
  });

  // Performance over time chart
  const renderPerformanceChart = () => (
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={analytics?.performance_timeline || []}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="time" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Area 
          type="monotone" 
          dataKey="avg_response_ms" 
          stackId="1"
          stroke="#8b5cf6" 
          fill="#8b5cf6" 
          fillOpacity={0.6}
          name="Avg Response (ms)"
        />
        <Area 
          type="monotone" 
          dataKey="p95_response_ms" 
          stackId="1"
          stroke="#3b82f6" 
          fill="#3b82f6" 
          fillOpacity={0.6}
          name="P95 Response (ms)"
        />
      </AreaChart>
    </ResponsiveContainer>
  );

  // Guardrail effectiveness radar chart
  const renderRadarChart = () => {
    const radarData = analytics?.guardrail_effectiveness || [];
    return (
      <ResponsiveContainer width="100%" height={300}>
        <RadarChart data={radarData}>
          <PolarGrid />
          <PolarAngleAxis dataKey="guardrail" />
          <PolarRadiusAxis angle={90} domain={[0, 100]} />
          <Radar 
            name="Effectiveness %" 
            dataKey="effectiveness" 
            stroke="#8b5cf6" 
            fill="#8b5cf6" 
            fillOpacity={0.6} 
          />
          <Radar 
            name="Block Rate %" 
            dataKey="block_rate" 
            stroke="#ef4444" 
            fill="#ef4444" 
            fillOpacity={0.6} 
          />
          <Legend />
        </RadarChart>
      </ResponsiveContainer>
    );
  };

  // Threat distribution bar chart
  const renderThreatChart = () => (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={analytics?.threat_distribution || []}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="threat_type" />
        <YAxis />
        <Tooltip />
        <Bar dataKey="count" name="Threat Count">
          {(analytics?.threat_distribution || []).map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );

  // Response time scatter plot
  const renderScatterChart = () => (
    <ResponsiveContainer width="100%" height={300}>
      <ScatterChart>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis type="number" dataKey="request_size" name="Request Size" unit="KB" />
        <YAxis type="number" dataKey="response_time" name="Response Time" unit="ms" />
        <Tooltip cursor={{ strokeDasharray: '3 3' }} />
        <Scatter 
          name="Requests" 
          data={analytics?.scatter_data || []} 
          fill="#8b5cf6"
        >
          {(analytics?.scatter_data || []).map((entry, index) => (
            <Cell 
              key={`cell-${index}`} 
              fill={entry.blocked ? '#ef4444' : '#10b981'} 
            />
          ))}
        </Scatter>
      </ScatterChart>
    </ResponsiveContainer>
  );

  const charts = {
    performance: { title: 'Performance Timeline', render: renderPerformanceChart },
    radar: { title: 'Guardrail Effectiveness', render: renderRadarChart },
    threats: { title: 'Threat Distribution', render: renderThreatChart },
    scatter: { title: 'Request Size vs Response Time', render: renderScatterChart }
  };

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex flex-wrap gap-4 items-center">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Time Range
            </label>
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            >
              <option value="1h">Last Hour</option>
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Chart Type
            </label>
            <select
              value={chartType}
              onChange={(e) => setChartType(e.target.value)}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            >
              <option value="performance">Performance Timeline</option>
              <option value="radar">Guardrail Effectiveness</option>
              <option value="threats">Threat Distribution</option>
              <option value="scatter">Request Analysis</option>
            </select>
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          {charts[chartType].title}
        </h3>
        {charts[chartType].render()}
      </div>

      {/* Key Insights */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="bg-white rounded-lg shadow p-6">
          <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wider">
            Top Threat
          </h4>
          <p className="mt-2 text-3xl font-semibold text-gray-900">
            {analytics?.top_threat || 'None'}
          </p>
          <p className="mt-1 text-sm text-gray-600">
            {analytics?.top_threat_count || 0} occurrences
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wider">
            Avg Response Time
          </h4>
          <p className="mt-2 text-3xl font-semibold text-gray-900">
            {analytics?.avg_response_time || 0}ms
          </p>
          <p className="mt-1 text-sm text-gray-600">
            P95: {analytics?.p95_response_time || 0}ms
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wider">
            False Positive Rate
          </h4>
          <p className="mt-2 text-3xl font-semibold text-gray-900">
            {analytics?.false_positive_rate || 0}%
          </p>
          <p className="mt-1 text-sm text-gray-600">
            {analytics?.false_positives || 0} false blocks
          </p>
        </div>
      </div>
    </div>
  );
}

export default AdvancedAnalytics;