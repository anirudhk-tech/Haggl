# Haggl — UI Specification (Final)

---

## Tech Stack

- **Framework:** Next.js 14 (App Router)
- **Styling:** Tailwind CSS
- **Components:** shadcn/ui as base (customize to match spec)
- **Icons:** Lucide React
- **Font:** Inter (import from Google Fonts)
- **Charts (if needed):** Recharts

---

## File Structure

```
/app
  /dashboard
    page.tsx
  /orders
    page.tsx
    /[id]
      page.tsx
  /new-order
    page.tsx
  /suppliers
    page.tsx
  /wallet
    page.tsx
  /inbox
    page.tsx
  /settings
    page.tsx
  layout.tsx
  page.tsx (redirect to /dashboard)

/components
  /ui (shadcn components)
  NavBar.tsx
  AgentActivityPanel.tsx
  OrderCard.tsx
  StatusBadge.tsx
  StatCard.tsx
  VendorCard.tsx
  TranscriptViewer.tsx
  ProgressPhase.tsx
```

---

## Build Order

Build in this sequence:

1. **Layout + NavBar** — Get navigation working first
2. **Dashboard** — Stats + Agent Activity Panel + Recent Orders table
3. **New Order** — 3-step flow (Upload → Review → Confirm)
4. **Order Detail** — Progress phases with live states
5. **Orders List** — Simple table page
6. **Wallet** — Balance card + transaction history
7. **Inbox** — Two-panel layout with transcript viewer
8. **Suppliers** — Card grid
9. **Settings** — Form sections

---

## Overview

**Product:** Haggl — The AI buyer for small businesses.

**Platform:** Web-based B2B procurement dashboard. Desktop only, 1440px fixed width.

**Design philosophy:** Clean, minimal, lots of whitespace. Content breathes. Colors pop on key actions and states. Feels like a YC-backed product — Linear, Raycast, Mercury energy.

---

## Brand & Visual Identity

### Logo
- **Symbol:** Multiple lines converging into a downward chevron (options funneling to the best deal)
- **Wordmark:** "Haggl" — clean geometric sans-serif, medium weight
- **Color:** Symbol in `#22C55E`, wordmark in `#111827`

### Color Palette

**Add to tailwind.config.js:**

```js
colors: {
  brand: {
    DEFAULT: '#22C55E',
    dark: '#16A34A',
    light: '#DCFCE7',
  },
  status: {
    blue: '#3B82F6',
    'blue-light': '#DBEAFE',
    orange: '#F97316',
    'orange-light': '#FFEDD5',
    yellow: '#FACC15',
    'yellow-light': '#FEF9C3',
    rose: '#F43F5E',
    'rose-light': '#FFE4E6',
    purple: '#8B5CF6',
    'purple-light': '#EDE9FE',
  }
}
```

**Primary:**
| Name | Hex | Tailwind | Usage |
|------|-----|----------|-------|
| Green | `#22C55E` | `bg-brand` | Primary buttons, success states, active indicators, key accents |
| Green Dark | `#16A34A` | `bg-brand-dark` | Primary button hover |
| Green Light | `#DCFCE7` | `bg-brand-light` | Success badge backgrounds, selected row highlights |

**Semantic:**
| Name | Hex | Tailwind | Usage |
|------|-----|----------|-------|
| Blue | `#3B82F6` | `bg-status-blue` | In Progress states (Sourcing, Processing) |
| Blue Light | `#DBEAFE` | `bg-status-blue-light` | In Progress badge backgrounds |
| Orange | `#F97316` | `bg-status-orange` | Negotiating, Live calls, active agent work |
| Orange Light | `#FFEDD5` | `bg-status-orange-light` | Negotiating badge backgrounds |
| Yellow | `#FACC15` | `bg-status-yellow` | Warning, Awaiting Approval, needs attention |
| Yellow Light | `#FEF9C3` | `bg-status-yellow-light` | Warning badge backgrounds |
| Rose | `#F43F5E` | `bg-status-rose` | Error, Failed, Rejected, danger actions |
| Rose Light | `#FFE4E6` | `bg-status-rose-light` | Error badge backgrounds |
| Purple | `#8B5CF6` | `bg-status-purple` | Payment processing |
| Purple Light | `#EDE9FE` | `bg-status-purple-light` | Payment badge backgrounds |

