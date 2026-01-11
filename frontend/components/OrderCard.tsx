'use client';

import Link from 'next/link';
import { StatusBadge } from './StatusBadge';
import type { Status } from './StatusBadge';
import { FileText } from 'lucide-react';

interface OrderCardProps {
  orderId: string;
  items: number;
  status: Status;
  total: string;
  date: string;
  live?: boolean;
  invoiceUrl?: string;
  onPayInvoice?: (orderId: string, invoiceUrl: string) => void;
}

export function OrderCard({ orderId, items, status, total, date, live, invoiceUrl, onPayInvoice }: OrderCardProps) {
  const href = live && status !== 'complete' ? `/orders/${orderId.replace('#', '')}/live` : `/orders/${orderId.replace('#', '')}`;
  
  const handleInvoiceClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (invoiceUrl && onPayInvoice) {
      onPayInvoice(orderId, invoiceUrl);
    }
  };

  return (
    <div className="border-b border-gray-200 py-4 hover:bg-gray-50 transition-colors">
      <div className="flex items-center justify-between">
        <Link href={href} className="flex items-center gap-6 flex-1">
          <span className="font-mono text-sm text-gray-900">{orderId}</span>
          <span className="text-sm text-gray-900">{items} items</span>
          <StatusBadge status={status} />
          {live && status !== 'complete' && (
            <span className="text-xs bg-status-orange-light text-status-orange px-2 py-0.5 rounded-full">
              Live
            </span>
          )}
        </Link>
        <div className="flex items-center gap-4">
          {invoiceUrl && status === 'paying' && (
            <button
              onClick={handleInvoiceClick}
              className="flex items-center gap-2 bg-brand hover:bg-brand-dark text-white text-sm font-medium px-3 py-1.5 rounded-lg transition-colors"
            >
              <FileText size={16} />
              Pay Invoice
            </button>
          )}
          <span className="font-mono text-sm text-gray-900">{total}</span>
          <span className="text-sm text-gray-500">{date}</span>
        </div>
      </div>
    </div>
  );
}
