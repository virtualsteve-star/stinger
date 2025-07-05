import React, { useState, useEffect } from 'react';
import './PerformancePanel.css';

interface PerformanceMetrics {
  total_requests: number;
  blocked_requests: number;
  avg_response_time_ms: number;
  peak_response_time_ms: number;
  last_request_time: number | null;
  block_rate: number;
}

interface PerformancePanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export const PerformancePanel: React.FC<PerformancePanelProps> = ({ isOpen, onClose }) => {
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const loadMetrics = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch('/api/performance');
      if (response.ok) {
        const data = await response.json();
        setMetrics(data.metrics);
      } else {
        // Don't show error for initial load, let the empty state handle it
        if (metrics !== null) {
          setError('Failed to refresh performance metrics');
        }
      }
    } catch (err) {
      // Don't show error for initial load, let the empty state handle it
      if (metrics !== null) {
        setError('Error connecting to server');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadMetrics();
      
      // Set up auto-refresh if enabled
      if (autoRefresh) {
        const interval = setInterval(loadMetrics, 2000); // Refresh every 2 seconds
        return () => clearInterval(interval);
      }
    }
  }, [isOpen, autoRefresh]);

  const formatTime = (ms: number) => {
    if (ms < 1000) {
      return `${ms.toFixed(0)}ms`;
    }
    return `${(ms / 1000).toFixed(2)}s`;
  };

  const formatTimestamp = (timestamp: number | null) => {
    if (!timestamp) return 'Never';
    const date = new Date(timestamp * 1000);
    return date.toLocaleTimeString();
  };

  return (
    <>
      {/* Backdrop */}
      {isOpen && <div className="panel-backdrop" onClick={onClose} />}
      
      {/* Panel */}
      <div className={`slide-panel performance-panel ${isOpen ? 'open' : ''}`}>
        <div className="panel-header">
          <h2>📊 Performance Monitoring</h2>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>
        
        <div className="panel-content">
        <div className="performance-controls">
          <label className="auto-refresh-toggle">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Auto-refresh
          </label>
          <button onClick={loadMetrics} disabled={loading || autoRefresh}>
            {loading ? 'Loading...' : 'Refresh'}
          </button>
        </div>

        {error && (
          <div className="performance-error">
            ⚠️ {error}
          </div>
        )}

        {metrics && (
          <div className="performance-metrics">
            <div className="metric-card">
              <h3>Request Volume</h3>
              <div className="metric-value">{metrics.total_requests}</div>
              <div className="metric-label">Total Requests</div>
            </div>

            <div className="metric-card">
              <h3>Security</h3>
              <div className="metric-value">{metrics.blocked_requests}</div>
              <div className="metric-label">Blocked Requests</div>
              <div className="metric-secondary">{metrics.block_rate.toFixed(1)}% block rate</div>
            </div>

            <div className="metric-card">
              <h3>Response Times</h3>
              <div className="metric-value">{formatTime(metrics.avg_response_time_ms)}</div>
              <div className="metric-label">Average Response</div>
              <div className="metric-secondary">Peak: {formatTime(metrics.peak_response_time_ms)}</div>
            </div>

            <div className="metric-card full-width">
              <h3>Last Activity</h3>
              <div className="metric-value">{formatTimestamp(metrics.last_request_time)}</div>
            </div>

            {metrics.total_requests > 0 && (
              <div className="performance-chart">
                <h3>Block Rate Visualization</h3>
                <div className="block-rate-bar">
                  <div 
                    className="block-rate-fill"
                    style={{ width: `${metrics.block_rate}%` }}
                  >
                    {metrics.block_rate > 5 && `${metrics.block_rate.toFixed(1)}%`}
                  </div>
                </div>
                <div className="block-rate-labels">
                  <span>0%</span>
                  <span>50%</span>
                  <span>100%</span>
                </div>
              </div>
            )}
          </div>
        )}

        {metrics && metrics.total_requests === 0 && (
          <div className="performance-empty">
            <p>No requests recorded yet. Start using the chat to see performance metrics.</p>
          </div>
        )}

        {!loading && !metrics && !error && (
          <div className="performance-empty">
            <h3>📊 Getting Started</h3>
            <p>Performance metrics will appear here once you start chatting.</p>
            <p>Try sending a message to see:</p>
            <ul style={{ textAlign: 'left', margin: '16px auto', maxWidth: '300px' }}>
              <li>Request processing times</li>
              <li>Security block rates</li>
              <li>Real-time performance data</li>
            </ul>
            <p style={{ marginTop: '20px', fontSize: '14px', color: '#666' }}>
              Auto-refresh is enabled and will update metrics every 2 seconds.
            </p>
          </div>
        )}

        {loading && !metrics && (
          <div className="performance-empty">
            <p>Loading performance metrics...</p>
          </div>
        )}
        </div>
      </div>
    </>
  );
};