**Neutrals (use Tailwind defaults):**
| Name | Hex | Tailwind |
|------|-----|----------|
| White | `#FFFFFF` | `bg-white` |
| Gray 50 | `#F9FAFB` | `bg-gray-50` |
| Gray 100 | `#F3F4F6` | `bg-gray-100` |
| Gray 200 | `#E5E7EB` | `bg-gray-200` / `border-gray-200` |
| Gray 400 | `#9CA3AF` | `text-gray-400` |
| Gray 500 | `#6B7280` | `text-gray-500` |
| Gray 900 | `#111827` | `text-gray-900` |

### Typography

**Font:** Inter (import from Google Fonts)

```css
/* Add to globals.css */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
```

| Element | Tailwind Classes |
|---------|------------------|
| Page headline | `text-2xl font-bold text-gray-900` (28px) |
| Section headline | `text-xl font-semibold text-gray-900` (20px) |
| Card title | `text-base font-semibold text-gray-900` (16px) |
| Body | `text-base font-normal text-gray-900` (16px) |
| Secondary/muted | `text-sm text-gray-500` (14px) |
| Small/caption | `text-xs text-gray-500` (12px) |
| Monospace | `font-mono text-sm font-medium text-gray-900` (14px) |

### Spacing

Use Tailwind defaults:
- `p-6` (24px) — Card padding
- `gap-12` (48px) — Section gaps
- `px-16` (64px) — Page horizontal padding
- `gap-4` (16px) — Between elements
- `gap-8` (32px) — Between cards

### Border Radius

- Buttons: `rounded-lg` (8px)
- Inputs: `rounded-lg` (8px)
- Cards: `rounded-xl` (12px)
- Badges: `rounded-full` (pill)

### Shadows

- Cards: `shadow-sm`
- Elevated (modals, dropdowns): `shadow-lg`

---

## Navigation

**Top Nav Bar:**
- Height: 64px (`h-16`)
- Background: `#FFFFFF` (`bg-white`)
- Border bottom: 1px `#E5E7EB` (`border-b border-gray-200`)
- Sticky at top (`sticky top-0 z-50`)

**Layout:**
- **Left:** Logo (symbol + "Haggl"), links to Dashboard
- **Right:** Nav links in a row — "Dashboard" · "New Order" · "Orders" · "Suppliers" · "Wallet" · "Inbox"
- **Far right:** User avatar (32px circle) with dropdown (Profile, Settings, Logout)

**Nav link style:**
- 14px, weight 500
- Default: `#6B7280` (`text-gray-500`)
- Hover: `#111827` (`hover:text-gray-900`)
- Active: `#22C55E` with subtle underline (`text-brand border-b-2 border-brand`)

**NavBar Component:**
```tsx
// components/NavBar.tsx
import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navLinks = [
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/new-order', label: 'New Order' },
  { href: '/orders', label: 'Orders' },
  { href: '/suppliers', label: 'Suppliers' },
  { href: '/wallet', label: 'Wallet' },
  { href: '/inbox', label: 'Inbox' },
];

export function NavBar() {
  const pathname = usePathname();
  
  return (
    <nav className="sticky top-0 z-50 bg-white border-b border-gray-200 h-16">
      <div className="max-w-[1440px] mx-auto px-16 h-full flex items-center justify-between">
        {/* Logo */}
        <Link href="/dashboard" className="flex items-center gap-2">
          <div className="w-8 h-8 bg-brand rounded-lg" /> {/* Logo placeholder */}
          <span className="text-xl font-semibold text-gray-900">Haggl</span>
        </Link>
        
        {/* Nav Links */}
        <div className="flex items-center gap-8">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`text-sm font-medium transition-colors ${
                pathname === link.href
                  ? 'text-brand border-b-2 border-brand pb-1'
                  : 'text-gray-500 hover:text-gray-900'
              }`}
            >
              {link.label}
            </Link>
          ))}
        </div>
        
        {/* User Avatar */}
        <div className="w-8 h-8 bg-gray-200 rounded-full" />
      </div>
    </nav>
  );
}
```

