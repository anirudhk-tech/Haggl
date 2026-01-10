# Haggl Frontend Overview

**Framework:** Next.js 14 + React + TailwindCSS + Shadcn/UI + Recharts
**Version:** 2.0
**Date:** January 10, 2026

---

## Architecture

Single-user application with no authentication. The app uses a hardcoded `business_id` for all API calls. All state persists server-side via the FastAPI backend.

**Tech Stack:**
- Next.js 14 App Router
- React Server Components where applicable
- TailwindCSS for styling
- Shadcn/UI component library
- Recharts for radar chart visualizations
- React Query for data fetching and caching

---

## Page Structure

```
/                     → Dashboard (home)
/order/new            → New Order flow
/order/[id]           → Order details & tracking
/vendors              → Vendor directory with evaluation
/vendors/[id]         → Individual vendor profile
/payments             → Payment history with x402 transactions
/messages             → SMS conversation history
/settings             → Preferences and budget configuration
```

---

## User Flow

### Flow 1: First-Time Order

1. User lands on Dashboard
2. Taps "New Order" button
3. Chooses input method: Manual Entry, CSV Upload, or Menu Upload
4. Enters ingredients with quantity, unit, and quality tier
5. Sets budget limit
6. Taps "Find Vendors" - Sourcing Agent searches for suppliers
7. Views ranked vendor list with radar charts showing scores
8. Adjusts preferences using UP/DOWN buttons on each parameter
9. Selects vendors (auto-selected within budget, can override)
10. Taps "Place Order" - Calling Agent phones vendors
11. Views real-time call status and transcripts
12. Order confirmed - x402 authorizes payment
13. Payment Agent executes ACH transfer
14. User receives confirmation with tracking number

### Flow 2: Quick Reorder

1. User lands on Dashboard
2. Views recent orders in the order list
3. Taps "Reorder" on any past order
4. System pre-fills ingredients with preferred vendors from last order
5. User confirms or modifies quantities
6. Taps "Place Order" - skips sourcing for preferred vendors
7. Order completes with minimal interaction

### Flow 3: SMS Ordering

1. User texts Haggl number: "Order 500 lbs flour"
2. Haggl responds with vendor recommendation and price
3. User replies "APPROVE" or "DENY"
4. Order placed, confirmation sent via SMS
5. User can view full conversation in Messages page

### Flow 4: Preference Learning

1. User views vendor evaluation results
2. Each vendor card shows radar chart with 4 parameters
3. User taps UP arrow next to "Quality" - weight increases 5%
4. User taps DOWN arrow next to "Affordability" - weight decreases 5%
5. Vendors re-rank in real-time based on new weights
6. Preferences persist across all future searches
7. System learns user priorities over time

---

## Page Descriptions

### Dashboard (/)

The main landing page showing procurement overview at a glance.

**Header Section:**
- Haggl logo (left)
- Search bar for orders/vendors/ingredients (center)
- Settings icon (right)

**Stats Row:**
Three stat cards displayed horizontally on desktop, stacked on mobile:
- Active Orders: Count of in-progress orders with status indicator
- Monthly Savings: Dollar amount saved compared to market average
- Pending Approvals: Count of orders awaiting user confirmation, with quick-action button

**Recent Orders Section:**
List of recent orders showing:
- Order ID
- Ingredients summary (first 2-3 items + "and X more")
- Total amount
- Status badge (Sourcing, Calling, Confirmed, Delivered, Failed)
- Action buttons: View Details, Reorder

**Quick Actions:**
Floating action button (mobile) or prominent button row (desktop):
- New Order (primary)
- Reorder Last
- Check Messages

---

### New Order (/order/new)

Multi-step order creation flow.

**Step 1: Input Method**
Three option cards:
- Manual Entry: Add ingredients one by one
- CSV Upload: Drag-drop or browse for spreadsheet
- Menu Upload: Upload PDF/image of menu for AI extraction (future)

**Step 2: Ingredients (Manual Entry)**
Form with repeating ingredient rows:
- Ingredient name (text input with autocomplete from past orders)
- Quantity (number input)
- Unit (dropdown: lbs, kg, dozen, units, cases)
- Quality tier (dropdown: Standard, Premium, Organic, Custom)
- Preferred Vendor toggle: If user has ordered this ingredient before, shows last vendor with price. Toggle ON to use preferred vendor, OFF to let Haggl find best price.
- Remove button (X icon)

