# Haggl Branding Kit

**Version:** 1.0
**Date:** January 10, 2026

---

## Development Tools

### Required MCP Servers

Install the following MCP servers for component development:

**21st.dev MCP**
```bash
npx -y @anthropic-ai/mcp-server-21st-dev@latest
```
Used for AI-powered UI component generation. Integrates with Claude to generate React components from natural language descriptions.

**Shadcn MCP**
```bash
npx -y @anthropic-ai/mcp-server-shadcn@latest
```
Used for installing and managing Shadcn/UI components. Provides direct access to the Shadcn component registry.

### Usage in Claude Code

Add to your Claude Code MCP configuration:
```json
{
  "mcpServers": {
    "21st-dev": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-21st-dev@latest"]
    },
    "shadcn": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-shadcn@latest"]
    }
  }
}
```

---

## Brand Philosophy

Haggl is invisible infrastructure. The brand should feel like it disappears—letting the user's business take center stage. We use restraint as a design principle: minimal color, generous whitespace, and motion that feels natural rather than decorative.

**Core Principles:**
1. **Disappear** - The interface should feel like an extension of thought
2. **Breathe** - Generous spacing, never cramped
3. **Move with purpose** - Animation serves function, not decoration
4. **Monochrome first** - Color is reserved for meaning

---

## Logo

### Wordmark

The Haggl wordmark is set in **Inter** at **600 weight** with **-2% letter-spacing**. The double 'g' creates a natural visual anchor.

```
Haggl
```

**Specifications:**
- Font: Inter SemiBold (600)
- Letter-spacing: -0.02em
- All lowercase is acceptable in casual contexts
- Never modify letterforms or spacing

**Sizing:**
- Minimum size: 16px
- Primary size: 24px (navigation)
- Hero size: 48px (landing pages)

**Clear space:**
Maintain clear space equal to the height of the 'H' on all sides.

### Logomark (Optional)

For compact spaces, use the letter **H** from the wordmark in a subtle rounded square container.

```
┌─────┐
│  H  │
└─────┘
```

- Container: 1px border, 8px border-radius
- Border color: #E5E7EB (light mode) / #374151 (dark mode)
- Background: transparent

---

## Color System

### Philosophy

Haggl uses a near-monochrome palette. Color appears only to communicate:
- **State** (success, error, warning)
- **Action** (primary interactive elements)
- **Data** (charts, metrics)

The interface is predominantly grayscale. This creates calm and lets color moments feel intentional.

### Primary Palette

| Name | Hex | Usage |
|------|-----|-------|
| Black | #000000 | Primary text, wordmark |
| White | #FFFFFF | Backgrounds, inverse text |
| Gray 900 | #111827 | Headings, emphasis |
| Gray 600 | #4B5563 | Body text |
| Gray 400 | #9CA3AF | Secondary text, placeholders |
| Gray 200 | #E5E7EB | Borders, dividers |
| Gray 50 | #F9FAFB | Background tint |

### Accent Color

| Name | Hex | Usage |
|------|-----|-------|
| Blue | #2563EB | Primary CTA, links, focus states |
| Blue Light | #DBEAFE | Hover backgrounds, selection |

Blue is used sparingly—only for:
- Primary action buttons
- Interactive links
- Focus rings
- Selected states

### Semantic Colors

| Name | Hex | Usage |
|------|-----|-------|
| Green | #10B981 | Success, savings, confirmed |
| Red | #EF4444 | Error, failed, destructive |
| Amber | #F59E0B | Warning, pending, attention |

These appear only in:
- Status badges
- Toast notifications
- Form validation
- Data visualization

### Color Usage Rules

1. **No decorative color** - Every color must have meaning
2. **Gray is default** - When unsure, use grayscale
3. **One accent per view** - Avoid multiple colored CTAs competing
4. **Semantic colors are temporary** - They appear in response to state, then fade

---

## Typography

### Font Stack

