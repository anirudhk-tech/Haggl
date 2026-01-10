import type { BusinessProfile, PreferenceWeights, Vendor, Order, Payment, Message, VendorOrder, VendorMessage } from "./types";

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
    price_per_unit: 0.45,
    unit: "lb",
    min_order: 25,
    min_order_unit: "lbs",
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
    price_per_unit: 5.25,
    unit: "dozen",
    min_order: 10,
    min_order_unit: "dozen",
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
    price_per_unit: 3.25,
    unit: "lb",
    min_order: 20,
    min_order_unit: "lbs",
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
    price_per_unit: 0.38,
    unit: "lb",
    min_order: 50,
    min_order_unit: "lbs",
  },
];

// Mock vendor orders for correction dialog
export const demoVendorOrders: Record<string, VendorOrder[]> = {
  v001: [
    { order_id: "HGL-2026-0192", date: "2026-01-10", items: ["Flour"], quantity: "500 lbs", total: 212.50 },
    { order_id: "HGL-2026-0191", date: "2026-01-08", items: ["Sugar"], quantity: "200 lbs", total: 70.00 },
    { order_id: "HGL-2026-0190", date: "2026-01-05", items: ["Vanilla Extract", "Cocoa Powder"], quantity: "5 gal, 25 lbs", total: 127.25 },
  ],
  v002: [
    { order_id: "HGL-2026-0192", date: "2026-01-10", items: ["Eggs"], quantity: "1000 units", total: 500.00 },
    { order_id: "HGL-2026-0185", date: "2025-12-28", items: ["Eggs"], quantity: "500 units", total: 250.00 },
  ],
  v003: [
    { order_id: "HGL-2026-0191", date: "2026-01-08", items: ["Butter"], quantity: "100 lbs", total: 325.00 },
    { order_id: "HGL-2026-0180", date: "2025-12-20", items: ["Cream", "Milk"], quantity: "20 gal, 50 gal", total: 185.00 },
  ],
  v004: [
    { order_id: "HGL-2026-0175", date: "2025-12-15", items: ["Oats"], quantity: "100 lbs", total: 45.00 },
  ],
};

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

