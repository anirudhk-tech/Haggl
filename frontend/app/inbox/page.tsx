'use client';

import { useState } from 'react';
import { Phone, Mail, FileText, Play, Pause } from 'lucide-react';

type Tab = 'all' | 'calls' | 'emails' | 'invoices';

const items = [
  { id: 1, type: 'call' as const, vendor: 'Bay Area Foods', preview: 'Negotiated 15% discount on flour order...', time: '2:34', date: 'Jan 10, 2026', unread: true },
  { id: 2, type: 'email' as const, vendor: 'Fresh Farms', preview: 'Invoice #INV-1234 ready for review...', time: '10:15 AM', date: 'Jan 9, 2026', unread: true },
  { id: 3, type: 'invoice' as const, vendor: 'Golden Gate Grains', preview: 'Invoice for $450.00 - 3 items...', time: '3:22 PM', date: 'Jan 8, 2026', unread: false },
  { id: 4, type: 'call' as const, vendor: 'Pacific Produce', preview: 'Follow-up call scheduled...', time: '1:45', date: 'Jan 7, 2026', unread: false },
];

export default function Inbox() {
  const [activeTab, setActiveTab] = useState<Tab>('all');
  const [selectedItem, setSelectedItem] = useState(items[0]);
  const [isPlaying, setIsPlaying] = useState(false);

  const filteredItems = activeTab === 'all' 
    ? items 
    : items.filter(item => item.type === activeTab.slice(0, -1));

  const getIcon = (type: string) => {
    switch (type) {
      case 'call': return <Phone size={18} className="text-status-orange" />;
      case 'email': return <Mail size={18} className="text-status-blue" />;
      case 'invoice': return <FileText size={18} className="text-status-purple" />;
      default: return null;
    }
  };

  return (
    <div className="flex h-[calc(100vh-64px)]">
      {/* List Panel */}
      <div className="w-[35%] border-r border-gray-200 flex flex-col">
        {/* Tabs */}
        <div className="flex border-b border-gray-200">
          {(['all', 'calls', 'emails', 'invoices'] as Tab[]).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
                activeTab === tab
                  ? 'text-brand border-b-2 border-brand'
                  : 'text-gray-500 hover:text-gray-900'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* Items List */}
        <div className="flex-1 overflow-y-auto">
          {filteredItems.map((item) => (
            <div
              key={item.id}
              onClick={() => setSelectedItem(item)}
              className={`p-4 border-b border-gray-200 cursor-pointer hover:bg-gray-50 transition-colors ${
                selectedItem.id === item.id ? 'bg-gray-50' : ''
              }`}
            >
              <div className="flex items-start gap-3">
                {getIcon(item.type)}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-semibold text-gray-900">{item.vendor}</span>
                    {item.unread && <div className="w-2 h-2 bg-status-blue rounded-full" />}
                  </div>
                  <p className="text-sm text-gray-500 truncate">{item.preview}</p>
                  <p className="text-xs text-gray-400 mt-1">{item.time} · {item.date}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Detail Panel */}
      <div className="flex-1 overflow-y-auto">
        {selectedItem && (
          <div className="p-8">
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                {selectedItem.type === 'call' ? 'Call' : selectedItem.type === 'email' ? 'Email' : 'Invoice'} with {selectedItem.vendor}
              </h2>
              <div className="flex items-center gap-4 text-sm text-gray-500">
                {selectedItem.type === 'call' && <span>{selectedItem.time} duration</span>}
                <span>{selectedItem.date}</span>
              </div>
            </div>

            {selectedItem.type === 'call' && (
              <>
                {/* Audio Player */}
                <div className="bg-gray-50 rounded-lg p-6 mb-6">
                  <div className="flex items-center gap-4 mb-4">
                    <button
                      onClick={() => setIsPlaying(!isPlaying)}
                      className="w-12 h-12 bg-brand hover:bg-brand-dark text-white rounded-full flex items-center justify-center transition-colors"
                    >
                      {isPlaying ? <Pause size={20} /> : <Play size={20} className="ml-1" />}
                    </button>
                    <div className="flex-1">
                      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div className="h-full bg-brand" style={{ width: '35%' }} />
                      </div>
                      <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
                        <span>0:45</span>
                        <span>{selectedItem.time}</span>
                      </div>
                    </div>
                    <button className="text-sm text-gray-500 hover:text-gray-900">1x</button>
                  </div>
                </div>

                {/* Transcript */}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Transcript</h3>
                  <div className="space-y-4 font-mono text-sm">
                    <div>
                      <span className="text-gray-500">[0:00]</span>{' '}
                      <span className="font-semibold text-gray-900">Agent:</span>{' '}
                      <span className="text-gray-700">Hi, I'm calling on behalf of Sweet Dreams Bakery...</span>
                    </div>
                    <div>
                      <span className="text-gray-500">[0:12]</span>{' '}
                      <span className="font-semibold text-gray-900">Vendor:</span>{' '}
                      <span className="text-gray-700">How can I help?</span>
                    </div>
                    <div>
                      <span className="text-gray-500">[0:15]</span>{' '}
                      <span className="font-semibold text-gray-900">Agent:</span>{' '}
                      <span className="text-gray-700">We need 500 lbs of flour. What's your best price?</span>
                    </div>
                  </div>
                </div>

                {/* Outcome */}
                <div className="inline-flex items-center gap-2 bg-brand-light text-brand px-4 py-2 rounded-full">
                  <span className="text-sm font-medium">15% Discount</span>
                </div>
              </>
            )}

            {selectedItem.type === 'email' && (
              <div className="prose max-w-none">
                <p className="text-gray-700">{selectedItem.preview}</p>
              </div>
            )}

            {selectedItem.type === 'invoice' && (
              <div className="bg-gray-50 rounded-lg p-6">
                <h3 className="font-semibold text-gray-900 mb-4">Invoice Details</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Amount:</span>
                    <span className="font-semibold text-gray-900">$450.00</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Items:</span>
                    <span className="text-gray-900">3</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Due Date:</span>
                    <span className="text-gray-900">Jan 15, 2026</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

