'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Check, Loader2, Phone, Search, DollarSign, CreditCard, MessageSquare, MapPin, Star, X, FileText } from 'lucide-react';
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

export default function LiveOrderFlow({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [currentPhase, setCurrentPhase] = useState<Phase>('sourcing');
  const [activities, setActivities] = useState<LiveActivity[]>([]);
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [selectedVendor, setSelectedVendor] = useState<Vendor | null>(null);
  const [showTranscript, setShowTranscript] = useState(false);

  // Mock live updates - in real app, this would come from WebSocket/SSE
  useEffect(() => {
    const phases: Phase[] = ['sourcing', 'negotiating', 'evaluating', 'approval', 'payment', 'complete'];
    let phaseIndex = phases.indexOf(currentPhase);
    let activityIndex = 0;
    let vendorIndex = 0;

    const mockVendors: Vendor[] = [
      { 
        id: '1', 
        vendor_name: 'Bay Area Foods Co', 
        location: 'San Francisco, CA', 
        distance_miles: 12.5,
        phone: '(415) 555-0123',
        price_per_unit: 0.42,
        unit: 'lb',
        products: ['Flour', 'Sugar', 'Grains'],
        final_score: 8.5,
        status: 'found' 
      },
      { 
        id: '2', 
        vendor_name: 'Golden Gate Grains', 
        location: 'Oakland, CA', 
        distance_miles: 8.2,
        phone: '(510) 555-0456',
        price_per_unit: 0.38,
        unit: 'lb',
        products: ['Flour', 'Grains'],
        final_score: 8.2,
        status: 'found' 
      },
      { 
        id: '3', 
        vendor_name: 'Fresh Farms', 
        location: 'Berkeley, CA', 
        distance_miles: 5.8,
        phone: '(510) 555-0789',
        price_per_unit: 0.35,
        unit: 'lb',
        products: ['Flour', 'Butter', 'Dairy'],
        final_score: 7.8,
        status: 'found' 
      },
    ];

    const phaseActivities = {
      sourcing: [
        { message: 'Searching for local vendors in your area...', type: 'info' as const },
        { message: 'Found Bay Area Foods Co - San Francisco, CA', type: 'success' as const },
        { message: 'Found Golden Gate Grains - Oakland, CA', type: 'success' as const },
        { message: 'Found Fresh Farms - Berkeley, CA', type: 'success' as const },
        { message: 'Found 12 vendors total', type: 'success' as const },
      ],
      negotiating: [
        { message: 'Starting negotiations with top vendors...', type: 'info' as const },
        { message: '📞 Calling Bay Area Foods Co...', type: 'info' as const },
        { message: '✓ Bay Area Foods answered - negotiating...', type: 'success' as const },
        { message: '✓ Bay Area Foods: 15% discount offered', type: 'success' as const },
        { message: '📞 Calling Golden Gate Grains...', type: 'info' as const },
        { message: '✓ Golden Gate Grains answered - negotiating...', type: 'success' as const },
        { message: '✓ Golden Gate Grains: 12% discount offered', type: 'success' as const },
        { message: '📞 Calling Fresh Farms...', type: 'info' as const },
        { message: '✓ Fresh Farms answered - negotiating...', type: 'success' as const },
        { message: '✓ Fresh Farms: 18% discount offered', type: 'success' as const },
      ],
      evaluating: [
        { message: 'Evaluating all offers...', type: 'info' as const },
        { message: 'Comparing prices, quality, and delivery terms...', type: 'info' as const },
        { message: 'Best deal identified: Fresh Farms (18% discount)', type: 'success' as const },
      ],
      approval: [
        { message: 'Preparing order summary for approval...', type: 'info' as const },
        { message: 'Order ready: $842.50 (18% savings)', type: 'success' as const },
      ],
      payment: [
        { message: 'Processing payment authorization...', type: 'info' as const },
        { message: 'x402 authorization approved', type: 'success' as const },
        { message: 'Submitting payment to vendor...', type: 'info' as const },
        { message: 'Payment confirmed! Transaction: 0xA3F8...', type: 'success' as const },
      ],
    };

    const interval = setInterval(() => {
      const currentActivities = phaseActivities[currentPhase];
      
      // Handle vendor updates during sourcing
      if (currentPhase === 'sourcing' && vendorIndex < mockVendors.length) {
        setVendors(prev => [...prev, mockVendors[vendorIndex]]);
        vendorIndex++;
      }
      
      // Handle vendor status updates during negotiation - all called simultaneously
      if (currentPhase === 'negotiating') {
        if (activityIndex === 1) {
          // Start calling all vendors at once
          setVendors(prev => prev.map(v => ({ ...v, status: 'calling' })));
        } else if (activityIndex === 2) {
          // Vendor 1 answers
          setVendors(prev => prev.map(v => v.id === '1' ? { ...v, status: 'talking' } : v));
        } else if (activityIndex === 3) {
          // Vendor 1 negotiation complete
          setVendors(prev => prev.map(v => v.id === '1' ? { ...v, status: 'answered', discount: 15, callDuration: '2:34', transcript: '[0:00] Agent: Hi, I\'m calling on behalf of Sweet Dreams Bakery...\n[0:12] Vendor: How can I help?\n[0:15] Agent: We need 500 lbs of flour monthly. What\'s your best bulk price?\n[0:45] Vendor: For that volume, I can offer 15% off our standard rate.\n[1:20] Agent: That works for us. What about delivery?\n[1:45] Vendor: We deliver within 3-5 business days.\n[2:10] Agent: Perfect. We\'ll be in touch. Thank you!' } : v));
        } else if (activityIndex === 4) {
          // Vendor 2 answers
          setVendors(prev => prev.map(v => v.id === '2' ? { ...v, status: 'talking' } : v));
        } else if (activityIndex === 5) {
          // Vendor 2 goes to voicemail
          setVendors(prev => prev.map(v => v.id === '2' ? { ...v, status: 'voicemail', callDuration: '0:15', transcript: '[0:00] Agent: (Voicemail) Hi, this is calling on behalf of Sweet Dreams Bakery. We\'re interested in bulk flour orders...' } : v));
        } else if (activityIndex === 6) {
          // Vendor 3 answers
          setVendors(prev => prev.map(v => v.id === '3' ? { ...v, status: 'talking' } : v));
        } else if (activityIndex === 7) {
          // Vendor 3 negotiation complete
          setVendors(prev => prev.map(v => v.id === '3' ? { ...v, status: 'answered', discount: 18, callDuration: '3:12', transcript: '[0:00] Agent: Hi, calling about flour supply for our bakery...\n[0:08] Vendor: Yes, how can I help?\n[0:20] Agent: We need 500 lbs monthly. What\'s your best bulk rate?\n[0:55] Vendor: For that volume, I can offer 18% discount off our list price.\n[1:30] Agent: Excellent! That\'s the best we\'ve heard. Can you deliver?\n[2:00] Vendor: Yes, we deliver within 2 days. Free delivery for orders over $500.\n[2:45] Agent: Perfect. We\'ll be in touch. Thank you!' } : v));
        }
      }
      
      if (currentActivities && activityIndex < currentActivities.length) {
        const activity = currentActivities[activityIndex];
        setActivities(prev => [...prev, {
          id: Date.now().toString(),
          timestamp: new Date(),
          ...activity,
        }]);
        activityIndex++;
      } else if (phaseIndex < phases.length - 1) {
        // Move to next phase
        phaseIndex++;
        setCurrentPhase(phases[phaseIndex]);
        activityIndex = 0;
        
        // Initialize vendors for negotiation phase
        if (phases[phaseIndex] === 'negotiating' && vendors.length === 0) {
          setVendors(mockVendors.slice(0, 3));
        }
      } else {
        // Complete - redirect to orders after a moment
        setTimeout(() => {
          router.push('/orders');
        }, 3000);
        clearInterval(interval);
      }
    }, 2000); // Update every 2 seconds

    return () => clearInterval(interval);
  }, [currentPhase, vendors.length, router]);

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
                    {vendors.find(v => v.discount === 18)?.vendor_name || 'Fresh Farms'}
                  </h3>
                  <div className="flex items-center gap-2 text-sm text-gray-500 mb-4">
                    <MapPin size={14} />
                    <span>{vendors.find(v => v.discount === 18)?.location || 'Berkeley, CA'}</span>
                    {vendors.find(v => v.discount === 18)?.distance_miles && (
                      <>
                        <span>•</span>
                        <span>{vendors.find(v => v.discount === 18)?.distance_miles.toFixed(1)} mi</span>
                      </>
                    )}
                  </div>
                  <p className="text-4xl font-bold text-brand mb-4">$842.50</p>
                  <div className="flex items-center gap-4 text-sm text-gray-500 mb-6">
                    <span>3 items</span>
                    <span>•</span>
                    <span>Delivery</span>
                    <span>•</span>
                    <span>Arrives Jan 12</span>
                  </div>
                  <div className="inline-block bg-brand-light text-brand px-4 py-2 rounded-full text-sm font-medium mb-6">
                    Saved $138 (18%)
                  </div>
                  <div className="flex gap-4">
                    <button 
                      onClick={() => setCurrentPhase('payment')}
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

            {currentPhase === 'complete' && (
              <div className="w-full max-w-2xl mt-6">
                <div className="bg-brand-light rounded-lg p-8">
                  <p className="text-lg text-gray-900 mb-4">Your order has been successfully placed!</p>
                  <div className="space-y-2 text-sm text-gray-600 mb-6">
                    <p>Vendor: Fresh Farms</p>
                    <p>Total: $842.50</p>
                    <p>Transaction: 0xA3F8...5678</p>
                  </div>
                  <Link
                    href="/orders"
                    className="inline-block bg-brand hover:bg-brand-dark text-white font-medium px-6 py-3 rounded-lg transition-colors"
                  >
                    View All Orders
                  </Link>
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
                <h3 className="text-xl font-semibold text-gray-900">{selectedVendor.name}</h3>
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