Add Ingredient button at bottom of list.

**Step 2: Ingredients (CSV Upload)**
- Drag-drop zone for file upload
- Supported formats: .csv, .xlsx
- Required columns: ingredient, quantity
- Optional columns: unit, quality, priority
- Preview table showing parsed data with validation status
- Error highlighting for invalid rows
- Import button to confirm

**Step 3: Budget & Preferences**
- Budget input (dollar amount)
- Current preference weights display (Quality, Affordability, Shipping, Reliability percentages)
- Link to adjust preferences in Settings
- Location confirmation (city, state for shipping estimates)

**Step 4: Review & Submit**
- Summary of all ingredients
- Estimated total based on preferred vendors or market prices
- Submit button: "Find Vendors" or "Place Order" (if all preferred vendors selected)

---

### Order Details (/order/[id])

Real-time order tracking and details.

**Order Header:**
- Order ID
- Created timestamp
- Overall status badge
- Total amount

**Progress Timeline:**
Vertical timeline showing order stages:
1. Order Created (timestamp)
2. Sourcing Vendors (timestamp, vendor count found)
3. Calling Vendors (timestamp, call status per vendor)
4. Order Confirmed (timestamp, confirmed prices)
5. Payment Authorized (timestamp, x402 tx hash link)
6. Payment Executed (timestamp, confirmation number)
7. Delivery Expected (ETA)

**Ingredients Breakdown:**
List of each ingredient with:
- Ingredient name and quantity
- Assigned vendor name
- Negotiated price vs. original price (savings highlighted)
- Vendor status (Confirmed, Pending, Failed)

**Call Transcripts:**
Expandable section showing:
- Vendor name
- Call duration
- Full transcript text
- Outcome: Confirmed/Not Confirmed with negotiated terms

**Payment Details:**
- x402 authorization status
- Transaction hash (links to BaseScan block explorer)
- ACH confirmation number
- Receipt download link

---

### Vendors (/vendors)

Vendor directory with evaluation and preference learning.

**Filter Bar:**
- Search by vendor name
- Filter by ingredient category
- Filter by certification (Organic, FDA, etc.)
- Sort by: Final Score, Quality, Price, Distance

**Vendor Grid/List:**
Each vendor card displays:
- Vendor name
- Primary products
- Overall score (0-100)
- Distance from user location
- Certifications badges

Tap card to expand or navigate to full profile.

**Evaluation Controls (visible when vendors are being compared):**
Global preference adjustment panel:
- Quality: current weight % with UP/DOWN buttons
- Affordability: current weight % with UP/DOWN buttons
- Shipping: current weight % with UP/DOWN buttons
- Reliability: current weight % with UP/DOWN buttons
- Reset to Defaults button

When user taps UP/DOWN, vendors re-sort in real-time.

---

### Vendor Profile (/vendors/[id])

Detailed view of a single vendor with interactive scoring.

**Vendor Header:**
- Vendor name
- Contact info (phone, email, website)
- Address with distance
- Certifications list

**Radar Chart:**
Large Recharts radar visualization showing 4 parameters:
- Quality (0-100)
- Affordability (0-100)
- Shipping (0-100)
- Reliability (0-100)

Chart fills based on vendor's scores with preference-weighted final score displayed.

**Parameter Breakdown:**
Four rows, one per parameter:
- Parameter name
- Score value (0-100)
- UP button (increases weight by 5%)
- DOWN button (decreases weight by 5%)
- Current weight percentage

Tapping UP/DOWN updates weights via API, radar chart animates to new shape, final score recalculates.

**Score Summary:**
- Embedding Score (from Voyage AI model)
- Parameter Score (from explicit metrics)
- Final Score (30% embedding + 70% parameter, weighted by preferences)
- Rank among all vendors

**Order History with Vendor:**
List of past orders placed with this vendor:
- Order date
- Ingredients ordered
- Quantity and price
- Order status

**Actions:**
- Set as Preferred Vendor (for specific ingredients)
- Contact Vendor
- Place New Order with Vendor

---

### Payments (/payments)

Payment history with x402 blockchain verification.

