// Demo business profile
export interface BusinessProfile {
  business_id: string;
  business_name: string;
  business_type: string;
  location: {
    city: string;
    state: string;
    zip_code: string;
  };
  phone: string;
}

// Preference weights for vendor evaluation
export interface PreferenceWeights {
  quality: number;
  affordability: number;
  shipping: number;
  reliability: number;
}

// Vendor scores
export interface VendorScores {
  quality: number;
  affordability: number;
  shipping: number;
  reliability: number;
}

// Vendor data
export interface Vendor {
  vendor_id: string;
  vendor_name: string;
  phone?: string;
  email?: string;
  website?: string;
  address?: string;
  distance_miles?: number;
  certifications: string[];
  products: string[];
  scores: VendorScores;
  embedding_score: number;
  parameter_score: number;
  final_score: number;
  rank: number;
  // Pricing info
  price_per_unit?: number;
  unit?: string;
  min_order?: number;
  min_order_unit?: string;
}

// Order status
export type OrderStatus =
  | "sourcing"
  | "calling"
  | "confirmed"
  | "payment_pending"
  | "payment_processing"
  | "paid"
  | "delivered"
  | "failed";

// Order ingredient
export interface OrderIngredient {
  name: string;
  quantity: number;
  unit: string;
  quality?: string;
  vendor_id?: string;
  vendor_name?: string;
  price_per_unit?: number;
  status?: "pending" | "confirmed" | "failed";
}

// Order
export interface Order {
  order_id: string;
  created_at: string;
  status: OrderStatus;
  ingredients: OrderIngredient[];
  total_amount: number;
  savings?: number;
  x402_tx_hash?: string;
  ach_confirmation?: string;
  eta?: string;
}

// Payment
export interface Payment {
  invoice_id: string;
  date: string;
  vendor_name: string;
  amount_usd: number;
  x402_tx_hash?: string;
  ach_confirmation?: string;
  status: "authorized" | "executed" | "failed";
}

// Message
export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

// Radar chart data point
export interface RadarDataPoint {
  parameter: string;
  value: number;
  fullMark: number;
}

// Vendor order history (for correction dialog)
export interface VendorOrder {
  order_id: string;
  date: string;
  items: string[];
  quantity: string;
  total: number;
}

// Correction request for online learning
export interface CorrectionRequest {
  vendor_id: string;
  parameter: "quality" | "affordability" | "shipping" | "reliability";
  direction: "up" | "down";
  current_prediction: number;
}

// Correction response from backend
export interface CorrectionResponse {
  status: string;
  parameter: string;
  direction: string;
  new_prediction: number;
}

// Vendor message (calls and SMS)
export interface VendorMessage {
  id: string;
  vendor_id: string;
  vendor_name: string;
  type: "call" | "sms";
  direction: "inbound" | "outbound";
  timestamp: string;
  duration?: string;
  content: string;
  transcript?: string;
}

// Extended vendor with pricing info
export interface VendorPricing {
  price_per_unit: number;
  unit: string;
  min_order?: number;
  min_order_unit?: string;
}

// Pending approval for an ingredient
export interface PendingApproval {
  approval_id: string;
  created_at: string;
  ingredient: string;
  quantity: number;
  unit: string;
  vendor: Vendor;
  total_price: number;
  has_invoice: boolean;
  invoice_url?: string;
  alternatives: Vendor[];
}

// Wallet transaction
export interface WalletTransaction {
  id: string;
  type: "deposit" | "payment" | "refund";
  amount: number;
  description: string;
  timestamp: string;
  status: "pending" | "completed" | "failed";
  reference?: string;
  vendor_name?: string;
}

// Wallet data
export interface Wallet {
  balance: number;
  pending_balance: number;
  currency: string;
  transactions: WalletTransaction[];
}
