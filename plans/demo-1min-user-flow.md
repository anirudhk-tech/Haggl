# Haggl - 1 Minute Demo Script
## Business Vendor Order Flow

**Total Duration:** 60 seconds

---

## The Flow (Visual Timeline)

```
[0:00] INTRO → [0:10] INPUT → [0:18] SOURCE → [0:28] NEGOTIATE → [0:42] APPROVE → [0:50] PAY → [0:57] CONFIRM → [1:00] END
```

---

## Complete User Flow

```
1. INPUT        → Business owner enters ingredients + budget
2. SOURCE       → AI finds wholesale suppliers via web search
3. NEGOTIATE    → AI calls vendors to negotiate prices
4. APPROVE      → Present best options, request owner approval
5. PAY          → Payment agent executes via pre-saved invoice
6. CONFIRM      → On-chain confirmation + order complete
```

---

## Scene-by-Scene Breakdown

### Scene 1: Hook (0:00 - 0:10)
**Duration:** 10 seconds

**Say:**
> "What if AI could source, negotiate, and pay for your business supplies - with your approval? This is Haggl."

**Show:** Dashboard with wallet balance ($500 USDC)

---

### Scene 2: Input Order (0:10 - 0:18)
**Duration:** 8 seconds

**Say:**
> "A bakery needs flour, eggs, butter, sugar - $2,000 budget."

**Action:** Click "Start Order" or run demo command

**Show:**
```
Ingredients: flour, eggs, butter, sugar
Budget: $2,000
Location: San Francisco, CA
```

---

### Scene 3: Sourcing (0:18 - 0:28)
**Duration:** 10 seconds

**Say:**
> "The sourcing agent finds 12 real wholesale suppliers in seconds."

**Show:**
```
[SOURCING] Finding suppliers...
  → Bay Area Foods Co
  → Golden Gate Grains
  → Fresh Farm Eggs
  → 12 suppliers found
```

---

### Scene 4: Negotiation - THE WOW MOMENT (0:28 - 0:42)
**Duration:** 14 seconds

**Say:**
> "Now the AI makes REAL phone calls to negotiate. These are actual calls happening right now."

**Show:**
```
[CALLING] Negotiating with vendors...
  "Hi, I'm calling on behalf of Sweet Dreams Bakery..."
  "We need 500 lbs of flour, what's your best bulk pricing?"
  → Negotiated 15% bulk discount!
  → Free shipping on eggs!
```

**Key:** Pause to let the impact land. This is the moment judges remember.

---

### Scene 5: Approval Request (0:42 - 0:50)
**Duration:** 8 seconds

**Say:**
> "Before purchasing, Haggl asks for your approval with the best options."

**Show:**
```
[APPROVAL REQUIRED]
  Best combination found:
  - Bay Area Foods: flour @ $212.50 (15% off)
  - Fresh Farm Eggs: eggs @ $485.00 (free shipping)
  - Dairy Direct: butter @ $650.00
  - SweetSupply: sugar @ $500.00

  Total: $1,847.50 (under budget by $152.50)

  → Owner clicks APPROVE
```

---

### Scene 6: Payment (0:50 - 0:57)
**Duration:** 7 seconds

**Say:**
> "The payment agent executes via x402 - on-chain, autonomous."

**Show:**
```
[PAYMENT] Executing via x402...
  Processing invoice...
  → Authorization: APPROVED
  → TX: 0x8f3e7b2a...

  Total: $1,847.50
  Savings: $152.50
```

---

### Scene 7: Close (0:57 - 1:00)
**Duration:** 3 seconds

**Say:**
> "Source. Negotiate. Approve. Pay. That's Haggl."

**Show:** BaseScan with confirmed transaction

---

## Quick Reference Card

| Time | Phase | Key Visual | Key Line |
|------|-------|------------|----------|
| 0:00 | Hook | Wallet | "With your approval" |
| 0:10 | Input | Ingredient list | "$2,000 budget" |
| 0:18 | Source | Suppliers found | "12 real suppliers" |
| 0:28 | Negotiate | Phone call | "REAL phone calls" |
| 0:42 | Approve | Best options | "Asks for your approval" |
| 0:50 | Pay | TX hash | "Executes via x402" |
| 0:57 | Close | Confirmation | "Source. Negotiate. Approve. Pay." |

---

## The Complete Technical Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. INPUT                                                    │
│    Business owner enters: ingredients, quantities, budget   │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. SOURCING AGENT                                           │
│    Exa.ai search → Claude extraction → 12 vendors found     │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. CALLING AGENT                                            │
│    Vapi TTS → Real phone calls → Negotiate prices           │
│    "What's your best bulk pricing?"                         │
│    → Discounts secured, terms discussed                     │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. EVALUATION AGENT                                         │
│    Score vendors → Optimize within budget → Select best     │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. APPROVAL REQUEST                                         │
│    Present options to business owner                        │
│    Show: vendors, prices, savings, total                    │
│    → Wait for APPROVE / DENY                                │
└─────────────────────┬───────────────────────────────────────┘
                      ▼ (on APPROVE)
┌─────────────────────────────────────────────────────────────┐
│ 6. PAYMENT AGENT                                            │
│    Load pre-saved invoice                                   │
│    x402 authorization (budget check, escrow lock)           │
│    Execute payment                                          │
│    Capture confirmation                                     │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. CONFIRMATION                                             │
│    On-chain TX hash → BaseScan proof                        │
│    SMS/Email notification to owner                          │
│    Order marked complete                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Fallback Options

**If calls fail:** Play pre-recorded negotiation audio (30s clip)

**If payment fails:** Show pre-generated TX hash on BaseScan

**If everything fails:** Walk through code + show architecture diagram

---

## Pre-Demo Checklist

- [ ] Backend running (`uvicorn src.server:app`)
- [ ] Frontend running (`npm run dev`)
- [ ] Wallet funded (500 USDC visible)
- [ ] Pre-saved invoice ready
- [ ] BaseScan tab open
- [ ] Audio working (for call playback)
- [ ] Demo data cleared from previous runs

---

## The One Thing to Remember

**The WOW moment is the phone call.**

Everything else supports that. If judges remember one thing, it's: "Wait, it actually called them?"

Make sure Scene 4 lands. Pause. Let them hear it. Let it sink in.
