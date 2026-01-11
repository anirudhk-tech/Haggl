'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Check, Loader2, Phone, Search, DollarSign, CreditCard, MessageSquare, MapPin, Star, X, FileText, Wifi, WifiOff } from 'lucide-react';
import Link from 'next/link';

type Phase = 'sourcing' | 'negotiating' | 'evaluating' | 'approval' | 'payment' | 'complete';

interface LiveActivity {
  id: string;
  timestamp: Date;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
}

interface Vendor {
  id: string;
  vendor_name: string;
  location: string;
  distance_miles?: number;
  phone?: string;
  email?: string;
  price_per_unit?: number;
  unit?: string;
  products?: string[];
  status: 'found' | 'calling' | 'talking' | 'answered' | 'declined' | 'voicemail' | 'negotiated' | 'completed';
  discount?: number;
  callDuration?: string;
  transcript?: string;
  final_score?: number;
}

// Map backend stages to frontend phases
const stageToPhase: Record<string, Phase> = {
  'idle': 'sourcing',
  'sourcing': 'sourcing',
  'calling': 'negotiating',
  'negotiating': 'negotiating',
  'evaluating': 'evaluating',
  'approval_pending': 'approval',
  'approved': 'payment',
  'paying': 'payment',
  'payment_complete': 'complete',
  'completed': 'complete',
  'failed': 'complete',
};

