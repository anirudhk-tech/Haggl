import { Search, Star } from 'lucide-react';

const suppliers = [
  { name: 'Bay Area Foods Co', location: 'San Francisco, CA', tags: ['Flour', 'Sugar'], rating: 8.5, lastRate: '$0.40/lb on Jan 5' },
  { name: 'Golden Gate Grains', location: 'Oakland, CA', tags: ['Flour', 'Grains'], rating: 8.2, lastRate: '$0.38/lb on Jan 3' },
  { name: 'Fresh Farms', location: 'Berkeley, CA', tags: ['Butter', 'Dairy'], rating: 7.8, lastRate: '$2.10/lb on Jan 4' },
  { name: 'Pacific Produce', location: 'San Jose, CA', tags: ['Fruits', 'Vegetables'], rating: 8.0, lastRate: '$1.20/lb on Jan 2' },
  { name: 'Coastal Seafood', location: 'Half Moon Bay, CA', tags: ['Seafood'], rating: 7.5, lastRate: '$8.50/lb on Jan 1' },
  { name: 'Mountain Spices', location: 'Santa Cruz, CA', tags: ['Spices', 'Herbs'], rating: 8.3, lastRate: '$12.00/lb on Dec 28' },
];

export default function Suppliers() {
  return (
    <div className="max-w-[1100px] mx-auto px-16 py-12">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Suppliers</h1>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
          <input
            type="text"
            placeholder="Search suppliers..."
            className="pl-10 pr-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand w-64"
          />
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {suppliers.map((supplier) => (
          <div key={supplier.name} className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="font-semibold text-gray-900 mb-1">{supplier.name}</h3>
            <p className="text-sm text-gray-500 mb-4">{supplier.location}</p>
            
            <div className="flex flex-wrap gap-2 mb-4">
              {supplier.tags.map((tag) => (
                <span key={tag} className="bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded-full">
                  {tag}
                </span>
              ))}
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1">
                <Star className="text-yellow-400 fill-yellow-400" size={16} />
                <span className="text-sm font-medium text-gray-900">{supplier.rating}</span>
              </div>
              <span className="text-xs text-gray-500">{supplier.lastRate}</span>
            </div>

            <button className="w-full mt-4 text-sm text-brand hover:text-brand-dark text-left">
              View details →
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

