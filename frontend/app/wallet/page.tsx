'use client';

import { Copy, ExternalLink } from 'lucide-react';
import { useState } from 'react';
import { toast } from 'sonner';

const transactions = [
  { date: 'Jan 10, 2026', type: 'Payment', description: 'Bay Area Foods Co', amount: '-$842.50', hash: '0xA3F8...', status: 'complete' },
  { date: 'Jan 9, 2026', type: 'Deposit', description: 'Added funds', amount: '+$2,000.00', hash: '0xB2E7...', status: 'complete' },
  { date: 'Jan 8, 2026', type: 'Payment', description: 'Fresh Farms', amount: '-$450.00', hash: '0xC1D6...', status: 'complete' },
];

export default function Wallet() {
  const [dailyLimit, setDailyLimit] = useState(5000);
  const [perTxLimit, setPerTxLimit] = useState(1000);
  const [requireApproval, setRequireApproval] = useState(true);
  const [approvalThreshold, setApprovalThreshold] = useState(500);

  const copyAddress = () => {
    navigator.clipboard.writeText('0x1234...5678');
    toast.success('Address copied to clipboard');
  };

  return (
    <div className="max-w-[1100px] mx-auto px-16 py-12">
      {/* Balance Card */}
      <div className="max-w-[500px] mx-auto mb-12">
        <div className="bg-white rounded-xl shadow-sm p-8 text-center">
          <p className="text-sm text-gray-500 mb-2">Balance</p>
          <p className="text-4xl font-bold font-mono text-gray-900 mb-1">$2,500.00</p>
          <p className="text-sm text-gray-500 mb-6">USDC</p>
          
          <div className="flex items-center justify-center gap-2 mb-6">
            <span className="font-mono text-sm text-gray-500">0x1234...5678</span>
            <button
              onClick={copyAddress}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <Copy size={16} />
            </button>
          </div>

          <button className="w-full bg-brand hover:bg-brand-dark text-white font-medium px-4 py-2.5 rounded-lg transition-colors">
            Add Funds
          </button>
        </div>
      </div>

      {/* Spending Limits */}
      <div className="max-w-[600px] mx-auto mb-12">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Spending Limits</h2>
          
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-900 mb-2">Daily Limit</label>
              <div className="flex items-center gap-2">
                <span className="text-gray-500">$</span>
                <input
                  type="number"
                  value={dailyLimit}
                  onChange={(e) => setDailyLimit(parseInt(e.target.value) || 0)}
                  className="flex-1 border border-gray-200 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-brand"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-900 mb-2">Per Transaction Limit</label>
              <div className="flex items-center gap-2">
                <span className="text-gray-500">$</span>
                <input
                  type="number"
                  value={perTxLimit}
                  onChange={(e) => setPerTxLimit(parseInt(e.target.value) || 0)}
                  className="flex-1 border border-gray-200 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-brand"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-gray-900">Require Approval Above</label>
                <input
                  type="checkbox"
                  checked={requireApproval}
                  onChange={(e) => setRequireApproval(e.target.checked)}
                  className="rounded border-gray-300 text-brand focus:ring-brand"
                />
              </div>
              {requireApproval && (
                <div className="flex items-center gap-2">
                  <span className="text-gray-500">$</span>
                  <input
                    type="number"
                    value={approvalThreshold}
                    onChange={(e) => setApprovalThreshold(parseInt(e.target.value) || 0)}
                    className="flex-1 border border-gray-200 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-brand"
                  />
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Transaction History */}
      <div className="bg-white rounded-xl shadow-sm">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Transaction History</h2>
        </div>
        <div className="divide-y divide-gray-200">
          <div className="grid grid-cols-5 gap-4 p-4 bg-gray-50 text-xs font-medium text-gray-500">
            <div>Date</div>
            <div>Type</div>
            <div>Description</div>
            <div className="text-right">Amount</div>
            <div>TX Hash</div>
          </div>
          {transactions.map((tx, idx) => (
            <div key={idx} className="grid grid-cols-5 gap-4 p-4 hover:bg-gray-50">
              <div className="text-sm text-gray-900">{tx.date}</div>
              <div>
                <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                  tx.type === 'Payment' ? 'bg-status-rose-light text-status-rose' : 'bg-brand-light text-brand'
                }`}>
                  {tx.type}
                </span>
              </div>
              <div className="text-sm text-gray-900">{tx.description}</div>
              <div className={`text-sm font-mono text-right ${tx.amount.startsWith('+') ? 'text-brand' : 'text-gray-900'}`}>
                {tx.amount}
              </div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-sm text-gray-500">{tx.hash}</span>
                <ExternalLink className="text-gray-400" size={14} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

