import React, { useState, lazy, Suspense } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import './App.css';

// Lazy load components for better performance
const Dashboard = lazy(() => import('./components/Dashboard'));
const GuardrailMetrics = lazy(() => import('./components/GuardrailMetrics'));
const ConversationMonitor = lazy(() => import('./components/ConversationMonitor'));
const LogExplorer = lazy(() => import('./components/LogExplorer'));
const VirtualLogExplorer = lazy(() => import('./components/VirtualLogExplorer'));
const SystemHealth = lazy(() => import('./components/SystemHealth'));
const AdvancedAnalytics = lazy(() => import('./components/AdvancedAnalytics'));
const DataRetention = lazy(() => import('./components/DataRetention'));

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const tabs = [
    { id: 'dashboard', label: '📊 Dashboard', component: Dashboard },
    { id: 'guardrails', label: '🎯 Guardrails', component: GuardrailMetrics },
    { id: 'conversations', label: '💬 Conversations', component: ConversationMonitor },
    { id: 'logs', label: '📝 Logs', component: VirtualLogExplorer },
    { id: 'analytics', label: '📈 Analytics', component: AdvancedAnalytics },
    { id: 'health', label: '❤️ Health', component: SystemHealth },
    { id: 'settings', label: '⚙️ Settings', component: DataRetention },
  ];

  const ActiveComponent = tabs.find(t => t.id === activeTab)?.component || Dashboard;

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <h1 className="text-xl font-semibold text-gray-900">
                🛡️ Stinger Management Console
              </h1>
              <button 
                onClick={() => queryClient.invalidateQueries()}
                className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
              >
                ↻ Refresh All
              </button>
            </div>
          </div>
        </header>

        {/* Navigation */}
        <nav className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex space-x-8">
              {tabs.map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Suspense fallback={
            <div className="flex items-center justify-center h-64">
              <div className="spinner mr-2" />
              <span className="text-gray-500">Loading...</span>
            </div>
          }>
            <ActiveComponent />
          </Suspense>
        </main>
      </div>
    </QueryClientProvider>
  );
}

export default App;