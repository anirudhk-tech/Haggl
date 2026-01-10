'use client';

import { useState } from 'react';
import { StatusBadge } from '@/components/StatusBadge';
import { ProgressPhase } from '@/components/ProgressPhase';
import { Check, Loader2, ExternalLink } from 'lucide-react';

export default function OrderDetail({ params }: { params: { id: string } }) {
  const [expandedPhase, setExpandedPhase] = useState<string | null>('negotiation');

  return (
    <div className="max-w-[1100px] mx-auto px-16 py-12">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-4">
          <span className="font-mono text-xl font-bold text-gray-900">{params.id}</span>
          <StatusBadge status="negotiating" />
        </div>
        <span className="text-sm text-gray-500">Created Jan 10, 2026</span>
      </div>

      {/* Budget Row */}
      <div className="flex items-center gap-6 mb-12 text-sm text-gray-500">
        <span>Budget: $1,000</span>
        <span className="text-brand">Current: $842</span>
        <span>Savings: $158 (14%)</span>
      </div>

      {/* Progress Phases */}
      <div className="space-y-6">
        {/* Phase 1: Sourcing */}
        <ProgressPhase
          title="Sourcing"
          status="complete"
          color="status-blue"
          summary="Found 12 suppliers"
          isCollapsed={expandedPhase !== 'sourcing'}
          onToggle={() => setExpandedPhase(expandedPhase === 'sourcing' ? null : 'sourcing')}
        >
          {expandedPhase === 'sourcing' && (
            <div className="font-mono text-sm space-y-1">
              <div className="text-brand">✓ Searching for flour suppliers...</div>
              <div className="text-brand">✓ Found: Bay Area Foods Co</div>
              <div className="text-brand">✓ Found: Golden Gate Grains</div>
              <div className="text-gray-900">→ Searching for butter suppliers...</div>
            </div>
          )}
        </ProgressPhase>

        {/* Phase 2: Negotiation */}
        <ProgressPhase
          title="Negotiation"
          status="active"
          color="status-orange"
        >
          <div className="bg-status-orange-light rounded-lg p-4 mb-6">
            <div className="flex items-center gap-2 mb-2">
              <span className="w-2 h-2 bg-status-orange rounded-full animate-pulse" />
              <span className="font-semibold text-status-orange">Live: Calling 2 vendors</span>
            </div>
            <div className="flex gap-4 text-sm">
              <span className="text-status-orange">[Bay Area Foods 1:23]</span>
              <span className="text-status-orange">[Fresh Farms 0:45]</span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            {[
              { name: 'Bay Area Foods', ingredient: 'Flour', status: 'calling', time: '1:23', discount: '15%' },
              { name: 'Fresh Farms', ingredient: 'Butter', status: 'calling', time: '0:45', discount: null },
            ].map((vendor) => (
              <div key={vendor.name} className="bg-gray-50 rounded-lg p-4">
                <h4 className="font-semibold text-gray-900 mb-1">{vendor.name}</h4>
                <p className="text-sm text-gray-500 mb-3">{vendor.ingredient}</p>
                {vendor.status === 'calling' ? (
                  <div className="flex items-center gap-2 text-status-orange">
                    <Loader2 className="animate-spin" size={16} />
                    <span className="text-sm">📞 Calling... {vendor.time}</span>
                  </div>
                ) : vendor.discount ? (
                  <div className="text-sm">
                    <span className="text-brand">✓ {vendor.discount} discount</span>
                    <button className="ml-2 text-brand hover:text-brand-dark text-xs">
                      View transcript
                    </button>
                  </div>
                ) : (
                  <span className="text-sm text-gray-500">Queued</span>
                )}
              </div>
            ))}
          </div>
        </ProgressPhase>

        {/* Phase 3: Evaluation */}
        <ProgressPhase
          title="Evaluation"
          status="pending"
          color="status-blue"
          summary="Optimal vendors selected"
          isCollapsed={expandedPhase !== 'evaluation'}
          onToggle={() => setExpandedPhase(expandedPhase === 'evaluation' ? null : 'evaluation')}
        />

        {/* Phase 4: Approval */}
        <ProgressPhase
          title="Approval"
          status="pending"
          color="status-yellow"
        >
          <div className="bg-gray-50 rounded-lg p-6 mb-6">
            <h4 className="text-xl font-semibold text-gray-900 mb-2">Bay Area Foods</h4>
            <p className="text-3xl font-bold text-brand mb-2">$842.50</p>
            <p className="text-sm text-gray-500 mb-4">3 items · Delivery · Arrives Jan 12</p>
            <span className="inline-block bg-brand-light text-brand px-3 py-1 rounded-full text-xs font-medium">
              Saved $138 (14%)
            </span>
          </div>
          <div className="flex gap-4">
            <button className="flex-1 bg-brand hover:bg-brand-dark text-white font-medium px-6 py-3 rounded-lg transition-colors">
              Approve & Pay
            </button>
            <button className="flex-1 bg-white hover:bg-status-rose-light text-status-rose border border-status-rose font-medium px-6 py-3 rounded-lg transition-colors">
              Reject
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-4 text-center">Or reply YES to SMS</p>
        </ProgressPhase>

        {/* Phase 5: Payment */}
        <ProgressPhase
          title="Payment"
          status="pending"
          color="status-purple"
          summary="Payment Complete"
          isCollapsed={expandedPhase !== 'payment'}
          onToggle={() => setExpandedPhase(expandedPhase === 'payment' ? null : 'payment')}
        >
          {expandedPhase === 'payment' && (
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm">
                <Check className="text-brand" size={16} />
                <span className="text-gray-900">Payment Complete</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <span className="font-mono text-gray-500">x402 Auth: 0xA3F8...</span>
                <ExternalLink className="text-gray-400" size={14} />
              </div>
            </div>
          )}
        </ProgressPhase>
      </div>
    </div>
  );
}

