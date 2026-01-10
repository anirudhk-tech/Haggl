# Pitch Script
## Haggl - 3-Minute Presentation

---

## Opening Hook (15 seconds)

> "Sarah runs Sweet Dreams Bakery. Every week, she spends 6 hours calling suppliers, comparing prices, and managing invoices. She knows she's overpaying, but who has time to negotiate when you're running a business? And when she needs to reorder flour, she's stuck digging through emails while frosting cakes."

---

## The Problem (20 seconds)

> "Small business owners face three painful realities:
>
> First, **sourcing takes forever** - 5 to 10 hours per week finding and comparing suppliers.
>
> Second, **they have no negotiating power** - individual businesses can't get bulk discounts like big corporations.
>
> Third, **payments are fragmented** - multiple invoices, multiple methods, constant reconciliation.
>
> This costs them thousands of dollars and dozens of hours every month."

---

## The Solution (30 seconds)

> "We built Haggl - four AI agents that source, negotiate, and pay for business supplies autonomously.
>
> **Agent 1** uses Exa.ai to search the web and find every potential supplier.
>
> **Agent 2** - and this is where it gets interesting - makes **real phone calls** via Vapi to negotiate bulk discounts. It's literally calling vendors right now.
>
> **Agent 3** evaluates all options and selects the optimal combination within budget.
>
> **Agent 4** processes invoices and executes payments through the **x402 protocol** - real on-chain transactions, fully autonomous.
>
> And here's the best part: Sarah can **text us to reorder**. 'Reorder flour' - that's it. We pull her last order, confirm the vendor, and she replies APPROVE. Done while frosting a cake.
>
> All four agents work **concurrently**. What took Sarah 6 hours now takes 3 minutes - or one text message."

---

## Live Demo (90 seconds)

> "Let me show you. Sarah needs flour, eggs, butter, and sugar with a $2,000 budget."

*[Run demo command]*

> "Watch the sourcing agent find suppliers across the web..."

*[Wait for Phase 1]*

> "Now the negotiation agent is making real phone calls. Listen..."

*[Wait for Vapi call]*

> "It just negotiated a 15% discount by asking about bulk pricing. All these calls are happening simultaneously.
>
> The evaluation agent scores vendors on quality and price, optimizes within budget...
>
> And now x402 payments. These are real USDC transactions on Base network."

*[Show BaseScan]*

> "There's the proof. Transaction confirmed on the blockchain. No human clicked 'confirm' - the agent decided and paid autonomously."

---

## Impact (20 seconds)

> "Results for Sarah:
>
> - **Time saved:** 6 hours per week → 3 minutes
> - **Money saved:** 15% average discount through negotiation
> - **Peace of mind:** Every decision logged, every payment verified on-chain
>
> For a business ordering $10,000 monthly, that's **$1,500 saved per month** and **24 hours reclaimed**."

---

## Why This Matters (20 seconds)

> "Most AI demos can either search, OR chat, OR mock a payment.
>
> Haggl does something no one else has shown:
>
> **Real phone negotiations** - AI calling real vendors, getting real discounts.
>
> **Real autonomous payments** - x402 protocol executing actual transactions.
>
> This isn't a demo of what AI might do someday. This is AI doing procurement **right now**."

---

## Closing (15 seconds)

> "We built Haggl for Sarah - and for millions of small business owners drowning in procurement tasks.
>
> Four agents. Concurrent execution. Real negotiations. Real payments.
>
> **The future of B2B commerce isn't coming - it's running in this demo.**
>
> Thank you."

---

## Q&A Prep

### "How does the phone negotiation work?"
> "We use Vapi's voice AI platform. It creates a Claude-powered assistant that makes outbound calls with realistic text-to-speech. The AI has specific negotiation strategies - mentioning competitors, asking for bulk pricing, offering long-term commitments. All calls are transcribed and analyzed for outcomes."

### "Explain the x402 payment flow"
> "x402 is an authorization layer. When the agent wants to pay an invoice, it first transfers USDC to our escrow wallet - that's the x402 signature. Once our backend verifies that on-chain payment, we execute the actual payment to the vendor via Stripe or ACH. The vendor receives normal payment - they never know x402 exists. This gives us a secure, auditable way for AI to spend money autonomously."

### "How does SMS ordering work?"
> "We use Twilio for SMS. Business owners text our number with commands like 'Reorder flour' or 'Order 500 lbs sugar'. Claude parses the intent and we look up their order history in MongoDB. For reorders, we auto-fill from their last purchase - same vendor, same quantity, same price. They just reply APPROVE and we handle the rest. No app download, works on any phone."

### "Can they import bulk orders?"
> "Yes, CSV upload. They export from QuickBooks, their inventory system, or even a Google Sheet. We auto-detect column mappings - ingredient, quantity, unit, quality. Upload once, we source everything. Great for the initial setup or weekly bulk orders."

### "What's the business model?"
> "Three options we're exploring:
> 1. Transaction fee (0.5-1% of order value)
> 2. Subscription for businesses ($50-200/month)
> 3. Success fee (percentage of negotiated savings)
>
> Given average 15% negotiation savings, even a 20% success fee leaves businesses way ahead."

### "How do you ensure AI doesn't overpay?"
> "Multiple safeguards:
> 1. Budget constraints are hard limits - agent won't exceed
> 2. Evaluation scoring penalizes high prices
> 3. Competitive quoting - agent mentions other suppliers' prices
> 4. All decisions logged to MongoDB for audit
> 5. x402 spend limits can be configured
> 6. Large purchases require SMS approval before proceeding"

### "What's the total addressable market?"
> "$2.3 trillion B2B procurement market globally. Even focusing just on small business ingredient sourcing, that's $180 billion. We're starting with food service - bakeries, restaurants, caterers - where ingredient quality matters and margins are tight."

---

## Key Stats to Memorize

- **6 hours/week** → 3 minutes (time saved)
- **15%** average negotiation discount
- **12** suppliers found per order
- **6** concurrent phone calls
- **$1,500/month** savings for $10k/month business
- **<3 minutes** total demo time
- **x402** for autonomous payments
- **Vapi** for voice AI

---

## Body Language Notes

- **Opening:** Conversational, relatable (Sarah's story)
- **Problem:** Slight frustration in voice
- **Solution:** Build excitement with each agent
- **Demo:** Confident pauses during Vapi call
- **BaseScan moment:** Point at screen, make eye contact with judges
- **Closing:** Strong, slow delivery on "right now"

---

**Pitch Status:** Ready
**Practice Runs Needed:** 3-5