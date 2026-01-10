'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { OrderCard } from '@/components/OrderCard';
import Link from 'next/link';

const allOrders = [
  { orderId: '#ORD-001', items: 8, status: 'sourcing' as const, total: '$842.50', date: 'Jan 10, 2026', live: true },
  { orderId: '#ORD-002', items: 12, status: 'negotiating' as const, total: '$1,240.00', date: 'Jan 9, 2026', live: true },
  { orderId: '#ORD-003', items: 5, status: 'awaiting-approval' as const, total: '$450.00', date: 'Jan 8, 2026' },
  { orderId: '#ORD-004', items: 15, status: 'paying' as const, total: '$1,850.00', date: 'Jan 7, 2026' },
  { orderId: '#ORD-005', items: 6, status: 'complete' as const, total: '$320.00', date: 'Jan 6, 2026' },
  { orderId: '#ORD-006', items: 10, status: 'complete' as const, total: '$680.00', date: 'Jan 5, 2026' },
  { orderId: '#ORD-007', items: 4, status: 'complete' as const, total: '$240.00', date: 'Jan 4, 2026' },
];

export default function Orders() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');

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

