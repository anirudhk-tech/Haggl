import type { BusinessProfile, PreferenceWeights, Vendor, Order, Payment, Message } from "./types";

// Demo business profile
export const demoProfile: BusinessProfile = {
  business_id: "demo-bakery-001",
  business_name: "Demo Business",
  business_type: "bakery",
  location: {
    city: "San Francisco",
    state: "CA",
    zip_code: "94102",
  },
  phone: "+1-555-000-0000",
};

// Default preference weights
export const defaultWeights: PreferenceWeights = {
  quality: 0.30,
  affordability: 0.35,
  shipping: 0.15,
  reliability: 0.20,
};

// Demo vendors
export const demoVendors: Vendor[] = [
  {
    vendor_id: "v001",
    vendor_name: "Bay Area Foods Co",
    phone: "+1-415-555-0123",
    email: "orders@bayareafoods.com",
    website: "bayareafoods.com",
    address: "123 Market St, San Francisco, CA",
    distance_miles: 12.5,
    certifications: ["Organic", "FDA Certified"],
    products: ["Flour", "Sugar", "Baking Supplies"],
    scores: { quality: 92, affordability: 78, shipping: 85, reliability: 94 },
    embedding_score: 0.87,
    parameter_score: 0.82,
    final_score: 89.2,
    rank: 1,
  },
  {
    vendor_id: "v002",
    vendor_name: "Farm Fresh Eggs",
    phone: "+1-415-555-0456",
    email: "sales@farmfresheggs.com",
    website: "farmfresheggs.com",
    address: "456 Farm Rd, Petaluma, CA",
    distance_miles: 35.2,
    certifications: ["Cage-Free", "Organic"],
    products: ["Eggs", "Poultry"],
    scores: { quality: 96, affordability: 65, shipping: 72, reliability: 91 },
    embedding_score: 0.82,
    parameter_score: 0.78,
    final_score: 84.5,
    rank: 2,
  },
  {
    vendor_id: "v003",
    vendor_name: "Pacific Dairy Supply",
    phone: "+1-510-555-0789",
    email: "info@pacificdairy.com",
    website: "pacificdairy.com",
    address: "789 Industrial Blvd, Oakland, CA",
    distance_miles: 18.7,
    certifications: ["FDA Certified", "USDA Grade A"],
    products: ["Butter", "Cream", "Milk"],
    scores: { quality: 88, affordability: 82, shipping: 90, reliability: 87 },
    embedding_score: 0.79,
    parameter_score: 0.85,
    final_score: 86.8,
    rank: 3,
  },
  {
    vendor_id: "v004",
    vendor_name: "Golden State Grains",
    phone: "+1-650-555-0321",
    email: "orders@goldenstategrain.com",
    website: "goldenstategrain.com",
    address: "321 Grain Ave, South San Francisco, CA",
    distance_miles: 8.3,
    certifications: ["Non-GMO", "Kosher"],
    products: ["Flour", "Oats", "Rice"],
    scores: { quality: 85, affordability: 91, shipping: 95, reliability: 83 },
    embedding_score: 0.75,
    parameter_score: 0.88,
    final_score: 88.1,
    rank: 4,
  },
];