// Vendor messages (calls and SMS) with transcripts
export const demoVendorMessages: VendorMessage[] = [
  {
    id: "msg-001",
    vendor_id: "v001",
    vendor_name: "Bay Area Foods Co",
    type: "call",
    direction: "outbound",
    timestamp: "2026-01-10T10:30:00Z",
    duration: "4:32",
    content: "Discussed bulk flour pricing and confirmed delivery schedule for order #HGL-2026-0192",
    transcript: `Agent: Hi, this is Haggl AI calling on behalf of Demo Business. Am I speaking with Bay Area Foods Co?

Vendor: Yes, this is Maria from Bay Area Foods. How can I help you?

Agent: Great! I'm calling to discuss a flour order. We need 500 pounds of all-purpose flour. What's your current pricing?

Vendor: For 500 pounds, we can do $0.425 per pound. That's our bulk rate.

Agent: That sounds good. What's your earliest delivery date?

Vendor: We can have it to you by January 12th. We deliver to San Francisco on Tuesdays and Thursdays.

Agent: Perfect. I'll place the order now. Can you confirm the total would be $212.50?

Vendor: Yes, that's correct. We'll send an invoice shortly.

Agent: Thank you, Maria. Have a great day!

Vendor: You too! Thank you for the order.`,
  },
  {
    id: "msg-002",
    vendor_id: "v001",
    vendor_name: "Bay Area Foods Co",
    type: "sms",
    direction: "inbound",
    timestamp: "2026-01-10T14:22:00Z",
    content: "Order #HGL-2026-0192 confirmed and scheduled for delivery Jan 12. Tracking: BAF-78342",
  },
  {
    id: "msg-003",
    vendor_id: "v002",
    vendor_name: "Farm Fresh Eggs",
    type: "call",
    direction: "outbound",
    timestamp: "2026-01-10T11:15:00Z",
    duration: "3:18",
    content: "Negotiated egg pricing and confirmed organic certification for large order",
    transcript: `Agent: Hello, this is Haggl AI calling for Demo Business. Is this Farm Fresh Eggs?

Vendor: Yes, this is Tom speaking.

Agent: Hi Tom! We're looking to order 1000 eggs. I see you're cage-free and organic certified?

Vendor: That's right. All our eggs are certified organic and cage-free.

Agent: Excellent. What's your pricing for 1000 units?

Vendor: For that quantity, it's $0.50 per egg, so $500 total.

Agent: Do you offer any bulk discounts for regular orders?

Vendor: If you commit to weekly orders, we can do $0.45 per egg.

Agent: That's great to know. For now, we'll proceed with the single order at $500.

Vendor: Sounds good. When do you need them?

Agent: As soon as possible, ideally with the flour delivery on January 12th.

Vendor: We can do that. I'll coordinate with Bay Area Foods for combined delivery.

Agent: Perfect, thank you Tom!`,
  },
  {
    id: "msg-004",
    vendor_id: "v002",
    vendor_name: "Farm Fresh Eggs",
    type: "sms",
    direction: "outbound",
    timestamp: "2026-01-10T11:45:00Z",
    content: "Confirming order: 1000 organic eggs @ $0.50/ea = $500. Delivery: Jan 12. Please reply YES to confirm.",
  },
  {
    id: "msg-005",
    vendor_id: "v002",
    vendor_name: "Farm Fresh Eggs",
    type: "sms",
    direction: "inbound",
    timestamp: "2026-01-10T11:47:00Z",
    content: "YES - confirmed. Invoice sent to orders@demobusiness.com",
  },
  {
    id: "msg-006",
    vendor_id: "v003",
    vendor_name: "Pacific Dairy Supply",
    type: "call",
    direction: "outbound",
    timestamp: "2026-01-08T09:00:00Z",
    duration: "5:45",
    content: "Placed butter order and discussed cream availability for next month",
    transcript: `Agent: Good morning, this is Haggl AI calling for Demo Business. May I speak with someone about placing an order?

Vendor: Hi, this is Sarah from Pacific Dairy. What can I help you with?

Agent: We'd like to order 100 pounds of butter. What's your current pricing?

Vendor: For Grade A butter, it's $3.25 per pound.

Agent: That works for us. We're also interested in cream for next month. What's availability like?

Vendor: We have plenty of heavy cream. 40% butterfat, $4.50 per gallon. We recommend ordering a week in advance.

Agent: Good to know. Let's proceed with the butter order for now. Total would be $325?

Vendor: Correct. We can deliver by January 10th if you need it quickly.

Agent: That would be perfect. Please confirm the order.

Vendor: Order confirmed. You'll receive tracking information shortly.

Agent: Thank you, Sarah!`,
  },
  {
    id: "msg-007",
    vendor_id: "v003",
    vendor_name: "Pacific Dairy Supply",
    type: "sms",
    direction: "inbound",
    timestamp: "2026-01-08T15:30:00Z",
    content: "Butter order shipped! Tracking: PDS-91827. ETA: Jan 10, 8am-12pm. Refrigerated truck.",
  },
  {
    id: "msg-008",
    vendor_id: "v004",
    vendor_name: "Golden State Grains",
    type: "call",
    direction: "inbound",
    timestamp: "2026-01-09T14:00:00Z",
    duration: "2:10",
    content: "Vendor called to offer promotional pricing on bulk oats",
    transcript: `Vendor: Hi, this is Mike from Golden State Grains. Is this Demo Business?

Agent: Yes, this is Haggl AI assistant for Demo Business. How can I help you?

Vendor: I wanted to let you know we're running a promotion on bulk oats this month. 15% off orders over 100 pounds.

Agent: That's great to know. What would the pricing be?

Vendor: Normally $0.45 per pound, but with the discount it's $0.38 per pound.

Agent: Interesting. Let me check with the business owner and get back to you.

Vendor: Sure thing. The offer is valid through January 31st.

Agent: Thank you for reaching out, Mike. We'll be in touch.`,
  },
];