**Nav is visible on all screens.**

---

## Page Structure

All pages:
- White background (`#FFFFFF`)
- Max content width: 1100px, centered
- Generous whitespace — sections separated by 48px
- No clutter — only essential elements visible

---

## Screen 1: Dashboard

### Header
- **Headline:** "Welcome back" (28px, bold)
- No subhead — keep it minimal

### Stats Row (4 cards, horizontal, equal width)

Cards have:
- White background, subtle shadow
- 24px padding
- 12px border radius

| Card | Content |
|------|---------|
| **Wallet** | Label: "Balance" (12px, muted) · Value: "$2,500.00" (24px, bold, monospace) · Small "Add Funds" text link below |
| **Active** | Label: "Active Orders" · Value: "3" (24px, bold) · "View all →" text link |
| **Saved** | Label: "Saved This Month" · Value: "$1,240" (24px, bold, `#22C55E`) · "↓ 14% vs manual" small text |
| **Suppliers** | Label: "Suppliers" · Value: "28" (24px, bold) |

### Agent Activity Panel (Hero Section)

**This is prominent — the main visual on the dashboard.**

Card:
- Full width of content area
- White background, subtle shadow
- 32px padding (`p-8`)

**Header row:**
- Left: "Agent Activity" (20px, semibold)
- Right: Status indicator — green pulsing dot + "Active" when agents working, gray dot + "Idle" when not

**4 Agent Rows (vertical stack, 16px gap):**

Each row:
- Height: 56px
- Background: `#F9FAFB` (`bg-gray-50`)
- Border radius: 8px (`rounded-lg`)
- Padding: 16px (`p-4`)
- Layout: Icon (left) · Agent name (bold) · Status text (right-aligned)

| Agent | Icon | Idle | Active | Complete |
|-------|------|------|--------|----------|
| Sourcing | 🔍 | "Idle" (gray) | "Searching for flour suppliers..." (blue text, blue left border) | "Found 12 suppliers ✓" (green) |
| Negotiation | 📞 | "Idle" (gray) | "Calling Bay Area Foods... 1:23" (orange text, orange left border, pulsing) | "15% discount secured ✓" (green) |
| Evaluation | 📊 | "Idle" (gray) | "Scoring 8 suppliers..." (blue) | "Best vendor selected ✓" (green) |
| Payment | 💳 | "Idle" (gray) | "Processing $842.50..." (purple) | "Paid ✓ 0xA3F..." (green, hash truncated) |

**When Negotiation agent is calling:**
- Row has orange left border (4px)
- Animated phone icon or pulsing dot
- Elapsed time counter

