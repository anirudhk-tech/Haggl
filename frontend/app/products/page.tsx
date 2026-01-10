'use client';

import { useState } from 'react';
import { Plus, Search, Edit2, Trash2 } from 'lucide-react';

// Mock saved products - in real app, this would come from API
const savedProducts = [
  { id: 1, name: 'All-Purpose Flour', category: 'Dry Goods', unit: 'lbs', typicalQuantity: 200, lastOrdered: 'Jan 5, 2026' },
  { id: 2, name: 'Butter', category: 'Dairy', unit: 'lbs', typicalQuantity: 100, lastOrdered: 'Jan 3, 2026' },
  { id: 3, name: 'Sugar', category: 'Dry Goods', unit: 'lbs', typicalQuantity: 150, lastOrdered: 'Jan 2, 2026' },
  { id: 4, name: 'Eggs', category: 'Dairy', unit: 'dozen', typicalQuantity: 50, lastOrdered: 'Jan 1, 2026' },
  { id: 5, name: 'Vanilla Extract', category: 'Flavorings', unit: 'oz', typicalQuantity: 10, lastOrdered: 'Dec 28, 2025' },
];

export default function Products() {
  const [products, setProducts] = useState(savedProducts);
  const [searchQuery, setSearchQuery] = useState('');

  const filteredProducts = products.filter(p =>
    p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="max-w-[1100px] mx-auto px-16 py-12">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">My Products</h1>
          <p className="text-sm text-gray-500 mt-1">Manage your regular order items</p>
        </div>
        <button className="bg-brand hover:bg-brand-dark text-white font-medium px-4 py-2.5 rounded-lg transition-colors flex items-center gap-2">
          <Plus size={18} />
          Add Product
        </button>
      </div>

      {/* Search */}
      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
        <input
          type="text"
          placeholder="Search products..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand"
        />
      </div>

      {/* Products List */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <div className="divide-y divide-gray-200">
          {filteredProducts.length > 0 ? (
            filteredProducts.map((product) => (
              <div key={product.id} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-semibold text-gray-900">{product.name}</h3>
                      <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded-full">
                        {product.category}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span>Typical: {product.typicalQuantity} {product.unit}</span>
                      <span>•</span>
                      <span>Last ordered: {product.lastOrdered}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
                      <Edit2 size={18} />
                    </button>
                    <button className="p-2 text-gray-400 hover:text-status-rose transition-colors">
                      <Trash2 size={18} />
                    </button>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="p-12 text-center">
              <p className="text-gray-500 mb-4">No products found</p>
              <button className="text-sm text-brand hover:text-brand-dark">
                Add your first product
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

