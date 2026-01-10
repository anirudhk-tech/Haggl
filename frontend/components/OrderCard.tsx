import Link from 'next/link';
import { StatusBadge } from './StatusBadge';
import type { Status } from './StatusBadge';

interface OrderCardProps {
  orderId: string;
  items: number;
  status: Status;
  total: string;
  date: string;
  live?: boolean;
}

export function OrderCard({ orderId, items, status, total, date, live }: OrderCardProps) {
  const href = live && status !== 'complete' ? `/orders/${orderId}/live` : `/orders/${orderId}`;
  
  return (
    <Link href={href}>
      <div className="border-b border-gray-200 py-4 hover:bg-gray-50 transition-colors cursor-pointer">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-6">
            <span className="font-mono text-sm text-gray-900">{orderId}</span>
            <span className="text-sm text-gray-900">{items} items</span>
            <StatusBadge status={status} />
            {live && status !== 'complete' && (
              <span className="text-xs bg-status-orange-light text-status-orange px-2 py-0.5 rounded-full">
                Live
              </span>
            )}
          </div>
          <div className="flex items-center gap-6">
            <span className="font-mono text-sm text-gray-900">{total}</span>
            <span className="text-sm text-gray-500">{date}</span>
          </div>
        </div>
      </div>
    </Link>
  );
}

