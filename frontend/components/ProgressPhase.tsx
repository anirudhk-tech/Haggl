'use client';

import { useState } from 'react';
import { Check, Loader2 } from 'lucide-react';

type PhaseStatus = 'pending' | 'active' | 'complete';

interface ProgressPhaseProps {
  title: string;
  status: PhaseStatus;
  color: string;
  children?: React.ReactNode;
  summary?: string;
  isCollapsed?: boolean;
  onToggle?: () => void;
}

export function ProgressPhase({ 
  title, 
  status, 
  color, 
  children, 
  summary,
  isCollapsed = false,
  onToggle 
}: ProgressPhaseProps) {
  const isActive = status === 'active';
  const isComplete = status === 'complete';
  
  // Map color prop to actual Tailwind classes
  const borderColorClass = isActive 
    ? color === 'status-blue' ? 'border-status-blue' 
      : color === 'status-orange' ? 'border-status-orange'
      : color === 'status-yellow' ? 'border-status-yellow'
      : color === 'status-purple' ? 'border-status-purple'
      : 'border-transparent'
    : 'border-transparent';
  
  const textColorClass = isActive
    ? color === 'status-blue' ? 'text-status-blue'
      : color === 'status-orange' ? 'text-status-orange'
      : color === 'status-yellow' ? 'text-status-yellow'
      : color === 'status-purple' ? 'text-status-purple'
      : 'text-gray-500'
    : 'text-gray-500';

  if (isComplete && isCollapsed) {
    return (
      <div 
        onClick={onToggle}
        className="bg-white rounded-xl shadow-sm p-4 flex items-center justify-between cursor-pointer hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <Check className="text-brand" size={20} />
          <span className="font-medium text-gray-900">{title}</span>
        </div>
        {summary && <span className="text-sm text-gray-500">{summary}</span>}
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-xl shadow-sm p-6 border-l-4 ${borderColorClass}`}>
      <div className="flex items-center gap-3 mb-4">
        {isActive && <Loader2 className={`${textColorClass} animate-spin`} size={20} />}
        {isComplete && <Check className="text-brand" size={20} />}
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
      </div>
      {children}
    </div>
  );
}