**Summary Stats:**
- Total spent this month
- Total spent all time
- Average order value
- Budget remaining

**Transaction List:**
Table/list with columns:
- Date
- Vendor name
- Amount (USD)
- x402 TX hash (truncated, clickable link to BaseScan)
- ACH confirmation number
- Status badge (Authorized, Executed, Failed)

Clicking a row expands to show:
- Full transaction details
- Invoice breakdown
- Payment method used
- Timestamps for authorization and execution
- Receipt download

**Budget Management:**
- Current budget limit display
- Edit budget button
- Spending alerts configuration

---

### Messages (/messages)

SMS conversation history with Haggl bot.

**Conversation View:**
Chat-style interface showing:
- User messages (right-aligned, colored background)
- Haggl responses (left-aligned, neutral background)
- Timestamps on each message
- Links within messages are tappable (order IDs, tracking numbers)

**Message Types:**
- Order requests: "Reorder flour"
- Confirmations: "APPROVE" / "DENY"
- Status queries: "Status of order #123"
- Budget checks: "What's my remaining budget?"

**Quick Actions:**
- Copy Haggl phone number
- Send test message
- Clear conversation history

---

### Settings (/settings)

User preferences and configuration.

**Business Profile:**
- Business name (editable)
- Business type (bakery, restaurant, cafe, etc.)
- Location (city, state, zip)
- Phone number for SMS

**Preference Weights:**
Visual display of current weights with sliders or UP/DOWN controls:
- Quality: slider 5-60%
- Affordability: slider 5-60%
- Shipping: slider 5-60%
- Reliability: slider 5-60%

Weights always normalize to 100%. Changing one automatically adjusts others.

Reset to Defaults button.

Feedback count display: "Based on X preference adjustments"

**Budget Settings:**
- Default order budget
- Monthly spending limit
- Alert threshold percentage

**Notification Preferences:**
- SMS notifications toggle
- Order status updates toggle
- Payment confirmations toggle

**Data Management:**
- Export order history (CSV)
- Clear preference learning data
- Reset all settings

---

## Responsive Design

### Desktop (>1024px)
- Side navigation rail on left
- Full dashboard with multi-column layouts
- Vendor cards in grid (3-4 per row)
- Radar charts at full size
- Tables with all columns visible

### Tablet (768-1024px)
- Collapsible side navigation (hamburger menu)
- Two-column layouts where applicable
- Vendor cards in grid (2 per row)
- Radar charts at medium size
- Tables with horizontal scroll for overflow

### Mobile (<768px)
- Bottom navigation bar with 5 icons: Home, Orders, Vendors, Payments, Messages
- Single-column layouts throughout
- Vendor cards as full-width list items
- Radar charts at compact size with tap-to-expand
- Tables converted to card-based lists
- Floating action button for New Order
- Pull-to-refresh on all list views

---

## Component Library

Built with Shadcn/UI components:

**Layout:**
- Card: Container for stats, vendor info, orders
- Sheet: Mobile-friendly slide-out panels
- Tabs: Section navigation within pages
- Separator: Visual dividers

**Forms:**
- Input: Text entry
- Select: Dropdowns for unit, quality
- Button: Primary, secondary, ghost variants
- Toggle: Preferred vendor switches
- Slider: Preference weight adjustment

**Data Display:**
- Table: Payment history, order lists
- Badge: Status indicators
- Progress: Order timeline
- Avatar: Vendor icons

**Feedback:**
- Toast: Success/error notifications
- Alert: Important messages
- Skeleton: Loading states

**Custom Components:**
- RadarChart: Recharts-based 4-axis vendor scoring
- PreferenceControl: UP/DOWN buttons with weight display
- OrderTimeline: Vertical progress indicator
- VendorCard: Compact vendor summary with scores

---

## API Integration

All API calls go to the FastAPI backend at `/api` (proxied via Next.js rewrites).

**Key Endpoints Used:**

```typescript
// Sourcing
POST /sourcing/search
GET /sourcing/results/{ingredient}
GET /sourcing/status

// Evaluation (Preference Learning)
POST /evaluation/vendors
POST /evaluation/feedback
GET /evaluation/preferences/{business_id}
GET /evaluation/radar/{business_id}/{vendor_id}
POST /evaluation/reset/{business_id}

// Calling
POST /calling/order
GET /calling/status/{order_id}

// Payments (x402)
POST /x402/authorize
POST /x402/pay
GET /x402/status/{invoice_id}
GET /x402/spending
GET /x402/wallet

// Messages
GET /messaging/history/{phone_number}

// Health
GET /health
```