// Pending approvals for the approvals page
export const demoPendingApprovals: import("./types").PendingApproval[] = [
  {
    approval_id: "APR-001",
    created_at: "2026-01-10T16:00:00Z",
    ingredient: "Almond Flour",
    quantity: 50,
    unit: "lbs",
    vendor: {
      vendor_id: "v001",
      vendor_name: "Bay Area Foods Co",
      phone: "+1-415-555-0123",
      email: "orders@bayareafoods.com",
      certifications: ["Organic", "FDA Certified"],
      products: ["Flour", "Sugar", "Baking Supplies"],
      scores: { quality: 92, affordability: 78, shipping: 85, reliability: 94 },
      embedding_score: 0.87,
      parameter_score: 0.82,
      final_score: 89.2,
      rank: 1,
      price_per_unit: 4.50,
      unit: "lb",
      distance_miles: 12.5,
    },
    total_price: 225.00,
    has_invoice: true,
    invoice_url: "https://example.com/invoice/INV-2026-0195",
    alternatives: [
      {
        vendor_id: "v004",
        vendor_name: "Golden State Grains",
        phone: "+1-650-555-0321",
        certifications: ["Non-GMO", "Kosher"],
        products: ["Flour", "Oats", "Rice"],
        scores: { quality: 85, affordability: 91, shipping: 95, reliability: 83 },
        embedding_score: 0.75,
        parameter_score: 0.88,
        final_score: 88.1,
        rank: 2,
        price_per_unit: 4.25,
        unit: "lb",
        distance_miles: 8.3,
      },
    ],
  },
  {
    approval_id: "APR-002",
    created_at: "2026-01-10T15:30:00Z",
    ingredient: "Heavy Cream",
    quantity: 20,
    unit: "gallons",
    vendor: {
      vendor_id: "v003",
      vendor_name: "Pacific Dairy Supply",
      phone: "+1-510-555-0789",
      email: "info@pacificdairy.com",
      certifications: ["FDA Certified", "USDA Grade A"],
      products: ["Butter", "Cream", "Milk"],
      scores: { quality: 88, affordability: 82, shipping: 90, reliability: 87 },
      embedding_score: 0.79,
      parameter_score: 0.85,
      final_score: 86.8,
      rank: 1,
      price_per_unit: 4.50,
      unit: "gal",
      distance_miles: 18.7,
    },
    total_price: 90.00,
    has_invoice: false,
    alternatives: [],
  },
  {
    approval_id: "APR-003",
    created_at: "2026-01-10T14:00:00Z",
    ingredient: "Organic Eggs",
    quantity: 500,
    unit: "units",
    vendor: {
      vendor_id: "v002",
      vendor_name: "Farm Fresh Eggs",
      phone: "+1-415-555-0456",
      email: "sales@farmfresheggs.com",
      certifications: ["Cage-Free", "Organic"],
      products: ["Eggs", "Poultry"],
      scores: { quality: 96, affordability: 65, shipping: 72, reliability: 91 },
      embedding_score: 0.82,
      parameter_score: 0.78,
      final_score: 84.5,
      rank: 1,
      price_per_unit: 0.55,
      unit: "ea",
      distance_miles: 35.2,
    },
    total_price: 275.00,
    has_invoice: true,
    invoice_url: "https://example.com/invoice/INV-2026-0194",
    alternatives: [],
  },
];

// Wallet data
export const demoWallet: import("./types").Wallet = {
  balance: 2847.50,
  pending_balance: 590.00,
  currency: "USD",
  transactions: [
    {
      id: "txn-001",
      type: "deposit",
      amount: 5000.00,
      description: "Bank transfer deposit",
      timestamp: "2026-01-05T09:00:00Z",
      status: "completed",
      reference: "ACH-DEP-78001",
    },
    {
      id: "txn-002",
      type: "payment",
      amount: -712.50,
      description: "Order #HGL-2026-0192",
      timestamp: "2026-01-10T14:35:00Z",
      status: "completed",
      reference: "x402-0x8f3e...a2c1",
      vendor_name: "Bay Area Foods Co, Farm Fresh Eggs",
    },
    {
      id: "txn-003",
      type: "payment",
      amount: -395.00,
      description: "Order #HGL-2026-0191",
      timestamp: "2026-01-08T10:20:00Z",
      status: "completed",
      reference: "x402-0x7c2d...b3f4",
      vendor_name: "Pacific Dairy Supply, Bay Area Foods Co",
    },
    {
      id: "txn-004",
      type: "payment",
      amount: -127.25,
      description: "Order #HGL-2026-0190",
      timestamp: "2026-01-05T09:15:00Z",
      status: "completed",
      reference: "x402-0x9a1b...c5e2",
      vendor_name: "Bay Area Foods Co",
    },
    {
      id: "txn-005",
      type: "deposit",
      amount: 1000.00,
      description: "Card deposit",
      timestamp: "2026-01-01T12:00:00Z",
      status: "completed",
      reference: "CARD-DEP-77892",
    },
    {
      id: "txn-006",
      type: "payment",
      amount: -590.00,
      description: "Order #HGL-2026-0193 (pending)",
      timestamp: "2026-01-10T16:00:00Z",
      status: "pending",
      vendor_name: "Bay Area Foods Co",
    },
    {
      id: "txn-007",
      type: "refund",
      amount: 82.25,
      description: "Partial refund - damaged goods",
      timestamp: "2026-01-07T11:30:00Z",
      status: "completed",
      reference: "REF-78201",
      vendor_name: "Golden State Grains",
    },
  ],
};

