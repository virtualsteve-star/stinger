import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { formatDistanceToNow } from 'date-fns';

function ConversationMonitor() {
  const { data: conversations, isLoading } = useQuery({
    queryKey: ['conversations'],
    queryFn: async () => {
      const response = await fetch('/api/conversations');
      if (!response.ok) throw new Error('Failed to fetch conversations');
      return response.json();
    },
    refetchInterval: 10000, // Poll every 10 seconds
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="spinner mr-2" />
        <span className="text-gray-500">Loading conversations...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Active Conversations</h3>
        </div>
        <div className="divide-y divide-gray-200">
          {conversations?.map((conv) => (
            <div key={conv.conversation_id} className="px-6 py-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {conv.conversation_id}
                  </p>
                  <p className="text-sm text-gray-500">
                    User: {conv.user_id} • {conv.turn_count} turns
                  </p>
                </div>
                <div className="text-right">
                  <span className={`status-badge ${conv.status === 'active' ? 'healthy' : 'bg-gray-100 text-gray-800'}`}>
                    {conv.status}
                  </span>
                  <p className="text-xs text-gray-500 mt-1">
                    Last activity: {formatDistanceToNow(new Date(conv.last_activity))} ago
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default ConversationMonitor;