```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

Inter is used exclusively. Its large x-height and open letterforms ensure readability at small sizes.

### Type Scale

| Name | Size | Weight | Line Height | Letter Spacing |
|------|------|--------|-------------|----------------|
| Display | 48px | 600 | 1.1 | -0.02em |
| H1 | 32px | 600 | 1.2 | -0.02em |
| H2 | 24px | 600 | 1.3 | -0.01em |
| H3 | 18px | 600 | 1.4 | 0 |
| Body | 15px | 400 | 1.6 | 0 |
| Body Small | 13px | 400 | 1.5 | 0 |
| Caption | 11px | 500 | 1.4 | 0.01em |
| Mono | 13px | 400 | 1.5 | 0 |

### Type Rules

1. **Two weights only** - 400 (regular) and 600 (semibold)
2. **No italics** - Use weight or color for emphasis
3. **Generous line height** - Body text always 1.5+
4. **Tight headings** - Negative letter-spacing for display sizes

---

## Spacing System

Based on 4px increments:

| Token | Value | Usage |
|-------|-------|-------|
| space-1 | 4px | Tight gaps, icon padding |
| space-2 | 8px | Related elements |
| space-3 | 12px | Form field gaps |
| space-4 | 16px | Card padding, component gaps |
| space-6 | 24px | Section gaps |
| space-8 | 32px | Major sections |
| space-12 | 48px | Page sections |
| space-16 | 64px | Hero spacing |

### Spacing Philosophy

- **More space than you think** - When in doubt, add more
- **Consistent rhythm** - Use the scale, don't invent values
- **Asymmetric is fine** - Top/bottom can differ from left/right

---

## Animation System

### Philosophy

Animation in Haggl serves three purposes:
1. **Orientation** - Help users understand spatial relationships
2. **Feedback** - Confirm actions were received
3. **Polish** - Make transitions feel smooth, not jarring

Animation should be **invisible**. Users should feel the interface is responsive without consciously noticing motion.

### Timing Curves

| Name | Curve | Duration | Usage |
|------|-------|----------|-------|
| Snap | ease-out | 150ms | Micro-interactions (hover, focus) |
| Smooth | ease-in-out | 200ms | State changes, toggles |
| Slide | cubic-bezier(0.4, 0, 0.2, 1) | 300ms | Panel transitions, modals |
| Spring | cubic-bezier(0.34, 1.56, 0.64, 1) | 400ms | Playful moments, success states |

### Core Animations

**Fade In**
```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
/* Duration: 200ms, ease-out */
```

**Slide Up**
```css
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
/* Duration: 300ms, ease-out */
```

**Scale In**
```css
@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
/* Duration: 200ms, ease-out */
```

**Pulse (Loading)**
```css
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
/* Duration: 1500ms, ease-in-out, infinite */
```

**Number Tick**
```css
@keyframes tick {
  0% { transform: translateY(0); }
  50% { transform: translateY(-100%); }
  50.01% { transform: translateY(100%); }
  100% { transform: translateY(0); }
}
/* Duration: 300ms, ease-in-out */
/* Used for updating numeric values */
```

### Animation Patterns

**Page Transitions:**
- New pages fade in over 200ms
- Content staggers in with 50ms delays between elements
- Maximum 5 staggered elements

**List Items:**
- Appear with slideUp, staggered 30ms
- On removal, fade out 150ms then collapse height 200ms

**Modals/Sheets:**
- Backdrop fades in 200ms
- Content scales in from 95% over 200ms
- Close: reverse, slightly faster (150ms)

**Buttons:**
- Hover: background color transition 150ms
- Active: scale to 98% over 100ms
- Disabled: opacity 0.5, no transition

**Toast Notifications:**
- Slide in from bottom-right, 300ms
- Auto-dismiss after 4 seconds
- Fade out over 200ms

**Radar Chart:**
- Data points animate from center outward
- Duration: 600ms with spring easing
- On preference change: morph to new shape over 400ms

**Preference Controls (UP/DOWN):**
- On click: button scales to 90% then springs back
- Weight value ticks to new number
- Related values adjust simultaneously

### Animation Rules

1. **Never block interaction** - Animations must not prevent clicking
2. **Respect reduced motion** - Honor `prefers-reduced-motion`
3. **No bouncing logos** - Motion is functional, not decorative
4. **Keep it short** - Maximum 400ms for any single animation
5. **Stagger thoughtfully** - Don't stagger more than 5 items

**Reduced Motion Fallback:**
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Component Patterns

Use the **Shadcn MCP** to install base components, then customize according to these specifications. Use **21st.dev MCP** for generating custom components from descriptions.

### Buttons

**Primary:**
- Background: Blue (#2563EB)
- Text: White
- Padding: 12px 20px
- Border-radius: 6px
- Hover: darken 10%
- Active: scale 98%

**Secondary:**
- Background: transparent
- Border: 1px solid Gray 200
- Text: Gray 900
- Hover: Background Gray 50

**Ghost:**
- Background: transparent
- Text: Gray 600
- Hover: Text Gray 900

### Cards

- Background: White
- Border: 1px solid Gray 200
- Border-radius: 8px
- Padding: 16px
- Shadow: none (borders only)
- Hover (if interactive): Border Gray 400

### Inputs

- Height: 40px
- Border: 1px solid Gray 200
- Border-radius: 6px
- Padding: 0 12px
- Focus: Border Blue, ring 2px Blue Light
- Placeholder: Gray 400

### Status Badges

Minimal pill-shaped badges:

| Status | Background | Text |
|--------|------------|------|
| Default | Gray 100 | Gray 600 |
| Success | Green 50 | Green 700 |
| Warning | Amber 50 | Amber 700 |
| Error | Red 50 | Red 700 |
| Info | Blue 50 | Blue 700 |

### Tables

- Header: Gray 50 background, Gray 600 text, 13px caption weight
- Rows: White background, 15px body text
- Borders: Horizontal only, Gray 200
- Row hover: Gray 50 background
- No zebra striping

---

## Iconography

Use **Lucide Icons** exclusively.

- Stroke width: 1.5px
- Size: 20px default, 16px compact, 24px prominent
- Color: inherits from text color

**Common Icons:**
- Navigation: Home, Package, Users, CreditCard, MessageSquare, Settings
- Actions: Plus, X, ChevronRight, ChevronDown, Search
- Status: Check, AlertCircle, Clock, Loader
- Preference: ChevronUp, ChevronDown (for UP/DOWN controls)

---

## Voice & Tone

### Principles

1. **Direct** - Say what you mean, no filler
2. **Calm** - Never urgent, never pushy
3. **Helpful** - Guidance over instruction

### Examples

**Good:**
- "Order placed"
- "3 vendors found"
- "Quality preference updated"
- "Payment confirmed"

**Avoid:**
- "Awesome! Your order has been successfully placed!"
- "We found 3 amazing vendors just for you!"
- "Great choice! Quality is now more important."
- "Congratulations! Payment complete!"

### Empty States

Keep them minimal:
- "No orders yet"
- "No vendors found"
- "No messages"

Add a subtle action when appropriate:
- "No orders yet. Create your first order."

### Error Messages

Be specific and actionable:
- "Payment failed. Check card details."
- "Vendor unreachable. Try again in 5 minutes."
- "Budget exceeded by $45.00"

---

## Demo Business Profile

The application ships with a pre-configured demo profile. Users can modify these values in Settings.

### Default Configuration

```json
{
  "business_id": "demo-bakery-001",
  "business_name": "Demo Business",
  "business_type": "bakery",
  "location": {
    "city": "San Francisco",
    "state": "CA",
    "zip_code": "94102"
  },
  "phone": "+1-555-000-0000",
  "preferences": {
    "quality": 0.30,
    "affordability": 0.35,
    "shipping": 0.15,
    "reliability": 0.20
  },
  "budget": {
    "default_order": 2000.00,
    "monthly_limit": 10000.00
  }
}
```

### Placeholder Text

When displaying demo data, use realistic but obviously placeholder content:

- Business name: "Demo Business"
- Phone: "+1-555-000-0000"
- Address: "123 Demo Street, San Francisco, CA 94102"

### Demo Indicator

In demo mode, show a subtle indicator:
- Small pill badge in header: "Demo"
- Gray 400 text, Gray 100 background
- Clicking opens Settings to configure real business info

---

## Dark Mode (Future)

The design system is prepared for dark mode but ships with light mode only.

**Dark Mode Mapping:**
| Light | Dark |
|-------|------|
| White | #0F0F0F |
| Gray 50 | #1A1A1A |
| Gray 200 | #2A2A2A |
| Gray 400 | #666666 |
| Gray 600 | #999999 |
| Gray 900 | #EEEEEE |
| Black | #FFFFFF |

Accent colors (Blue, Green, Red, Amber) remain unchanged but may need slight lightening for accessibility.

---

## Accessibility

### Color Contrast

All text meets WCAG AA standards:
- Body text (Gray 600 on White): 7.5:1
- Secondary text (Gray 400 on White): 4.6:1
- Primary button (White on Blue): 4.9:1

### Focus States

All interactive elements have visible focus:
- 2px Blue ring
- 2px offset from element
- Never removed for keyboard users

### Motion

- All animations respect `prefers-reduced-motion`
- No auto-playing video or GIFs
- Loading states use subtle pulse, not spinning

### Screen Readers

- All icons have aria-labels
- Status changes announced via aria-live regions
- Form errors linked via aria-describedby

---

## File Exports

### Logo Files

```
/brand/
  haggl-wordmark-black.svg
  haggl-wordmark-white.svg
  haggl-mark-black.svg
  haggl-mark-white.svg
