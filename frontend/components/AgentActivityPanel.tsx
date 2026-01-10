'use client';

type AgentStatus = 'idle' | 'active' | 'complete';

interface Agent {
  name: string;
  icon: string;
  status: AgentStatus;
  message: string;
  isNegotiating?: boolean;
}

const statusStyles: Record<AgentStatus, string> = {
  idle: 'text-gray-500',
  active: 'text-status-blue',
  complete: 'text-brand',
};

const borderStyles: Record<AgentStatus, string> = {
  idle: 'border-l-4 border-transparent',
  active: 'border-l-4 border-status-blue',
  complete: 'border-l-4 border-brand',
};

interface AgentActivityPanelProps {
  agents: Agent[];
}

export function AgentActivityPanel({ agents }: AgentActivityPanelProps) {
  const isAnyActive = agents.some(a => a.status === 'active');
  
  return (
    <div className="bg-white rounded-xl shadow-sm p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Agent Activity</h2>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${isAnyActive ? 'bg-brand animate-pulse' : 'bg-gray-400'}`} />
          <span className="text-sm text-gray-500">{isAnyActive ? 'Active' : 'Idle'}</span>
        </div>
      </div>
      
      {/* Agent Rows */}
      <div className="flex flex-col gap-4">
        {agents.map((agent) => {
          const isNegotiating = agent.isNegotiating && agent.status === 'active';
          const borderColor = isNegotiating ? 'border-status-orange' : borderStyles[agent.status];
          const textColor = isNegotiating ? 'text-status-orange' : statusStyles[agent.status];
          
          return (
            <div
              key={agent.name}
              className={`bg-gray-50 rounded-lg p-4 flex items-center justify-between ${borderColor}`}
            >
              <div className="flex items-center gap-3">
                <span className="text-xl">{agent.icon}</span>
                <span className="font-medium text-gray-900">{agent.name}</span>
              </div>
              <span className={`text-sm ${textColor} ${isNegotiating ? 'flex items-center gap-2' : ''}`}>
                {isNegotiating && <span className="w-2 h-2 bg-status-orange rounded-full animate-pulse" />}
                {agent.message}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