// Demo orders
export const demoOrders: Order[] = [
  {
    order_id: "HGL-2026-0192",
    created_at: "2026-01-10T14:30:00Z",
    status: "confirmed",
    ingredients: [
      { name: "Flour", quantity: 500, unit: "lbs", vendor_name: "Bay Area Foods Co", price_per_unit: 0.425, status: "confirmed" },
      { name: "Eggs", quantity: 1000, unit: "units", vendor_name: "Farm Fresh Eggs", price_per_unit: 0.50, status: "confirmed" },
    ],
    total_amount: 712.50,
    savings: 87.50,
    x402_tx_hash: "0x8f3e...a2c1",
    eta: "Jan 12, 2026",
  },
  {
    order_id: "HGL-2026-0191",
    created_at: "2026-01-08T10:15:00Z",
    status: "delivered",
    ingredients: [
      { name: "Butter", quantity: 100, unit: "lbs", vendor_name: "Pacific Dairy Supply", price_per_unit: 3.25, status: "confirmed" },
      { name: "Sugar", quantity: 200, unit: "lbs", vendor_name: "Bay Area Foods Co", price_per_unit: 0.35, status: "confirmed" },
    ],
    total_amount: 395.00,
    savings: 45.00,
    x402_tx_hash: "0x7c2d...b3f4",
    ach_confirmation: "ACH-78291",
  },
  {
    order_id: "HGL-2026-0190",
    created_at: "2026-01-05T09:00:00Z",
    status: "delivered",
    ingredients: [
      { name: "Vanilla Extract", quantity: 5, unit: "gallons", vendor_name: "Bay Area Foods Co", price_per_unit: 18.50, status: "confirmed" },
      { name: "Cocoa Powder", quantity: 25, unit: "lbs", vendor_name: "Bay Area Foods Co", price_per_unit: 1.39, status: "confirmed" },
    ],
    total_amount: 127.25,
    savings: 12.75,
    x402_tx_hash: "0x9a1b...c5e2",
    ach_confirmation: "ACH-78156",
  },
];

// Demo payments
export const demoPayments: Payment[] = [
  {
    invoice_id: "INV-2026-0192",
    date: "2026-01-10",
    vendor_name: "Bay Area Foods Co",
    amount_usd: 212.50,
    x402_tx_hash: "0x8f3e...a2c1",
    ach_confirmation: "ACH-78342",
    status: "executed",
  },
  {
    invoice_id: "INV-2026-0192-B",
    date: "2026-01-10",
    vendor_name: "Farm Fresh Eggs",
    amount_usd: 500.00,
    x402_tx_hash: "0x8f3e...a2c2",
    ach_confirmation: "ACH-78343",
    status: "executed",
  },
  {
    invoice_id: "INV-2026-0191",
    date: "2026-01-08",
    vendor_name: "Pacific Dairy Supply",
    amount_usd: 325.00,
    x402_tx_hash: "0x7c2d...b3f4",
    ach_confirmation: "ACH-78291",
    status: "executed",
  },
  {
    invoice_id: "INV-2026-0191-B",
    date: "2026-01-08",
    vendor_name: "Bay Area Foods Co",
    amount_usd: 70.00,
    x402_tx_hash: "0x7c2d...b3f5",
    ach_confirmation: "ACH-78292",
    status: "executed",
  },
];

// Demo messages
export const demoMessages: Message[] = [
  {
    id: "m1",
    role: "user",
    content: "Reorder flour",
    timestamp: "2026-01-10T14:34:00Z",
  },
  {
    id: "m2",
    role: "assistant",
    content: "Reorder 500 lbs all-purpose flour from Bay Area Foods @ $0.425/lb ($212.50 total)? Reply APPROVE or DENY",
    timestamp: "2026-01-10T14:34:05Z",
  },
  {
    id: "m3",
    role: "user",
    content: "APPROVE",
    timestamp: "2026-01-10T14:35:00Z",
  },
  {
    id: "m4",
    role: "assistant",
    content: "Order placed! x402 TX: 0x8f3e... ETA: Jan 12. Tracking: #HGL-2026-0192",
    timestamp: "2026-01-10T14:35:10Z",
  },
];

// Stats calculations
export const demoStats = {
  activeOrders: demoOrders.filter(o => ["sourcing", "calling", "confirmed", "payment_pending", "payment_processing"].includes(o.status)).length,
  monthlySavings: demoOrders.reduce((sum, o) => sum + (o.savings || 0), 0),
  pendingApprovals: 0,
  totalSpent: demoPayments.reduce((sum, p) => sum + p.amount_usd, 0),
};