```

### CSS Custom Properties

```css
:root {
  /* Colors */
  --color-black: #000000;
  --color-white: #FFFFFF;
  --color-gray-50: #F9FAFB;
  --color-gray-200: #E5E7EB;
  --color-gray-400: #9CA3AF;
  --color-gray-600: #4B5563;
  --color-gray-900: #111827;
  --color-blue: #2563EB;
  --color-blue-light: #DBEAFE;
  --color-green: #10B981;
  --color-red: #EF4444;
  --color-amber: #F59E0B;

  /* Typography */
  --font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-size-xs: 11px;
  --font-size-sm: 13px;
  --font-size-base: 15px;
  --font-size-lg: 18px;
  --font-size-xl: 24px;
  --font-size-2xl: 32px;
  --font-size-3xl: 48px;

  /* Spacing */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-6: 24px;
  --space-8: 32px;
  --space-12: 48px;
  --space-16: 64px;

  /* Borders */
  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 8px;

  /* Transitions */
  --transition-snap: 150ms ease-out;
  --transition-smooth: 200ms ease-in-out;
  --transition-slide: 300ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-spring: 400ms cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

### Tailwind Config Extension

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        brand: {
          blue: '#2563EB',
          'blue-light': '#DBEAFE',
        }
      },
      fontFamily: {
        sans: ['Inter', ...defaultTheme.fontFamily.sans],
      },
      animation: {
        'fade-in': 'fadeIn 200ms ease-out',
        'slide-up': 'slideUp 300ms ease-out',
        'scale-in': 'scaleIn 200ms ease-out',
        'pulse-slow': 'pulse 1500ms ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
      },
    },
  },
}
```

---

**Document Status:** Ready for Implementation
