'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { OrderCard } from '@/components/OrderCard';
import Link from 'next/link';
import { useAgentEvents, type AgentEvent } from '@/lib/useAgentEvents';
import { Check, Loader2, RefreshCw, Wifi, WifiOff } from 'lucide-react';

const allOrders = [
  { orderId: '#ORD-001', items: 8, status: 'sourcing' as const, total: '$842.50', date: 'Jan 10, 2026', live: true },
  { orderId: '#ORD-002', items: 12, status: 'negotiating' as const, total: '$1,240.00', date: 'Jan 9, 2026', live: true },
  { orderId: '#ORD-003', items: 5, status: 'awaiting-approval' as const, total: '$450.00', date: 'Jan 8, 2026' },
  { orderId: '#ORD-004', items: 15, status: 'paying' as const, total: '$1,850.00', date: 'Jan 7, 2026' },
  { orderId: '#ORD-005', items: 6, status: 'complete' as const, total: '$320.00', date: 'Jan 6, 2026' },
  { orderId: '#ORD-006', items: 10, status: 'complete' as const, total: '$680.00', date: 'Jan 5, 2026' },
  { orderId: '#ORD-007', items: 4, status: 'complete' as const, total: '$240.00', date: 'Jan 4, 2026' },
];

function formatTime(timestamp: string) {
  return new Date(timestamp).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

function LiveActivityPanel({ events, connected, onRefresh }: {
  events: AgentEvent[];
  connected: boolean;
  onRefresh: () => void;
}) {
  return (
    <div className="bg-white rounded-xl shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <h2 className="text-lg font-semibold text-gray-900">Live Activity</h2>
          <div className={`flex items-center gap-1.5 ${connected ? 'text-brand' : 'text-gray-400'}`}>
            {connected ? (
              <>
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-brand"></span>
                </span>
                <span className="text-xs font-medium">Live</span>
              </>
            ) : (
              <>
                <WifiOff size={12} />
                <span className="text-xs font-medium">Disconnected</span>
              </>
            )}
          </div>
        </div>
        <button
          onClick={onRefresh}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          title="Refresh"
        >
          <RefreshCw size={16} className="text-gray-500" />
        </button>
      </div>
      
      {/* Activity Feed */}
      <div className="max-h-80 overflow-y-auto divide-y divide-gray-100">
        {events.length === 0 ? (
          <div className="p-8 text-center text-gray-500 text-sm">
            <p>Waiting for activity...</p>
            <p className="text-xs mt-1">Send a message to start</p>
          </div>
        ) : (
          events.slice(0, 15).map((event, i) => (
            <div key={`${event.timestamp}-${i}`} className="px-6 py-3 hover:bg-gray-50 transition-colors">
              <div className="flex items-start gap-3">
                <div className={`w-2 h-2 rounded-full mt-2 ${
                  event.stage === 'sourcing' ? 'bg-status-blue' :
                  event.stage === 'calling' || event.stage === 'negotiating' ? 'bg-status-orange' :
                  event.stage === 'evaluating' ? 'bg-status-blue' :
                  event.stage === 'approval_pending' ? 'bg-status-yellow' :
                  event.stage === 'approved' || event.stage === 'completed' ? 'bg-brand' :
                  event.stage === 'failed' ? 'bg-status-rose' :
                  'bg-gray-400'
                }`} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-900 leading-relaxed">{event.message}</p>
                  <p className="text-xs text-gray-400 mt-1 font-mono">{formatTime(event.timestamp)}</p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

function PendingApprovalsPanel({ approvals, onApprove }: {
  approvals: { order_id: string; vendor_name: string; price: number; product: string; quantity: number; unit: string }[];
  onApprove: (orderId: string) => Promise<boolean>;
}) {
  const [approvingId, setApprovingId] = useState<string | null>(null);

  const handleApprove = async (orderId: string) => {
    setApprovingId(orderId);
    await onApprove(orderId);
    setApprovingId(null);
  };

  if (approvals.length === 0) return null;

  return (
    <div className="bg-status-yellow-light border border-status-yellow rounded-xl p-6 mb-8">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
        <span className="w-2 h-2 bg-status-yellow rounded-full animate-pulse" />
        Pending Approvals ({approvals.length})
      </h3>
      <div className="space-y-4">
        {approvals.map((approval) => (
          <div key={approval.order_id} className="bg-white rounded-lg p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-900">{approval.vendor_name}</p>
                <p className="text-sm text-gray-500">
                  {approval.quantity} {approval.unit} of {approval.product} @ ${approval.price.toFixed(2)}/{approval.unit}
                </p>
                <p className="text-xs text-gray-400 font-mono mt-1">{approval.order_id}</p>
              </div>
              <button
                onClick={() => handleApprove(approval.order_id)}
                disabled={approvingId === approval.order_id}
                className="bg-brand hover:bg-brand-dark text-white font-medium px-4 py-2 rounded-lg transition-colors disabled:opacity-50 flex items-center gap-2"
              >
                {approvingId === approval.order_id ? (
                  <>
                    <Loader2 size={16} className="animate-spin" />
                    Approving...
                  </>
                ) : (
                  <>
                    <Check size={16} />
                    Approve
                  </>
                )}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function Orders() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const { events, connected, pendingApprovals, approveOrder, refresh } = useAgentEvents();

  // Check if onboarding is complete
  useEffect(() => {
    const onboardingComplete = localStorage.getItem('onboarding_complete');
    if (!onboardingComplete) {
      router.push('/onboarding');
    }
  }, [router]);

  // Separate active and completed orders
  const activeOrders = allOrders.filter(order => 
    order.status !== 'complete' && 
    (order.orderId.toLowerCase().includes(searchQuery.toLowerCase()) || 
     order.total.includes(searchQuery))
  );

  const pastOrders = allOrders.filter(order => 
    order.status === 'complete' && 
    (order.orderId.toLowerCase().includes(searchQuery.toLowerCase()) || 
     order.total.includes(searchQuery))
  );

  return (
    <div className="max-w-[1100px] mx-auto px-16 py-12">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Orders</h1>
        <Link
          href="/new-order"
          className="bg-brand hover:bg-brand-dark text-white font-medium px-4 py-2.5 rounded-lg transition-colors"
        >
          New Order
        </Link>
      </div>

      {/* Pending Approvals Banner */}
      <PendingApprovalsPanel approvals={pendingApprovals} onApprove={approveOrder} />

      {/* Live Activity Panel */}
      <div className="mb-8">
        <LiveActivityPanel events={events} connected={connected} onRefresh={refresh} />
      </div>

      {/* Search */}
      <div className="mb-8">
        <input
          type="text"
          placeholder="Search orders..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full max-w-md border border-gray-200 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand"
        />
      </div>

      {/* Active Orders Section */}
      {activeOrders.length > 0 && (
        <div className="mb-12">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Active Orders</h2>
            <span className="text-sm text-gray-500">{activeOrders.length} in progress</span>
          </div>
          <div className="bg-white rounded-xl shadow-sm">
            <div className="divide-y divide-gray-200">
              {activeOrders.map((order) => (
                <OrderCard key={order.orderId} {...order} live={order.live} />
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Past Orders Section */}
      <div>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">Past Orders</h2>
          <span className="text-sm text-gray-500">{pastOrders.length} completed</span>
        </div>
        {pastOrders.length > 0 ? (
          <div className="bg-white rounded-xl shadow-sm">
            <div className="divide-y divide-gray-200">
              {pastOrders.map((order) => (
                <OrderCard key={order.orderId} {...order} live={order.live} />
              ))}
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-sm p-12 text-center">
            <p className="text-gray-500">No past orders yet</p>
          </div>
        )}
      </div>

      {/* Show empty state if no orders at all */}
      {activeOrders.length === 0 && pastOrders.length === 0 && (
        <div className="bg-white rounded-xl shadow-sm p-12 text-center">
          <p className="text-gray-500 mb-4">No orders found</p>
          <Link
            href="/new-order"
            className="inline-block bg-brand hover:bg-brand-dark text-white font-medium px-6 py-2.5 rounded-lg transition-colors"
          >
            Create your first order
          </Link>
        </div>
      )}
    </div>
  );
}

