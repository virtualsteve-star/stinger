import React, { useState, useEffect } from 'react';
import './StatusBar.css';

interface HealthStatus {
  backend: 'healthy' | 'error' | 'unknown';
  guardrails: 'active' | 'inactive' | 'unknown';
  auditTrail: 'enabled' | 'disabled' | 'unknown';
  totalGuardrails?: number;
  enabledGuardrails?: number;
}

export const StatusBar: React.FC = () => {
  const [health, setHealth] = useState<HealthStatus>({
    backend: 'unknown',
    guardrails: 'unknown',
    auditTrail: 'unknown'
  });

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch('/api/health');
        if (response.ok) {
          const data = await response.json();
          setHealth({
            backend: 'healthy',
            guardrails: data.pipeline_loaded ? 'active' : 'inactive',
            auditTrail: data.audit_enabled ? 'enabled' : 'disabled',
            totalGuardrails: data.total_guardrails,
            enabledGuardrails: data.enabled_guardrails
          });
        } else {
          setHealth(prev => ({ ...prev, backend: 'error' }));
        }
      } catch (error) {
        setHealth(prev => ({ ...prev, backend: 'error' }));
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="status-bar">
      <div className="status-indicator">
        <span className={`status-dot ${health.backend}`} />
        <span>Backend</span>
      </div>
      <div className="status-indicator">
        <span className={`status-dot ${health.guardrails}`} />
        <span>Guardrails</span>
      </div>
      <div className="status-indicator">
        <span className={`status-dot ${health.auditTrail}`} />
        <span>Audit Trail</span>
      </div>
    </div>
  );
};