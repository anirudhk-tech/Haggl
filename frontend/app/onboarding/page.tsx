'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Upload, Check, ArrowRight } from 'lucide-react';

type CompanyType = 'restaurant' | 'bakery' | 'cafe' | 'retail' | 'other' | null;
type Step = 1 | 2 | 3 | 4;

const companyTypes = [
  { id: 'restaurant' as const, label: 'Restaurant', description: 'Full-service or quick-service restaurant' },
  { id: 'bakery' as const, label: 'Bakery', description: 'Bakery or pastry shop' },
  { id: 'cafe' as const, label: 'Cafe', description: 'Coffee shop or cafe' },
  { id: 'retail' as const, label: 'Retail Store', description: 'Retail or grocery store' },
  { id: 'other' as const, label: 'Other', description: 'Other business type' },
];

// Mock extracted products - in real app, this would come from AI analysis
const extractedProducts = {
  restaurant: [
    { id: 1, name: 'All-Purpose Flour', category: 'Dry Goods', unit: 'lbs', estimatedMonthly: 200 },
    { id: 2, name: 'Olive Oil', category: 'Oils', unit: 'gallons', estimatedMonthly: 10 },
    { id: 3, name: 'Tomatoes', category: 'Produce', unit: 'lbs', estimatedMonthly: 150 },
    { id: 4, name: 'Mozzarella Cheese', category: 'Dairy', unit: 'lbs', estimatedMonthly: 80 },
    { id: 5, name: 'Ground Beef', category: 'Meat', unit: 'lbs', estimatedMonthly: 120 },
    { id: 6, name: 'Pasta', category: 'Dry Goods', unit: 'lbs', estimatedMonthly: 100 },
  ],
  bakery: [
    { id: 1, name: 'All-Purpose Flour', category: 'Dry Goods', unit: 'lbs', estimatedMonthly: 500 },
    { id: 2, name: 'Butter', category: 'Dairy', unit: 'lbs', estimatedMonthly: 200 },
    { id: 3, name: 'Sugar', category: 'Dry Goods', unit: 'lbs', estimatedMonthly: 300 },
    { id: 4, name: 'Eggs', category: 'Dairy', unit: 'dozen', estimatedMonthly: 150 },
    { id: 5, name: 'Vanilla Extract', category: 'Flavorings', unit: 'oz', estimatedMonthly: 20 },
    { id: 6, name: 'Chocolate Chips', category: 'Dry Goods', unit: 'lbs', estimatedMonthly: 100 },
  ],
  cafe: [
    { id: 1, name: 'Coffee Beans', category: 'Beverages', unit: 'lbs', estimatedMonthly: 200 },
    { id: 2, name: 'Milk', category: 'Dairy', unit: 'gallons', estimatedMonthly: 50 },
    { id: 3, name: 'Syrups', category: 'Flavorings', unit: 'bottles', estimatedMonthly: 30 },
    { id: 4, name: 'Paper Cups', category: 'Supplies', unit: 'cases', estimatedMonthly: 40 },
  ],
  retail: [
    { id: 1, name: 'Packaged Goods', category: 'General', unit: 'units', estimatedMonthly: 500 },
  ],
  other: [
    { id: 1, name: 'General Supplies', category: 'General', unit: 'units', estimatedMonthly: 100 },
  ],
};

