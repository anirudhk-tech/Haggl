# Haggl Frontend

Beautiful, modern frontend for Haggl - AI Buyer for Small Businesses.

## Tech Stack

- **Framework:** Next.js 14 (App Router)
- **Styling:** Tailwind CSS
- **Icons:** Lucide React
- **Font:** Inter (Google Fonts)
- **Notifications:** Sonner

## Getting Started

### Install Dependencies

```bash
npm install
```

### Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── app/
│   ├── dashboard/          # Dashboard with stats and agent activity
│   ├── new-order/          # 3-step order creation flow
│   ├── orders/             # Orders list and detail pages
│   ├── suppliers/          # Supplier directory
│   ├── wallet/             # Wallet and transaction history
│   ├── inbox/              # Call transcripts and messages
│   ├── settings/           # User settings
│   ├── layout.tsx          # Root layout with NavBar
│   └── globals.css         # Global styles
├── components/
│   ├── NavBar.tsx          # Top navigation bar
│   ├── AgentActivityPanel.tsx  # Live agent status
│   ├── StatusBadge.tsx     # Order status badges
│   ├── StatCard.tsx        # Dashboard stat cards
│   ├── OrderCard.tsx       # Order list item
│   └── ProgressPhase.tsx    # Order progress phases
└── package.json
```

## Features

- **Dashboard** - Overview with stats, agent activity, and recent orders
- **New Order** - 3-step flow: Upload → Review → Confirm
- **Order Tracking** - Real-time progress through 5 phases
- **Supplier Directory** - Browse and search suppliers
- **Wallet Management** - View balance, set limits, transaction history
- **Inbox** - View call transcripts, emails, and invoices
- **Settings** - Profile and preferences

## Design System

- **Primary Color:** Green (#22C55E)
- **Status Colors:** Blue (processing), Orange (live/calling), Yellow (attention), Rose (error), Purple (payment)
- **Typography:** Inter font family
- **Spacing:** Generous whitespace, clean minimal design
- **Max Width:** 1100px content area, 1440px overall

## API Integration

Currently uses mock data. Connect to the Haggl backend API by:

1. Create `lib/api.ts` for API client
2. Replace mock data in pages with API calls
3. Add loading and error states

Example API endpoints:
- `GET /api/orders` - List orders
- `GET /api/orders/:id` - Order details
- `POST /api/orders` - Create order
- `GET /api/wallet` - Wallet info
- `GET /api/suppliers` - Supplier list

