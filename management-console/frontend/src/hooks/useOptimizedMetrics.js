import { useState, useEffect, useMemo, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';

// Optimized hook with memoization and data reduction
export function useOptimizedMetricsHistory(interval = 5000) {
  const [history, setHistory] = useState([]);
  const [isPaused, setIsPaused] = useState(false);
  
  // Check if tab is visible
  useEffect(() => {
    const handleVisibilityChange = () => {
      setIsPaused(document.hidden);
    };
    
    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, []);
  
  const { data: stats } = useQuery({
    queryKey: ['systemStats'],
    queryFn: async () => {
      const response = await fetch('/api/stats/overview');
      if (!response.ok) throw new Error('Failed to fetch stats');
      return response.json();
    },
    refetchInterval: isPaused ? false : interval,
    staleTime: interval / 2, // Cache for half the interval
  });

  // Optimize history updates with data reduction
  useEffect(() => {
    if (stats?.total_requests !== undefined && !isPaused) {
      setHistory(prev => {
        const now = Date.now();
        const newPoint = {
          time: new Date(now).toLocaleTimeString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit' 
          }),
          timestamp: now,
          total: stats.total_requests,
          blocked: stats.blocked_requests,
          block_rate: stats.block_rate
        };
        
        // Data reduction strategy
        let updated = [...prev];
        
        // Add new point
        updated.push(newPoint);
        
        // Keep last 5 minutes of detailed data
        const fiveMinutesAgo = now - 5 * 60 * 1000;
        updated = updated.filter(point => point.timestamp > fiveMinutesAgo);
        
        // Downsample older data (keep every 5th point)
        if (updated.length > 60) {
          const recent = updated.slice(-60);
          const older = updated.slice(0, -60);
          const downsampled = older.filter((_, index) => index % 5 === 0);
          updated = [...downsampled, ...recent];
        }
        
        return updated;
      });
    }
  }, [stats, isPaused]);

  // Memoize computed values
  const computedMetrics = useMemo(() => {
    if (!history.length) return null;
    
    const recent = history.slice(-12); // Last minute
    const avgBlockRate = recent.reduce((sum, p) => sum + p.block_rate, 0) / recent.length;
    const trend = history.length > 1 
      ? history[history.length - 1].total - history[0].total 
      : 0;
    
    return {
      avgBlockRate: avgBlockRate.toFixed(2),
      requestTrend: trend,
      dataPoints: history.length
    };
  }, [history]);

  // Callbacks for manual control
  const clearHistory = useCallback(() => setHistory([]), []);
  const pauseUpdates = useCallback(() => setIsPaused(true), []);
  const resumeUpdates = useCallback(() => setIsPaused(false), []);

  return { 
    currentStats: stats, 
    history, 
    computedMetrics,
    isPaused,
    clearHistory,
    pauseUpdates,
    resumeUpdates
  };
}

// Debounced search hook
export function useDebouncedSearch(searchFn, delay = 300) {
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedTerm, setDebouncedTerm] = useState('');
  
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedTerm(searchTerm);
    }, delay);
    
    return () => clearTimeout(handler);
  }, [searchTerm, delay]);
  
  const results = useQuery({
    queryKey: ['search', debouncedTerm],
    queryFn: () => searchFn(debouncedTerm),
    enabled: debouncedTerm.length > 0,
  });
  
  return {
    searchTerm,
    setSearchTerm,
    results,
    isSearching: searchTerm !== debouncedTerm
  };
}

// Batch operations hook
export function useBatchOperations() {
  const [queue, setQueue] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  
  const addToQueue = useCallback((operation) => {
    setQueue(prev => [...prev, operation]);
  }, []);
  
  const processBatch = useCallback(async () => {
    if (queue.length === 0 || isProcessing) return;
    
    setIsProcessing(true);
    
    try {
      const batch = queue.slice(0, 10); // Process 10 at a time
      const results = await Promise.all(
        batch.map(op => op().catch(err => ({ error: err })))
      );
      
      setQueue(prev => prev.slice(10));
      return results;
    } finally {
      setIsProcessing(false);
    }
  }, [queue, isProcessing]);
  
  // Auto-process queue
  useEffect(() => {
    if (queue.length > 0 && !isProcessing) {
      const timer = setTimeout(processBatch, 100);
      return () => clearTimeout(timer);
    }
  }, [queue.length, isProcessing, processBatch]);
  
  return {
    addToQueue,
    queueSize: queue.length,
    isProcessing
  };
}