export default function Onboarding() {
  const router = useRouter();
  const [step, setStep] = useState<Step>(1);
  const [companyType, setCompanyType] = useState<CompanyType>(null);
  const [menuFile, setMenuFile] = useState<File | null>(null);
  const [menuText, setMenuText] = useState('');
  const [selectedProducts, setSelectedProducts] = useState<number[]>([]);
  const [isExtracting, setIsExtracting] = useState(false);

  const needsMenu = companyType === 'restaurant' || companyType === 'bakery';
  const products = companyType ? extractedProducts[companyType] : [];

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setMenuFile(e.target.files[0]);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setMenuFile(e.dataTransfer.files[0]);
    }
  };

  const handleExtractProducts = async () => {
    if (!companyType) return;
    
    setIsExtracting(true);
    // Simulate AI extraction
    await new Promise(resolve => setTimeout(resolve, 2000));
    setIsExtracting(false);
    setStep(3);
  };

  const toggleProduct = (productId: number) => {
    setSelectedProducts(prev =>
      prev.includes(productId)
        ? prev.filter(id => id !== productId)
        : [...prev, productId]
    );
  };

  const handleComplete = () => {
    // Save selected products to user's account
    // In real app, this would be an API call
    localStorage.setItem('onboarding_complete', 'true');
    localStorage.setItem('company_type', companyType || '');
    localStorage.setItem('selected_products', JSON.stringify(selectedProducts));
    router.push('/orders');
  };

  const handleSkip = () => {
    localStorage.setItem('onboarding_complete', 'true');
    localStorage.setItem('onboarding_skipped', 'true');
    router.push('/orders');
  };

  return (
    <div className="max-w-[1100px] mx-auto px-16 py-12">
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Let's get started</h1>
            <p className="text-sm text-gray-500">Set up your business profile in just a few steps.</p>
          </div>
          <button
            onClick={handleSkip}
            className="text-xs text-gray-500 hover:text-gray-700 transition-colors"
          >
            Skip
          </button>
        </div>

        {/* Progress Indicator */}
        <div className="flex items-center justify-center gap-4 mb-12">
          {[1, 2, 3, 4].map((s) => (
            <div key={s} className="flex items-center gap-2">
              <div className={`flex items-center justify-center w-10 h-10 rounded-full ${
                step > s ? 'bg-brand text-white' : step === s ? 'bg-brand text-white' : 'bg-gray-200 text-gray-500'
              }`}>
                {step > s ? <Check size={20} /> : s}
              </div>
              {s < 4 && (
                <div className={`w-16 h-0.5 ${step > s ? 'bg-brand' : 'bg-gray-200'}`} />
              )}
            </div>
          ))}
        </div>

        <div className="bg-white rounded-xl shadow-sm p-8">
          {/* Step 1: Company Type */}
          {step === 1 && (
            <>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">What type of business are you?</h2>
              <p className="text-sm text-gray-500 mb-8">We'll customize your experience based on your business type.</p>

              <div className="grid grid-cols-2 gap-4">
                {companyTypes.map((type) => (
                  <button
                    key={type.id}
                    onClick={() => {
                      setCompanyType(type.id);
                      if (type.id !== 'restaurant' && type.id !== 'bakery') {
                        // Skip menu step for non-restaurant/bakery
                        setTimeout(() => setStep(3), 300);
                      } else {
                        setTimeout(() => setStep(2), 300);
                      }
                    }}
                    className={`p-6 text-left border-2 rounded-xl transition-all ${
                      companyType === type.id
                        ? 'border-brand bg-brand-light'
                        : 'border-gray-200 hover:border-brand hover:bg-gray-50'
                    }`}
                  >
                    <h3 className="font-semibold text-gray-900 mb-1">{type.label}</h3>
                    <p className="text-xs text-gray-500">{type.description}</p>
                  </button>
                ))}
              </div>
            </>
          )}

          {/* Step 2: Menu Upload (Restaurant/Bakery only) */}
          {step === 2 && needsMenu && (
            <>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Upload your menu</h2>
              <p className="text-sm text-gray-500 mb-8">
                We'll analyze your menu to identify the ingredients you regularly order.
              </p>

              <div
                onDrop={handleDrop}
                onDragOver={(e) => e.preventDefault()}
                className={`border-2 border-dashed rounded-xl p-12 text-center transition-colors mb-6 ${
                  menuFile ? 'border-brand bg-brand-light' : 'border-gray-200 hover:border-brand'
                }`}
              >
                <Upload className="mx-auto mb-4 text-gray-400" size={48} />
                <p className="text-sm text-gray-900 mb-2">Drop a file here or browse</p>
                <p className="text-xs text-gray-500 mb-4">PDF, PNG, JPG, TXT</p>
                <input
                  type="file"
                  onChange={handleFileChange}
                  accept=".pdf,.png,.jpg,.jpeg,.txt"
                  className="hidden"
                  id="menu-upload"
                />
                <label
                  htmlFor="menu-upload"
                  className="inline-block bg-brand hover:bg-brand-dark text-white font-medium px-4 py-2 rounded-lg cursor-pointer transition-colors"
                >
                  Browse Files
                </label>
                {menuFile && (
                  <p className="mt-4 text-sm text-gray-900">{menuFile.name}</p>
                )}
              </div>

              <div className="flex items-center gap-4 mb-6">
                <div className="flex-1 h-px bg-gray-200" />
                <span className="text-sm text-gray-500">— or —</span>
                <div className="flex-1 h-px bg-gray-200" />
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  Paste your menu
                </label>
                <textarea
                  value={menuText}
                  onChange={(e) => setMenuText(e.target.value)}
                  rows={6}
                  className="w-full border border-gray-200 rounded-lg px-4 py-3 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand"
                  placeholder="Paste your menu items here..."
                />
              </div>

              <div className="flex gap-4">
                <button
                  onClick={() => setStep(1)}
                  className="flex-1 bg-white hover:bg-gray-50 text-gray-700 border border-gray-200 font-medium px-4 py-2.5 rounded-lg transition-colors"
                >
                  Back
                </button>
                <button
                  onClick={handleExtractProducts}
                  disabled={!menuFile && !menuText.trim()}
                  className="flex-1 bg-brand hover:bg-brand-dark disabled:bg-gray-200 disabled:text-gray-400 text-white font-medium px-4 py-2.5 rounded-lg transition-colors flex items-center justify-center gap-2"
                >
                  {isExtracting ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Analyzing menu...
                    </>
                  ) : (
                    <>
                      Extract Products
                      <ArrowRight size={16} />
                    </>
                  )}
                </button>
              </div>
            </>
          )}

          {/* Step 3: Select Common Products */}
          {step === 3 && (
            <>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Select your regular products</h2>
              <p className="text-sm text-gray-500 mb-8">
                We found {products.length} products you might order regularly. Select the ones you want to add to your product list.
              </p>

              <div className="space-y-3 mb-8 max-h-96 overflow-y-auto">
                {products.map((product) => (
                  <div
                    key={product.id}
                    onClick={() => toggleProduct(product.id)}
                    className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                      selectedProducts.includes(product.id)
                        ? 'border-brand bg-brand-light'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <input
                            type="checkbox"
                            checked={selectedProducts.includes(product.id)}
                            onChange={() => toggleProduct(product.id)}
                            className="rounded border-gray-300 text-brand focus:ring-brand"
                            onClick={(e) => e.stopPropagation()}
                          />
                          <div>
                            <h3 className="font-semibold text-gray-900">{product.name}</h3>
                            <p className="text-xs text-gray-500">{product.category} · ~{product.estimatedMonthly} {product.unit}/month</p>
                          </div>
                        </div>
                      </div>
                      {selectedProducts.includes(product.id) && (
                        <Check className="text-brand" size={20} />
                      )}
                    </div>
                  </div>
                ))}
              </div>

              <div className="flex gap-4">
                <button
                  onClick={() => setStep(needsMenu ? 2 : 1)}
                  className="flex-1 bg-white hover:bg-gray-50 text-gray-700 border border-gray-200 font-medium px-4 py-2.5 rounded-lg transition-colors"
                >
                  Back
                </button>
                <button
                  onClick={() => setStep(4)}
                  disabled={selectedProducts.length === 0}
                  className="flex-1 bg-brand hover:bg-brand-dark disabled:bg-gray-200 disabled:text-gray-400 text-white font-medium px-4 py-2.5 rounded-lg transition-colors"
                >
                  Continue ({selectedProducts.length} selected)
                </button>
              </div>
            </>
          )}

          {/* Step 4: Complete */}
          {step === 4 && (
            <>
              <div className="text-center mb-8">
                <div className="w-16 h-16 bg-brand-light rounded-full flex items-center justify-center mx-auto mb-4">
                  <Check className="text-brand" size={32} />
                </div>
                <h1 className="text-2xl font-bold text-gray-900 mb-2">You're all set!</h1>
                <p className="text-sm text-gray-500">
                  We've added {selectedProducts.length} products to your list. You can now start placing orders.
                </p>
              </div>

              <div className="bg-gray-50 rounded-lg p-6 mb-6">
                <h3 className="font-semibold text-gray-900 mb-4">What's next?</h3>
                <ul className="space-y-2 text-sm text-gray-700">
                  <li className="flex items-start gap-2">
                    <Check className="text-brand mt-0.5" size={16} />
                    <span>Select products from your list to place an order</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="text-brand mt-0.5" size={16} />
                    <span>Our AI agents will negotiate the best prices for you</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="text-brand mt-0.5" size={16} />
                    <span>Approve and pay when you're ready</span>
                  </li>
                </ul>
              </div>

              <button
                onClick={handleComplete}
                className="w-full bg-brand hover:bg-brand-dark text-white font-medium px-4 py-2.5 rounded-lg transition-colors"
              >
                Start Ordering
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