**Data Fetching Pattern:**
- React Query for caching and background refetching
- Optimistic updates for preference feedback
- Polling for order status during active orders
- Server-sent events (future) for real-time updates

---

## State Management

Minimal client-side state using React Query + URL state:

**React Query Keys:**
- `['vendors', businessId]` - Vendor evaluation results
- `['preferences', businessId]` - Current preference weights
- `['orders']` - Order list
- `['order', orderId]` - Single order details
- `['payments']` - Payment history
- `['messages', phoneNumber]` - SMS history

**URL State:**
- Filter/sort parameters in query string
- Active tab/step in pathname
- Modal states via query params

**No Global State Store Required:**
- Single user means no auth state
- Preferences fetched from server
- Order flow state managed by URL/React Query

---

## Preference Learning UX

The core differentiator of Haggl is the preference learning system. Here's how it works from a user perspective:

**Initial State:**
All users start with default weights:
- Quality: 30%
- Affordability: 35%
- Shipping: 15%
- Reliability: 20%

**Learning Interaction:**
1. User views vendor evaluation (grid or individual profile)
2. Each parameter shows current score and weight
3. UP button: Increases that parameter's importance by 5%
4. DOWN button: Decreases that parameter's importance by 5%
5. Other weights automatically rebalance (normalized to 100%)
6. Minimum weight: 5%, Maximum weight: 60%

**Visual Feedback:**
- Radar chart animates to reflect new weights
- Vendor rankings re-sort in real-time
- Toast notification confirms: "Quality preference increased to 35%"
- Final scores update immediately

**Persistence:**
- Every click sends `POST /evaluation/feedback`
- Server stores preference history per business_id
- Learned weights apply to all future vendor searches
- User can reset to defaults anytime in Settings

**Learning Model:**
The backend uses Voyage AI embeddings trained on 1000 examples. The final vendor score combines:
- 30% learned preference similarity (from embedding model)
- 70% explicit parameter scores (quality, price, distance, reliability)

Both components are weighted by user preferences, creating a personalized ranking that improves with each interaction.

---

## Design Tokens

**Colors:**
- Primary: #2563EB (Blue) - CTAs, active states
- Success: #10B981 (Green) - Confirmations, savings
- Warning: #F59E0B (Yellow) - Pending, caution
- Error: #EF4444 (Red) - Failures, alerts
- Background: #F9FAFB (Light Gray)
- Surface: #FFFFFF (White)
- Text Primary: #111827 (Dark Gray)
- Text Secondary: #6B7280 (Medium Gray)
- Border: #E5E7EB (Light Border)

**Typography:**
- Font Family: Inter (system fallback: -apple-system, sans-serif)
- H1: 24px / 600 weight
- H2: 20px / 600 weight
- H3: 16px / 600 weight
- Body: 14px / 400 weight
- Body Small: 12px / 400 weight
- Button: 14px / 500 weight

**Spacing:**
- Base unit: 4px
- Component padding: 16px
- Section gap: 24px
- Card border radius: 8px
- Button border radius: 6px

**Shadows:**
- Card: 0 1px 3px rgba(0,0,0,0.1)
- Dropdown: 0 4px 6px rgba(0,0,0,0.1)
- Modal: 0 10px 25px rgba(0,0,0,0.15)

---

## Implementation Phases

### Phase 1: Core Flow
1. Dashboard with stats and order list
2. New Order form with manual entry
3. Vendor evaluation with radar charts
4. Preference learning (UP/DOWN controls)
5. Order details with status timeline

### Phase 2: Enhanced Input
1. CSV import functionality
2. Preferred vendor auto-fill
3. Quick reorder from past orders

### Phase 3: Payments & Messaging
1. Payment history with x402 links
2. SMS conversation view
3. Real-time order status updates

### Phase 4: Polish
1. Mobile-optimized experience
2. Animations and transitions
3. Error handling and empty states
4. Performance optimization

---

**Document Status:** Ready for Implementation