**AgentActivityPanel Component:**
```tsx
// components/AgentActivityPanel.tsx
type AgentStatus = 'idle' | 'active' | 'complete';

interface Agent {
  name: string;
  icon: string;
  status: AgentStatus;
  message: string;
}

const statusStyles = {
  idle: 'text-gray-500',
  active: 'text-status-blue',
  complete: 'text-brand',
};

const borderStyles = {
  idle: 'border-l-4 border-transparent',
  active: 'border-l-4 border-status-blue',
  complete: 'border-l-4 border-brand',
};

// For negotiation agent specifically when calling
const negotiatingStyles = 'border-l-4 border-status-orange text-status-orange';

export function AgentActivityPanel({ agents }: { agents: Agent[] }) {
  const isAnyActive = agents.some(a => a.status === 'active');
  
  return (
    <div className="bg-white rounded-xl shadow-sm p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Agent Activity</h2>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${isAnyActive ? 'bg-brand animate-pulse' : 'bg-gray-400'}`} />
          <span className="text-sm text-gray-500">{isAnyActive ? 'Active' : 'Idle'}</span>
        </div>
      </div>
      
      {/* Agent Rows */}
      <div className="flex flex-col gap-4">
        {agents.map((agent) => (
          <div
            key={agent.name}
            className={`bg-gray-50 rounded-lg p-4 flex items-center justify-between ${borderStyles[agent.status]}`}
          >
            <div className="flex items-center gap-3">
              <span className="text-xl">{agent.icon}</span>
              <span className="font-medium text-gray-900">{agent.name}</span>
            </div>
            <span className={`text-sm ${statusStyles[agent.status]}`}>
              {agent.message}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
```

### Recent Orders

**Section header:**
- "Recent Orders" (20px, semibold) — left
- "View all →" text link — right

**Table:**
- Clean, minimal rows
- No heavy borders — just bottom border `#E5E7EB` between rows
- Row hover: `#F9FAFB` background

| Column | Style |
|--------|-------|
| Order ID | Monospace, `#111827` |
| Items | "8 items" — regular |
| Status | Badge (pill) |
| Total | Monospace, right-aligned |
| Date | Muted text |

**Status badges:**
| Status | Background | Text |
|--------|------------|------|
| Sourcing | `#DBEAFE` | `#3B82F6` |
| Negotiating | `#FFEDD5` | `#F97316` |
| Awaiting Approval | `#FEF9C3` | `#FACC15` |
| Paying | `#EDE9FE` | `#8B5CF6` |
| Complete | `#DCFCE7` | `#22C55E` |
| Failed | `#FFE4E6` | `#F43F5E` |

**Empty state:**
- Centered: "No orders yet" (muted) + "Create your first order" button (primary)

---

## Screen 2: New Order

### Page Header
- **Headline:** "New Order" (28px, bold)

### Step Indicator (horizontal)
- 3 steps: "Upload" · "Review" · "Confirm"
- Current step: `#22C55E` text + dot
- Future steps: `#9CA3AF` text
- Completed steps: `#22C55E` checkmark

---

### Step 1: Upload

**Centered card, max-width 600px**

**Headline:** "Upload your menu or ingredients" (20px, semibold)
**Subhead:** "We'll figure out what you need." (14px, muted)

**Upload zone:**
- Dashed border (`#E5E7EB`), 2px
- Border radius: 12px
- Padding: 48px
- Center: Upload icon + "Drop a file here or browse"
- Accepted: PDF, PNG, JPG, CSV, TXT
- On hover/drag: border becomes `#22C55E`

**Or divider:** "— or —" with lines

**Text input alternative:**
- "Paste your menu or ingredients" label
- Textarea, 4 rows, full width

**Button:** "Continue" (primary, full width of card) — disabled until input provided

---

### Step 2: Review Ingredients

**Centered card, max-width 700px**

**Header:**
- "We found 18 ingredients" (20px, semibold)
- "Edit quantities or remove items you don't need." (14px, muted)

**Ingredient table:**
- Clean rows, minimal borders

| Column | Content |
|--------|---------|
| Include | Checkbox (default checked) |
| Ingredient | Name (bold) |
| Quantity | Editable number input + unit dropdown |
| Confidence | Small bar or percentage (muted) |
| Source | "From: Croissant, Danish" (12px, muted) |

**Below table:**
- "+ Add ingredient" text link

**Button:** "Continue" (primary)

---

### Step 3: Confirm Top 3

**Centered content, max-width 800px**

**Header:**
- "Your top 3 cost drivers" (20px, semibold)
- "We'll focus negotiation here for maximum savings." (14px, muted)

**3 Cards (horizontal row, equal width):**

Each card:
- White background, subtle shadow
- 24px padding
- Border radius: 12px

Content:
- Rank badge: "#1" (small, `#22C55E` background, white text, top-left corner)
- Ingredient name (18px, semibold)
- Estimated quantity: "45 lbs/month" (14px, muted)
- Estimated spend: "$180" (24px, bold, monospace)

**Below cards:**
- "These items represent 68% of your estimated spend." (14px, muted, centered)

**Buttons (centered):**
- "Start Negotiation" (primary, large)
- "Edit selections" (text link below)

---

## Screen 3: Order Detail

### Header Row
- **Left:** "#ORD-001" (monospace) + Status badge
- **Right:** "Created Jan 10, 2026" (muted)

### Budget Row (subtle, below header)
- "Budget: $1,000" · "Current: $842" (green if under) · "Savings: $158 (14%)" — all in a row, muted style

---

### Progress Section (Vertical Phases)

Each phase is a card. Active phase has colored left border. Completed phases are collapsed to one line.

---

#### Phase 1: Sourcing

**Active state:**
- Card with `#3B82F6` left border (4px)
- Header: "Sourcing" + spinner
- Live log (monospace, 14px):
```
✓ Searching for flour suppliers...
✓ Found: Bay Area Foods Co
✓ Found: Golden Gate Grains
→ Searching for butter suppliers...
```

**Complete state:**
- Single row: "✓ Sourcing" (green checkmark) + "Found 12 suppliers" (muted)

---

#### Phase 2: Negotiation

**Active state:**
- Card with `#F97316` left border
- **Live banner at top:**
  - Orange background (`#FFF7ED`), orange text
  - "🔴 Live: Calling 2 vendors" + "[Bay Area Foods 1:23] [Fresh Farms 0:45]"

- **Vendor cards (2-column grid):**

Each card:
- Vendor name (bold)
- Ingredient (muted)
- Status:
  - Queued: "Queued" gray text
  - Calling: "📞 Calling... 0:45" orange text, pulsing dot, elapsed time
  - Done: "✓ 15% discount" green OR "No discount" gray
- "View transcript" link (appears when done)

**Complete state:**
- Single row: "✓ Negotiation" + "Best discount: 15%"

---

#### Phase 3: Evaluation

**Active state:**
- Card with `#3B82F6` left border
- "Scoring 8 suppliers..." with spinner

**Complete state:**
- Single row: "✓ Evaluation" + "Optimal vendors selected"
- Expandable: Click to see scoring table

---

#### Phase 4: Approval

**Active state:**
- Card with `#FACC15` left border
- **Recommendation block:**

Large card inside:
- Vendor: "Bay Area Foods" (20px, semibold)
- Total: "$842.50" (32px, bold, `#22C55E`)
- Summary: "3 items · Delivery · Arrives Jan 12" (14px, muted)
- Savings badge: "Saved $138 (14%)" — green pill

**Buttons:**
- "Approve & Pay" (primary, large)
- "Reject" (outline, rose text)

**Below buttons:**
- "Or reply YES to SMS" (12px, muted)

---

#### Phase 5: Payment

**Active state:**
- Card with `#8B5CF6` left border
- "Processing payment..." spinner
- "x402 Auth: 0xA3F8..." (monospace, muted)

**Complete state:**
- "✓ Payment Complete"
- Transaction hash (link to BaseScan)

---

## Screen 4: Orders

### Header Row
- **Left:** "Orders" (28px, bold)
- **Right:** "New Order" button (primary)

### Filters Row
- Status dropdown: All / Sourcing / Negotiating / Awaiting Approval / Complete
- Date range picker
- Search input

### Orders Table
Same style as Dashboard recent orders, but full page with pagination.

---

## Screen 5: Suppliers

### Header Row
- **Left:** "Suppliers" (28px, bold)
- **Right:** Search input

### Supplier Cards (Grid, 3 columns)

Each card:
- White background, subtle shadow
- Vendor name (bold)
- Location (muted)
- Tags: "Flour" "Sugar" (small pills, gray background)
- Rating: "★ 8.5" 
- Last rate: "$0.40/lb on Jan 5"
- "View details →" link

---

## Screen 6: Wallet

### Balance Card (Prominent)
- Large centered card, max-width 500px
- Balance: "$2,500.00" (40px, bold, monospace)
- "USDC" label (muted)
- Wallet address: "0x1234...5678" (monospace, muted) + copy icon
- "Add Funds" button (primary)

### Spending Limits (Below, smaller card)
- Daily: $5,000 (editable)
- Per transaction: $1,000 (editable)
- Require approval above: $500 (toggle + input)

### Transaction History
- Clean table: Date, Type (badge), Description, Amount (+/- colored), TX Hash (link)

---

## Screen 7: Inbox

### Layout
- Two panels: List (left, 35%) + Detail (right, 65%)
- Divider: 1px `#E5E7EB`

### List Panel
- Tabs: All · Calls · Emails · Invoices
- Each item row:
  - Icon (📞 📧 📄)
  - Vendor name (bold)
  - Preview text (truncated, muted)
  - Time (right-aligned, muted)
  - Unread: blue dot

### Detail Panel (for calls)
- Header: "Call with Bay Area Foods" + "2:34" duration + date
- Audio player: play button, progress bar, time, speed toggle
- Transcript:
```
[0:00] Agent: Hi, I'm calling on behalf of Sweet Dreams Bakery...
[0:12] Vendor: How can I help?
[0:15] Agent: We need 500 lbs of flour. What's your best price?
```
- Timestamps clickable
- Outcome badge: "15% Discount" (green pill)

---

## Global Components

### Buttons

**Primary Button:**
```tsx
<button className="bg-brand hover:bg-brand-dark text-white font-medium px-4 py-2.5 rounded-lg transition-colors">
  Button Text
</button>
```

**Secondary Button:**
```tsx
<button className="bg-white hover:bg-brand-light text-brand border border-brand font-medium px-4 py-2.5 rounded-lg transition-colors">
  Button Text
</button>
```

**Danger Button:**
```tsx
<button className="bg-white hover:bg-status-rose-light text-status-rose border border-status-rose font-medium px-4 py-2.5 rounded-lg transition-colors">
  Button Text
</button>
```

**Ghost Button:**
```tsx
<button className="bg-transparent hover:bg-gray-100 text-gray-500 font-medium px-4 py-2.5 rounded-lg transition-colors">
  Button Text
</button>
```

### Status Badge Component

```tsx
// components/StatusBadge.tsx
type Status = 'sourcing' | 'negotiating' | 'awaiting-approval' | 'paying' | 'complete' | 'failed';

const statusStyles: Record<Status, string> = {
  'sourcing': 'bg-status-blue-light text-status-blue',
  'negotiating': 'bg-status-orange-light text-status-orange',
  'awaiting-approval': 'bg-status-yellow-light text-status-yellow',
  'paying': 'bg-status-purple-light text-status-purple',
  'complete': 'bg-brand-light text-brand',
  'failed': 'bg-status-rose-light text-status-rose',
};

export function StatusBadge({ status }: { status: Status }) {
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusStyles[status]}`}>
      {status.replace('-', ' ')}
    </span>
  );
}
```

### Inputs

```tsx
<input 
  className="w-full bg-white border border-gray-200 rounded-lg px-4 py-3 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent"
  placeholder="Placeholder text"
