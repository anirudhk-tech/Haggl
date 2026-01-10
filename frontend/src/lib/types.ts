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

// Agent stages
export type AgentStage =
  | "idle"
  | "message_received"
  | "sourcing"
  | "calling"
  | "negotiating"
  | "evaluating"
  | "confirmed"
  | "approval_pending"
  | "approved"
  | "completed"
  | "failed";

// Event types
export type EventType =
  | "stage_change"
  | "log"
  | "vendor_update"
  | "call_update"
  | "evaluation_update"
  | "order_update"
  | "approval_required"
  | "system";

// Agent event from SSE
export interface AgentEvent {
  event_type: EventType;
  stage: AgentStage;
  order_id?: string;
  message: string;
  data: Record<string, unknown>;
  timestamp: string;
}

// Pending approval
export interface PendingApproval {
  order_id: string;
  vendor_name: string;
  price: number;
  product: string;
  quantity: number;
  unit: string;
  created_at?: string;
}
