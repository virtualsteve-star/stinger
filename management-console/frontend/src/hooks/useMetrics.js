import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';

// Hook to collect historical metrics
export function useMetricsHistory(interval = 5000) {
  const [history, setHistory] = useState([]);
  
  const { data: stats } = useQuery({
    queryKey: ['systemStats'],
    queryFn: async () => {
      const response = await fetch('/api/stats/overview');
      if (!response.ok) throw new Error('Failed to fetch stats');
      return response.json();
    },
    refetchInterval: interval,
  });

  useEffect(() => {
    if (stats?.total_requests !== undefined) {
      setHistory(prev => {
        const now = new Date();
        const newPoint = {
          time: now.toLocaleTimeString(),
          timestamp: now.getTime(),
          total: stats.total_requests,
          blocked: stats.blocked_requests,
          block_rate: stats.block_rate
        };
        
        // Keep last 60 data points (5 minutes at 5s intervals)
        const updated = [...prev, newPoint].slice(-60);
        return updated;
      });
    }
  }, [stats]);

  return { currentStats: stats, history };
}

// Hook to get guardrail-specific metrics
export function useGuardrailMetrics() {
  return useQuery({
    queryKey: ['guardrailMetrics'],
    queryFn: async () => {
      const response = await fetch('/api/guardrails/metrics');
      if (!response.ok) throw new Error('Failed to fetch metrics');
      return response.json();
    },
    refetchInterval: 10000,
  });
}