// Business types for onboarding/new order
export const businessTypes = [
  { id: "restaurant" as const, label: "Restaurant", description: "Full-service or quick-service restaurant" },
  { id: "bakery" as const, label: "Bakery", description: "Bakery or pastry shop" },
  { id: "cafe" as const, label: "Cafe", description: "Coffee shop or cafe" },
  { id: "retail" as const, label: "Retail", description: "Retail or grocery store" },
  { id: "other" as const, label: "Other", description: "Other business type" },
];

// Extracted products by business type (simulates AI extraction from menu)
export const extractedProducts: Record<string, { id: number; name: string; category: string; unit: string; estimatedMonthly: number }[]> = {
  restaurant: [
    { id: 1, name: "All-Purpose Flour", category: "Dry Goods", unit: "lbs", estimatedMonthly: 200 },
    { id: 2, name: "Olive Oil", category: "Oils", unit: "gallons", estimatedMonthly: 10 },
    { id: 3, name: "Tomatoes", category: "Produce", unit: "lbs", estimatedMonthly: 150 },
    { id: 4, name: "Mozzarella Cheese", category: "Dairy", unit: "lbs", estimatedMonthly: 80 },
    { id: 5, name: "Ground Beef", category: "Meat", unit: "lbs", estimatedMonthly: 120 },
    { id: 6, name: "Pasta", category: "Dry Goods", unit: "lbs", estimatedMonthly: 100 },
  ],
  bakery: [
    { id: 1, name: "All-Purpose Flour", category: "Dry Goods", unit: "lbs", estimatedMonthly: 500 },
    { id: 2, name: "Butter", category: "Dairy", unit: "lbs", estimatedMonthly: 200 },
    { id: 3, name: "Sugar", category: "Dry Goods", unit: "lbs", estimatedMonthly: 300 },
    { id: 4, name: "Eggs", category: "Dairy", unit: "dozen", estimatedMonthly: 150 },
    { id: 5, name: "Vanilla Extract", category: "Flavorings", unit: "oz", estimatedMonthly: 20 },
    { id: 6, name: "Chocolate Chips", category: "Dry Goods", unit: "lbs", estimatedMonthly: 100 },
    { id: 7, name: "Baking Powder", category: "Dry Goods", unit: "lbs", estimatedMonthly: 25 },
    { id: 8, name: "Heavy Cream", category: "Dairy", unit: "gallons", estimatedMonthly: 30 },
  ],
  cafe: [
    { id: 1, name: "Coffee Beans", category: "Beverages", unit: "lbs", estimatedMonthly: 200 },
    { id: 2, name: "Milk", category: "Dairy", unit: "gallons", estimatedMonthly: 50 },
    { id: 3, name: "Syrups", category: "Flavorings", unit: "bottles", estimatedMonthly: 30 },
    { id: 4, name: "Paper Cups", category: "Supplies", unit: "cases", estimatedMonthly: 40 },
    { id: 5, name: "Tea Bags", category: "Beverages", unit: "boxes", estimatedMonthly: 25 },
  ],
  retail: [
    { id: 1, name: "Packaged Goods", category: "General", unit: "cases", estimatedMonthly: 500 },
    { id: 2, name: "Cleaning Supplies", category: "Supplies", unit: "cases", estimatedMonthly: 20 },
  ],
  other: [
    { id: 1, name: "General Supplies", category: "General", unit: "units", estimatedMonthly: 100 },
  ],
};

// Saved products (user's product list after onboarding)
export const savedProducts = [
  { id: 1, name: "All-Purpose Flour", category: "Dry Goods", unit: "lbs", typicalQuantity: 500 },
  { id: 2, name: "Butter", category: "Dairy", unit: "lbs", typicalQuantity: 100 },
  { id: 3, name: "Sugar", category: "Dry Goods", unit: "lbs", typicalQuantity: 200 },
  { id: 4, name: "Eggs", category: "Dairy", unit: "dozen", typicalQuantity: 100 },
  { id: 5, name: "Vanilla Extract", category: "Flavorings", unit: "oz", typicalQuantity: 15 },
  { id: 6, name: "Chocolate Chips", category: "Dry Goods", unit: "lbs", typicalQuantity: 50 },
  { id: 7, name: "Heavy Cream", category: "Dairy", unit: "gallons", typicalQuantity: 20 },
  { id: 8, name: "Cocoa Powder", category: "Dry Goods", unit: "lbs", typicalQuantity: 25 },
];