/>
```

### Cards

```tsx
<div className="bg-white rounded-xl shadow-sm p-6">
  {/* Card content */}
</div>
```

**Card with colored left border (for phases):**
```tsx
<div className="bg-white rounded-xl shadow-sm p-6 border-l-4 border-status-blue">
  {/* Active phase content */}
</div>
```

### Toast Notifications

Use `sonner` or `react-hot-toast` library. Position bottom-right.

```tsx
<div className="bg-white rounded-xl shadow-lg p-4 flex items-center gap-3">
  <span className="text-status-orange">📞</span>
  <span className="text-sm text-gray-900">Calling Bay Area Foods...</span>
  <button className="text-gray-400 hover:text-gray-600">×</button>
</div>
```

Examples:
- 📞 "Calling Bay Area Foods..." (orange icon)
- ✓ "Negotiated 15% discount" (green icon)
- ⚠️ "Order needs approval" (yellow icon, clickable)

---

## Summary: Design Principles

1. **Whitespace is a feature.** Don't fill every pixel.
2. **Color means something.** Green = success/action. Orange = live/calling. Blue = processing. Yellow = attention. Rose = error.
3. **Typography hierarchy is clear.** Bold headlines, regular body, muted secondary.
4. **Tables are clean.** No heavy borders, just subtle dividers.
5. **Cards are light.** White + subtle shadow, not heavy borders.
6. **The Agent Activity panel is the hero.** Users should immediately see what's happening.

---

*End of specification.*
