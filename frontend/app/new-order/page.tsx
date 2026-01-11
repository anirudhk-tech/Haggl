'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Check, ShoppingCart } from 'lucide-react';
import Link from 'next/link';

// Mock saved products - in real app, this would come from API
const savedProducts = [
  { id: 1, name: 'All-Purpose Flour', category: 'Dry Goods', unit: 'lbs', typicalQuantity: 200 },
  { id: 2, name: 'Butter', category: 'Dairy', unit: 'lbs', typicalQuantity: 100 },
  { id: 3, name: 'Sugar', category: 'Dry Goods', unit: 'lbs', typicalQuantity: 150 },
  { id: 4, name: 'Eggs', category: 'Dairy', unit: 'dozen', typicalQuantity: 50 },
  { id: 5, name: 'Vanilla Extract', category: 'Flavorings', unit: 'oz', typicalQuantity: 10 },
];

export default function NewOrder() {
  const router = useRouter();
  const [selectedProducts, setSelectedProducts] = useState<number[]>([]);
  const [quantities, setQuantities] = useState<Record<number, number>>({});
  const [isCreating, setIsCreating] = useState(false);
  const [deliveryDate, setDeliveryDate] = useState<string>(() => {
    // Default to 3 days from now
    const date = new Date();
    date.setDate(date.getDate() + 3);
    return date.toISOString().split('T')[0];
  });
  const [deliveryAddress, setDeliveryAddress] = useState<string>('');

  // Check if onboarding is complete
  useEffect(() => {
    const onboardingComplete = localStorage.getItem('onboarding_complete');
    if (!onboardingComplete) {
      router.push('/onboarding');
    }
  }, [router]);

  const toggleProduct = (productId: number) => {
    setSelectedProducts(prev =>
      prev.includes(productId)
        ? prev.filter(id => id !== productId)
        : [...prev, productId]
    );
    
    // Set default quantity when selecting
    if (!selectedProducts.includes(productId)) {
      const product = savedProducts.find(p => p.id === productId);
      if (product) {
        setQuantities(prev => ({
          ...prev,
          [productId]: product.typicalQuantity
        }));
      }
    }
  };

  const updateQuantity = (productId: number, quantity: number) => {
    setQuantities(prev => ({
      ...prev,
      [productId]: quantity
    }));
  };

  const handleCreateOrder = async () => {
    if (selectedProducts.length === 0) return;

    setIsCreating(true);
    
    try {
      // Get business ID from localStorage (set during onboarding)
      const businessId = localStorage.getItem('business_id') || 'demo-business';
      
      // Build items from selected products
      const items = selectedProductsList.map(product => ({
        product: product.name,
        quantity: quantities[product.id] || product.typicalQuantity,
        unit: product.unit,
      }));
      
      // Call backend to create order and start agent flow
      const response = await fetch('http://localhost:8001/orders/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          business_id: businessId,
          items,
          delivery_date: deliveryDate,
          delivery_address: deliveryAddress,
        }),
      });
      
      const data = await response.json();
      
      if (response.ok && data.order_id) {
        // Redirect to live flow with real order ID
        router.push(`/orders/${data.order_id}/live`);
      } else {
        console.error('Failed to create order:', data);
        setIsCreating(false);
      }
    } catch (error) {
      console.error('Error creating order:', error);
      setIsCreating(false);
    }
  };

  const selectedProductsList = savedProducts.filter(p => selectedProducts.includes(p.id));

  return (
    <div className="max-w-[1100px] mx-auto px-16 py-12">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">New Order</h1>
          <p className="text-sm text-gray-500 mt-1">Select products from your list to order</p>
        </div>
        <Link
          href="/products"
          className="text-sm text-brand hover:text-brand-dark"
        >
          Manage Products →
        </Link>
      </div>

      {/* Products Selection */}
      {savedProducts.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm p-12 text-center">
          <ShoppingCart className="mx-auto mb-4 text-gray-400" size={48} />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">No products yet</h2>
          <p className="text-sm text-gray-500 mb-6">
            Add products to your list first, then you can quickly order them here.
          </p>
          <Link
            href="/onboarding"
            className="inline-block bg-brand hover:bg-brand-dark text-white font-medium px-6 py-2.5 rounded-lg transition-colors"
          >
            Set Up Products
          </Link>
        </div>
      ) : (
        <>
          {/* Products Grid */}
          <div className="grid grid-cols-2 gap-4 mb-8">
            {savedProducts.map((product) => {
              const isSelected = selectedProducts.includes(product.id);
              const quantity = quantities[product.id] || product.typicalQuantity;

              return (
                <div
                  key={product.id}
                  onClick={() => toggleProduct(product.id)}
                  className={`p-6 border-2 rounded-xl cursor-pointer transition-all ${
                    isSelected
                      ? 'border-brand bg-brand-light'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold text-gray-900">{product.name}</h3>
                        {isSelected && <Check className="text-brand" size={18} />}
                      </div>
                      <p className="text-xs text-gray-500">{product.category}</p>
                    </div>
                  </div>

                  {isSelected && (
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <label className="block text-xs font-medium text-gray-700 mb-2">
                        Quantity
                      </label>
                      <div className="flex items-center gap-2">
                        <input
                          type="number"
                          value={quantity}
                          onChange={(e) => updateQuantity(product.id, parseInt(e.target.value) || 0)}
                          onClick={(e) => e.stopPropagation()}
                          className="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand"
                        />
                        <span className="text-sm text-gray-500">{product.unit}</span>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Selected Products Summary */}
          {selectedProductsList.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Order Summary</h2>
              <div className="space-y-3">
                {selectedProductsList.map((product) => (
                  <div key={product.id} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                    <div>
                      <span className="font-medium text-gray-900">{product.name}</span>
                      <span className="text-sm text-gray-500 ml-2">{product.category}</span>
                    </div>
                    <span className="font-mono text-sm text-gray-900">
                      {quantities[product.id] || product.typicalQuantity} {product.unit}
                    </span>
                  </div>
                ))}
              </div>
              
              {/* Delivery Address */}
              <div className="mt-6 pt-4 border-t border-gray-200">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Delivery Address
                </label>
                <input
                  type="text"
                  value={deliveryAddress}
                  onChange={(e) => setDeliveryAddress(e.target.value)}
                  placeholder="123 Main St, City, State ZIP"
                  className="w-full border border-gray-200 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand"
                />
                <p className="text-xs text-gray-500 mt-1">Where should this be delivered?</p>
              </div>
              
              {/* Delivery Date */}
              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Delivery Date
                </label>
                <input
                  type="date"
                  value={deliveryDate}
                  onChange={(e) => setDeliveryDate(e.target.value)}
                  min={new Date().toISOString().split('T')[0]}
                  className="w-full max-w-xs border border-gray-200 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand"
                />
                <p className="text-xs text-gray-500 mt-1">When do you need this delivered?</p>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-4">
            <Link
              href="/orders"
              className="flex-1 bg-white hover:bg-gray-50 text-gray-700 border border-gray-200 font-medium px-4 py-2.5 rounded-lg transition-colors text-center"
            >
              Cancel
            </Link>
            <button
              onClick={handleCreateOrder}
              disabled={selectedProducts.length === 0 || isCreating}
              className="flex-1 bg-brand hover:bg-brand-dark disabled:bg-gray-200 disabled:text-gray-400 text-white font-medium px-4 py-2.5 rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              {isCreating ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Creating Order...
                </>
              ) : (
                <>
                  Start Negotiation
                  <ShoppingCart size={18} />
                </>
              )}
            </button>
          </div>
        </>
      )}
    </div>
  );
}