export default function LiveOrderFlow({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [currentPhase, setCurrentPhase] = useState<Phase>('sourcing');
  const [activities, setActivities] = useState<LiveActivity[]>([]);
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [selectedVendor, setSelectedVendor] = useState<Vendor | null>(null);
  const [showTranscript, setShowTranscript] = useState(false);
  const [connected, setConnected] = useState(false);
  const [bestVendor, setBestVendor] = useState<{ name: string; price: number; discount?: number } | null>(null);
  const [paymentInfo, setPaymentInfo] = useState<{ 
    status: string; 
    confirmation?: string; 
    receipt_url?: string; 
    amount?: number;
    vendor_name?: string;
  } | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  // Connect to SSE stream
  useEffect(() => {
    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
    
    const connect = () => {
      const eventSource = new EventSource(`${API_URL}/events/stream`);
      eventSourceRef.current = eventSource;
      
      eventSource.onopen = () => {
        setConnected(true);
        console.log('SSE connected for order:', params.id);
      };
      
      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          // Map stage to phase
          if (data.stage) {
            const newPhase = stageToPhase[data.stage] || 'sourcing';
            setCurrentPhase(newPhase);
          }
          
          // Add activity
          if (data.message) {
            const activityType = 
              data.level === 'error' ? 'error' :
              data.level === 'warning' ? 'warning' :
              data.type === 'stage_change' ? 'info' :
              'success';
            
            setActivities(prev => [{
              id: Date.now().toString(),
              timestamp: new Date(data.timestamp),
              message: data.message,
              type: activityType,
            }, ...prev.slice(0, 49)]);
          }
          
          // Handle vendor updates from call_update events
          if (data.type === 'call_update' && data.data) {
            const callData = data.data;
            setVendors(prev => {
              const existing = prev.find(v => v.vendor_name === callData.vendor_name);
              if (existing) {
                return prev.map(v => 
                  v.vendor_name === callData.vendor_name 
                    ? { 
                        ...v, 
                        status: callData.status === 'initiated' ? 'calling' : 
                               callData.status === 'completed' ? 'answered' : 
                               callData.status === 'failed' ? 'declined' : v.status,
                        price_per_unit: callData.price || v.price_per_unit,
                      }
                    : v
                );
              } else {
                return [...prev, {
                  id: callData.vendor_id || Date.now().toString(),
                  vendor_name: callData.vendor_name,
                  location: 'Nearby',
                  status: 'calling',
                }];
              }
            });
          }
          
          // Handle sourcing results
          if (data.stage === 'sourcing' && data.message?.includes('Found')) {
            const match = data.message.match(/Found (\d+) vendors/);
            if (match) {
              // Vendors will be populated via call_update events
            }
          }
          
          // Handle approval pending - extract best vendor info
          if (data.type === 'approval_required' && data.data) {
            setBestVendor({
              name: data.data.vendor_name,
              price: data.data.price,
            });
          }
          
          // Handle payment updates
          if (data.type === 'payment_update' && data.data) {
            setPaymentInfo({
              status: data.data.status,
              confirmation: data.data.confirmation,
              receipt_url: data.data.receipt_url,
              amount: data.data.amount,
              vendor_name: data.data.vendor_name,
            });
          }
          
          // Handle completion
          if (data.stage === 'payment_complete' || data.stage === 'completed') {
            setTimeout(() => {
              router.push('/orders');
            }, 5000);
          }
          
        } catch (e) {
          console.error('Failed to parse SSE event:', e);
        }
      };
      
      eventSource.onerror = () => {
        setConnected(false);
        eventSource.close();
        // Reconnect after delay
        setTimeout(connect, 3000);
      };
    };
    
    connect();
    
    return () => {
      eventSourceRef.current?.close();
    };
  }, [params.id, router]);

  const getPhaseConfig = (phase: Phase) => {
    const configs = {
      sourcing: {
        title: 'Finding Local Vendors',
        icon: Search,
        color: 'status-blue',
        borderColor: 'border-status-blue',
        bgColor: 'bg-status-blue-light',
        textColor: 'text-status-blue',
        description: 'Searching for suppliers in your area...',
      },
      negotiating: {
        title: 'Negotiating Prices',
        icon: Phone,
        color: 'status-orange',
        borderColor: 'border-status-orange',
        bgColor: 'bg-status-orange-light',
        textColor: 'text-status-orange',
        description: 'Making calls to get the best deals...',
      },
      evaluating: {
        title: 'Evaluating Offers',
        icon: DollarSign,
        color: 'status-blue',
        borderColor: 'border-status-blue',
        bgColor: 'bg-status-blue-light',
        textColor: 'text-status-blue',
        description: 'Comparing all vendor offers...',
      },
      approval: {
        title: 'Awaiting Your Approval',
        icon: MessageSquare,
        color: 'status-yellow',
        borderColor: 'border-status-yellow',
        bgColor: 'bg-status-yellow-light',
        textColor: 'text-status-yellow',
        description: 'Review and approve the best deal...',
      },
      payment: {
        title: 'Processing Payment',
        icon: CreditCard,
        color: 'status-purple',
        borderColor: 'border-status-purple',
        bgColor: 'bg-status-purple-light',
        textColor: 'text-status-purple',
        description: 'Completing the transaction...',
      },
      complete: {
        title: 'Order Complete!',
        icon: Check,
        color: 'brand',
        borderColor: 'border-brand',
        bgColor: 'bg-brand-light',
        textColor: 'text-brand',
        description: 'Your order has been successfully placed.',
      },
    };
    return configs[phase];
  };

  const phaseConfig = getPhaseConfig(currentPhase);
  const PhaseIcon = phaseConfig.icon;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-[1100px] mx-auto px-16 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link
                href="/orders"
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft size={20} className="text-gray-600" />
              </Link>
              <div>
                <h1 className="text-lg font-semibold text-gray-900">{params.id}</h1>
                <p className="text-xs text-gray-500">Live Order Flow</p>
              </div>
            </div>
            <div className={`flex items-center gap-2 ${connected ? 'text-brand' : 'text-gray-400'}`}>
              {connected ? (
                <>
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-brand"></span>
                  </span>
                  <Wifi size={16} />
                  <span className="text-xs font-medium">Connected</span>
                </>
              ) : (
                <>
                  <WifiOff size={16} />
                  <span className="text-xs font-medium">Connecting...</span>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content - Full Screen Phase View */}
      <div className="max-w-[1100px] mx-auto px-16 py-12">
        {/* Current Phase Card - Takes Full Focus */}
        <div className={`bg-white rounded-xl shadow-lg p-12 mb-8 border-l-4 ${phaseConfig.borderColor}`}>
          <div className="flex flex-col items-center text-center">
            <div className={`w-20 h-20 rounded-full ${phaseConfig.bgColor} flex items-center justify-center mb-6`}>
              {currentPhase === 'complete' ? (
                <Check className={phaseConfig.textColor} size={40} />
              ) : (
                <Loader2 className={`${phaseConfig.textColor} animate-spin`} size={40} />
              )}
            </div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">{phaseConfig.title}</h2>
            <p className="text-lg text-gray-500 mb-8">{phaseConfig.description}</p>

            {/* Phase-specific content */}
            {currentPhase === 'sourcing' && vendors.length > 0 && (
              <div className="w-full max-w-4xl mt-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Vendors Found ({vendors.length})</h3>
                <div className="bg-white rounded-lg border border-gray-200 divide-y divide-gray-200">
                  {vendors.map((vendor) => (
                    <div key={vendor.id} className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4 flex-1">
                          <div className="w-2 h-2 rounded-full bg-brand" />
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-1">
                              <h4 className="font-semibold text-gray-900">{vendor.vendor_name}</h4>
                              {vendor.final_score && (
                                <span className="text-xs text-gray-500 font-mono">
                                  Score: {vendor.final_score.toFixed(1)}
                                </span>
                              )}
                            </div>
                            <div className="flex items-center gap-4 text-xs text-gray-500">
                              <div className="flex items-center gap-1">
                                <MapPin size={12} />
                                <span>{vendor.location}</span>
                              </div>
                              {vendor.distance_miles && (
                                <>
                                  <span>•</span>
                                  <span>{vendor.distance_miles.toFixed(1)} mi</span>
                                </>
                              )}
                              {vendor.price_per_unit && (
                                <>
                                  <span>•</span>
                                  <span className="font-mono">${vendor.price_per_unit.toFixed(2)}/{vendor.unit}</span>
                                </>
                              )}
                            </div>
                            {vendor.products && vendor.products.length > 0 && (
                              <div className="flex flex-wrap gap-1 mt-2">
                                {vendor.products.slice(0, 3).map((product, idx) => (
                                  <span key={idx} className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
                                    {product}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {currentPhase === 'negotiating' && (
              <div className="w-full max-w-4xl mt-6">
                <div className="bg-status-orange-light rounded-lg p-4 mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 bg-status-orange rounded-full animate-pulse" />
                    <span className="font-semibold text-status-orange">Live: Calling all vendors simultaneously</span>
                  </div>
                </div>
                <div className="bg-white rounded-lg border border-gray-200 divide-y divide-gray-200">
                  {vendors.map((vendor) => (
                    <div
                      key={vendor.id}
                      onClick={() => {
                        if (vendor.transcript) {
                          setSelectedVendor(vendor);
                          setShowTranscript(true);
                        }
                      }}
                      className={`p-4 hover:bg-gray-50 transition-colors ${
                        vendor.transcript ? 'cursor-pointer' : ''
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4 flex-1">
                          {/* Status Indicator */}
                          <div className="flex-shrink-0">
                            {vendor.status === 'calling' && (
                              <Loader2 className="text-status-orange animate-spin" size={20} />
                            )}
                            {vendor.status === 'talking' && (
                              <div className="w-5 h-5 rounded-full bg-status-orange flex items-center justify-center">
                                <Phone className="text-white" size={12} />
                              </div>
                            )}
                            {vendor.status === 'answered' && (
                              <Check className="text-brand" size={20} />
                            )}
                            {vendor.status === 'voicemail' && (
                              <MessageSquare className="text-status-yellow" size={20} />
                            )}
                            {vendor.status === 'declined' && (
                              <X className="text-status-rose" size={20} />
                            )}
                            {vendor.status === 'found' && (
                              <div className="w-5 h-5 rounded-full bg-gray-300" />
                            )}
                          </div>

                          {/* Vendor Info */}
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-3 mb-1">
                              <h4 className="font-semibold text-gray-900">{vendor.vendor_name}</h4>
                              {vendor.final_score && (
                                <span className="text-xs text-gray-500 font-mono">
                                  Score: {vendor.final_score.toFixed(1)}
                                </span>
                              )}
                            </div>
                            <div className="flex items-center gap-4 text-xs text-gray-500">
                              <div className="flex items-center gap-1">
                                <MapPin size={12} />
                                <span>{vendor.location}</span>
                              </div>
                              {vendor.distance_miles && (
                                <>
                                  <span>•</span>
                                  <span>{vendor.distance_miles.toFixed(1)} mi</span>
                                </>
                              )}
                              {vendor.price_per_unit && (
                                <>
                                  <span>•</span>
                                  <span className="font-mono">${vendor.price_per_unit.toFixed(2)}/{vendor.unit}</span>
                                </>
                              )}
                            </div>
                            {vendor.products && vendor.products.length > 0 && (
                              <div className="flex flex-wrap gap-1 mt-2">
                                {vendor.products.slice(0, 3).map((product, idx) => (
                                  <span key={idx} className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
                                    {product}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>

                          {/* Status Text */}
                          <div className="flex-shrink-0 text-right">
                            {vendor.status === 'calling' && (
                              <span className="text-sm text-status-orange font-medium">Calling...</span>
                            )}
                            {vendor.status === 'talking' && (
                              <span className="text-sm text-status-orange font-medium">Talking...</span>
                            )}
                            {vendor.status === 'answered' && (
                              <div className="text-right">
                                <div className="text-sm font-semibold text-brand">{vendor.discount}% discount</div>
                                {vendor.callDuration && (
                                  <div className="text-xs text-gray-500">{vendor.callDuration}</div>
                                )}
                                {vendor.transcript && (
                                  <div className="text-xs text-brand mt-1 flex items-center gap-1 justify-end">
                                    <FileText size={12} />
                                    Transcript
                                  </div>
                                )}
                              </div>
                            )}
                            {vendor.status === 'voicemail' && (
                              <div className="text-right">
                                <span className="text-sm text-status-yellow font-medium">Left voicemail</span>
                                {vendor.callDuration && (
                                  <div className="text-xs text-gray-500">{vendor.callDuration}</div>
                                )}
                              </div>
                            )}
                            {vendor.status === 'declined' && (
                              <span className="text-sm text-status-rose font-medium">Declined</span>
                            )}
                            {vendor.status === 'found' && (
                              <span className="text-sm text-gray-400">Queued</span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {currentPhase === 'evaluating' && (
              <div className="w-full max-w-2xl mt-6">
                <div className="bg-gray-50 rounded-lg p-8 text-center">
                  <Loader2 className="text-status-blue animate-spin mx-auto mb-4" size={32} />
                  <p className="text-lg text-gray-700 mb-2">Evaluating all offers...</p>
                  <p className="text-sm text-gray-500">
                    Comparing prices, quality, delivery terms, and reliability scores
                  </p>
                </div>
              </div>
            )}

            {currentPhase === 'approval' && (
              <div className="w-full max-w-2xl mt-6">
                <div className="bg-gray-50 rounded-lg p-8">
                  <div className="mb-4">
                    <span className="inline-block bg-brand text-white px-3 py-1 rounded-full text-xs font-medium mb-2">
                      Best Deal Selected
                    </span>
                  </div>
                  <h3 className="text-2xl font-semibold text-gray-900 mb-2">
                    {bestVendor?.name || vendors.find(v => v.discount === 18)?.vendor_name || 'Best Vendor'}
                  </h3>
                  <div className="flex items-center gap-2 text-sm text-gray-500 mb-4">
                    <MapPin size={14} />
                    <span>{vendors.find(v => v.discount === 18)?.location || 'Nearby'}</span>
                    {vendors.find(v => v.discount === 18)?.distance_miles != null && (
                      <>
                        <span>•</span>
                        <span>{(vendors.find(v => v.discount === 18)?.distance_miles ?? 0).toFixed(1)} mi</span>
                      </>
                    )}
                  </div>
                  <p className="text-4xl font-bold text-brand mb-4">
                    ${bestVendor?.price?.toFixed(2) || '0.00'}
                  </p>
                  <div className="flex items-center gap-4 text-sm text-gray-500 mb-6">
                    <span>Order #{params.id}</span>
                    <span>•</span>
                    <span>Delivery</span>
                  </div>
                  {bestVendor?.discount && (
                  <div className="inline-block bg-brand-light text-brand px-4 py-2 rounded-full text-sm font-medium mb-6">
                      Saved {bestVendor.discount}%
                  </div>
                  )}
                  <div className="flex gap-4">
                    <button 
                      onClick={async () => {
                        const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
                        await fetch(`${API_URL}/orders/approve`, {
                          method: 'POST',
                          headers: { 'Content-Type': 'application/json' },
                          body: JSON.stringify({ order_id: params.id }),
                        });
                        setCurrentPhase('payment');
                      }}
                      className="flex-1 bg-brand hover:bg-brand-dark text-white font-medium px-6 py-3 rounded-lg transition-colors"
                    >
                      Approve & Pay
                    </button>
                    <button className="flex-1 bg-white hover:bg-status-rose-light text-status-rose border border-status-rose font-medium px-6 py-3 rounded-lg transition-colors">
                      Reject
                    </button>
                  </div>
                </div>
              </div>
            )}

            {currentPhase === 'payment' && (
              <div className="w-full max-w-2xl mt-6">
                <div className="bg-gray-50 rounded-lg p-8 text-center">
                  <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-status-purple-light flex items-center justify-center">
                    <CreditCard className="text-status-purple animate-pulse" size={32} />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">Processing Payment</h3>
                  <p className="text-gray-500 mb-4">
                    {paymentInfo?.status === 'processing' 
                      ? `Paying ${paymentInfo?.vendor_name || bestVendor?.name}...`
                      : 'Preparing secure payment...'
                    }
                  </p>
                  {paymentInfo?.amount && (
                    <p className="text-2xl font-bold text-status-purple">${paymentInfo.amount.toFixed(2)}</p>
                  )}
                  <div className="mt-6 flex items-center justify-center gap-2 text-sm text-gray-400">
                    <Loader2 size={16} className="animate-spin" />
                    <span>Securely processing via mock payment</span>
                  </div>
                </div>
              </div>
            )}

            {currentPhase === 'complete' && (
              <div className="w-full max-w-2xl mt-6">
                <div className="bg-brand-light rounded-lg p-8 text-center">
                  <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-brand flex items-center justify-center">
                    <Check className="text-white" size={32} />
                  </div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">Payment Complete!</h2>
                  <p className="text-lg text-gray-600 mb-6">Your order has been successfully placed.</p>
                  <div className="bg-white rounded-lg p-6 mb-6 text-left">
                    <div className="space-y-3 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-500">Vendor</span>
                        <span className="font-medium text-gray-900">{paymentInfo?.vendor_name || bestVendor?.name || 'Vendor'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Amount Paid</span>
                        <span className="font-medium text-brand">${paymentInfo?.amount?.toFixed(2) || bestVendor?.price?.toFixed(2) || '0.00'}</span>
                      </div>
                      {paymentInfo?.confirmation && (
                        <div className="flex justify-between">
                          <span className="text-gray-500">Confirmation</span>
                          <span className="font-mono text-xs text-gray-900">{paymentInfo.confirmation}</span>
                        </div>
                      )}
                      <div className="flex justify-between">
                        <span className="text-gray-500">Order ID</span>
                        <span className="font-mono text-xs text-gray-900">{params.id}</span>
                      </div>
                    </div>
                  </div>
                  {paymentInfo?.receipt_url && (
                    <a
                      href={paymentInfo.receipt_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-brand hover:underline mb-4 inline-block"
                    >
                      View Receipt →
                    </a>
                  )}
                  <div className="mt-4">
                    <Link
                      href="/orders"
                      className="inline-block bg-brand hover:bg-brand-dark text-white font-medium px-6 py-3 rounded-lg transition-colors"
                    >
                      View All Orders
                    </Link>
                  </div>
                  <p className="text-xs text-gray-400 mt-4">Redirecting in 5 seconds...</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Live Activity Feed */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Activity Log</h3>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {activities.length === 0 ? (
              <p className="text-sm text-gray-500 text-center py-8">Waiting for activity...</p>
            ) : (
              activities.map((activity) => (
                <div key={activity.id} className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50 transition-colors">
                  <div className={`w-2 h-2 rounded-full mt-2 ${
                    activity.type === 'success' ? 'bg-brand' :
                    activity.type === 'warning' ? 'bg-status-yellow' :
                    activity.type === 'error' ? 'bg-status-rose' :
                    'bg-status-blue'
                  }`} />
                  <div className="flex-1">
                    <p className={`text-sm ${
                      activity.type === 'success' ? 'text-brand' :
                      activity.type === 'warning' ? 'text-status-yellow' :
                      activity.type === 'error' ? 'text-status-rose' :
                      'text-gray-900'
                    }`}>
                      {activity.message}
                    </p>
                    <p className="text-xs text-gray-400 mt-1">
                      {activity.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Transcript Modal */}
      {showTranscript && selectedVendor && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-lg max-w-2xl w-full max-h-[80vh] overflow-hidden flex flex-col">
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <div>
                <h3 className="text-xl font-semibold text-gray-900">{selectedVendor.vendor_name}</h3>
                <p className="text-sm text-gray-500">{selectedVendor.location}</p>
              </div>
              <button
                onClick={() => {
                  setShowTranscript(false);
                  setSelectedVendor(null);
                }}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X size={20} className="text-gray-500" />
              </button>
            </div>
            <div className="p-6 overflow-y-auto flex-1">
              <div className="mb-6 space-y-2">
                <div className="flex items-center gap-4 text-sm text-gray-600">
                  {selectedVendor.callDuration && (
                    <span>Duration: {selectedVendor.callDuration}</span>
                  )}
                  {selectedVendor.discount && (
                    <span className="font-semibold text-brand">Discount: {selectedVendor.discount}%</span>
                  )}
                </div>
                {selectedVendor.phone && (
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Phone size={14} />
                    <span className="font-mono">{selectedVendor.phone}</span>
                  </div>
                )}
                {selectedVendor.price_per_unit && (
                  <div className="text-sm text-gray-600">
                    Price: <span className="font-mono">${selectedVendor.price_per_unit.toFixed(2)}/{selectedVendor.unit}</span>
                  </div>
                )}
              </div>
              <div className="bg-gray-50 rounded-lg p-4 font-mono text-sm space-y-3">
                {selectedVendor.transcript?.split('\n').map((line, idx) => (
                  <div key={idx} className="text-gray-700">
                    {line}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

