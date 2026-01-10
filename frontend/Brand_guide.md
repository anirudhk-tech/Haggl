# Brand Style Guide: Rectangular Minimalism

A design system emphasizing sharp geometry, purposeful animations, and editorial clarity. This guide can be used to recreate this visual language in any frontend application.

---

## Core Design Philosophy

**"Brutalist Editorial"** — Clean, sharp, and intentional. Every element earns its place.

### Key Principles
1. **Zero border-radius** — All elements are perfectly rectangular (no rounded corners anywhere)
2. **High contrast** — Black fills on cream/warm white backgrounds
3. **Purposeful motion** — Animations that convey state, not decoration
4. **Editorial typography** — Clean sans-serif with monospace accents
5. **Generous whitespace** — Let content breathe

---

## Color System

### Light Theme (Default)
```css
:root {
  /* Warm cream background */
  --background: hsl(40, 86%, 97%);        /* #FDFAF5 - warm off-white */
  --foreground: hsl(240, 10%, 3.9%);      /* #0A0A0B - near black */

  /* Cards match background (no visual separation) */
  --card: hsl(40, 86%, 97%);
  --card-foreground: hsl(240, 10%, 3.9%);

  /* Subtle borders */
  --border: hsl(40, 20%, 85%);            /* Warm gray border */
  --input: hsl(240, 5.9%, 90%);

  /* Muted text */
  --muted: hsl(240, 4.8%, 95.9%);
  --muted-foreground: hsl(240, 3.8%, 46.1%);  /* ~46% gray */

  /* Primary = foreground (inverts on interaction) */
  --primary: hsl(240, 5.9%, 10%);
  --primary-foreground: hsl(0, 0%, 98%);

  /* CRITICAL: No border radius */
  --radius: 0;
}
```

### Paper Theme (Alternative)
```css
.theme-paper {
  --background: hsl(40, 30%, 96%);
  --foreground: hsl(30, 10%, 15%);
  --border: hsl(40, 15%, 82%);
  --muted-foreground: hsl(30, 8%, 45%);
}
```

---

## Typography

### Font Stack
```css
/* Primary: Clean humanist sans-serif */
font-family: 'IBM Plex Sans', system-ui, sans-serif;

/* Monospace: For numbers, codes, timestamps */
font-family: 'IBM Plex Mono', monospace;

/* Serif: For editorial headers (optional) */
font-family: 'Instrument Serif', Georgia, serif;

/* Geometric: For modern tech feel (optional) */
font-family: 'Space Grotesk', system-ui, sans-serif;
```

### Type Scale
```css
/* Page headers */
.page-header {
  font-size: 2.25rem;     /* text-4xl */
  font-weight: 500;       /* medium */
  letter-spacing: -0.025em; /* tracking-tight */
  color: var(--foreground);
}

/* Page subtitles */
.page-header-subtitle {
  font-size: 1rem;
  font-weight: 300;       /* light */
  color: var(--muted-foreground);
}

/* Section headers */
.section-header {
  font-size: 0.875rem;    /* text-sm */
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em; /* tracking-wider */
  color: var(--muted-foreground);
}

/* Body text */
.body-text {
  font-size: 0.875rem;
  color: var(--foreground);
}

/* Muted/secondary text */
.muted-text {
  font-size: 0.75rem;     /* text-xs */
  color: var(--muted-foreground);
}
```

---

## The Zero-Radius Rule

**CRITICAL**: Force all elements to have no border radius.

```css
/* Global override */
* {
  border-radius: 0 !important;
}

/* Tailwind config */
borderRadius: {
  lg: "0",
  md: "0",
  sm: "0",
  DEFAULT: "0",
}
```

This creates the signature "rectangular" feel — buttons, cards, inputs, and all UI elements are sharp rectangles.

---

## Signature Animations

### 1. Fill Hover (Horizontal Slide-In)
The most distinctive animation. On hover, a black fill slides in from the left, inverting colors.

```css
.fill-hover {
  position: relative;
  overflow: hidden;
  background-color: var(--background);
}

.fill-hover::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 0;
  height: 100%;
  background-color: var(--foreground);
  transition: width 0.17s ease;
  z-index: 0;
}

.fill-hover:hover::before {
  width: 100%;
}

/* Invert text/icons on hover */
.fill-hover:hover,
.fill-hover:hover * {
  color: var(--background) !important;
}

.fill-hover:hover svg {
  stroke: var(--background) !important;
}

/* Keep content above the fill */
.fill-hover > * {
  position: relative;
  z-index: 1;
}
```

### 2. Vertical Fill (Bottom-Up)
Same concept, but fills from bottom to top. Good for calendar days, tabs.

```css
.fill-hover-vertical {
  position: relative;
  overflow: hidden;
}

.fill-hover-vertical::before {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 0;
  background-color: var(--foreground);
  transition: height 0.2s ease;
  z-index: 0;
}

.fill-hover-vertical:hover::before,
.fill-hover-vertical.selected::before {
  height: 100%;
}
```

### 3. Sliding Indicator (Vercel-Style)
For navigation and tabs — a filled indicator that smoothly animates between items.

```jsx
// Using Framer Motion
<motion.div
  layoutId="activeIndicator"
  className="absolute inset-0 bg-foreground"
  transition={{
    type: "tween",
    duration: 0.1,
    ease: "easeOut"
  }}
/>
```

**Key properties:**
- `layoutId` enables automatic position interpolation
- Duration: 100-150ms (fast, snappy)
- Ease: `easeOut` for responsive feel

### 4. Underline Indicator (Hover)
A subtle underline that appears and slides on hover.

```jsx
<motion.div
  className="absolute bottom-0 h-[2px] bg-foreground"
  animate={{
    left: underlinePosition.left,
    width: underlinePosition.width,
    opacity: isHovering ? 1 : 0,
  }}
  transition={{
    type: "tween",
    duration: 0.1,
    ease: "easeOut"
  }}
/>
```

### 5. Expand/Collapse Content
For accordions, dropdowns, selected day details.

```jsx
<motion.div
  initial={{ opacity: 0, height: 0, y: -20 }}
  animate={{ opacity: 1, height: "auto", y: 0 }}
  exit={{ opacity: 0, height: 0, y: -20 }}
  transition={{
    duration: 0.3,
    ease: [0.4, 0, 0.2, 1]  // Custom cubic-bezier
  }}
/>
```

---

## Component Patterns

### Card / Container
```jsx
// Base card - minimal styling
<div className="border border-border bg-background">
  {/* Content */}
</div>

// Card with glass effect (subtle)
<div className="border border-border bg-background backdrop-blur-none">
  {/* Content */}
</div>
```

### Card Header
```jsx
<div className="px-5 py-4 border-b border-border">
  <h2 className="text-sm font-medium uppercase tracking-wider text-muted-foreground">
    Section Title
  </h2>
</div>
```

### List Item (with Fill Hover)
```jsx
<div className="fill-hover flex items-center justify-between px-5 py-4 border-b border-border cursor-pointer">
  <div className="flex items-center gap-4">
    <span className="text-xs text-muted-foreground w-6">01</span>
    <div>
      <p className="text-sm font-medium">Primary Text</p>
      <p className="text-sm text-muted-foreground">Secondary text</p>
    </div>
  </div>
  <ArrowUpRight className="w-4 h-4 text-muted-foreground opacity-0 group-hover:opacity-100" />
</div>
```

### Button
```jsx
// Default button - inverts on hover
<button className="
  h-10 px-4 py-2
  bg-background
  border border-foreground/20
  text-foreground text-sm font-medium
  hover:bg-foreground hover:text-background
  transition-colors
">
  Button Text
</button>

// Ghost button
<button className="
  h-10 px-4 py-2
  bg-background
  text-foreground text-sm font-medium
  hover:bg-foreground hover:text-background
">
  Ghost Button
</button>
```

### Input
```jsx
<input className="
  h-10 w-full
  px-3 py-2
  bg-background
  border border-input
  text-sm
  placeholder:text-muted-foreground
  focus:outline-none focus:ring-2 focus:ring-ring
" />
```

### Navigation Bar
```jsx
<nav className="border-b border-border bg-background">
  <div className="max-w-6xl mx-auto px-8 py-4 flex items-center justify-between">
    {/* Nav items with sliding fill indicator */}
    <ul className="flex gap-1 relative">
      {/* Active fill indicator (absolute positioned) */}
      <motion.div
        layoutId="navFill"
        className="absolute inset-y-0 bg-foreground z-10"
        style={{ left: activeLeft, width: activeWidth }}
      />

      {navItems.map((item) => (
        <li>
          <a className="
            flex items-center gap-2
            px-4 py-2
            border border-border
            relative
          ">
            <Icon className={cn("w-4 h-4 z-20", isActive && "text-background")} />
            <span className={cn("text-sm font-medium z-20", isActive && "text-background")}>
              {item.label}
            </span>
          </a>
        </li>
      ))}
    </ul>
  </div>
</nav>
```

### Calendar Day Cell
```jsx
<div className="flex flex-col items-center py-5 px-2 relative cursor-pointer">
  {/* Fill indicator (absolute, animates between days) */}
  {isSelected && (
    <motion.div
      layoutId="dayFill"
      className="absolute inset-0 bg-foreground"
      transition={{ type: "tween", duration: 0.1, ease: "easeOut" }}
    />
  )}

  {/* Today outline (always visible if today) */}
  {isToday && (
    <div className="absolute inset-0 border-2 border-foreground z-10" />
  )}

  {/* Content */}
  <span className={cn(
    "text-[10px] uppercase tracking-wider mb-2 z-10",
    isSelected ? "text-background" : "text-muted-foreground"
  )}>
    Mon
  </span>
  <span className={cn(
    "text-xl font-medium z-10",
    isSelected ? "text-background" : "text-foreground"
  )}>
    15
  </span>
  <span className={cn(
    "mt-2 text-xs z-10",
    isSelected ? "text-background" : "text-muted-foreground"
  )}>
    {assignmentCount || "—"}
  </span>
</div>
```

---

## Layout Patterns

### Page Layout
```jsx
<div className="min-h-screen bg-background">
  {/* Top border accent */}
  <div className="h-px bg-border" />

  {/* Navigation */}
  <nav className="border-b border-border">...</nav>

  {/* Main content */}
  <main className="max-w-6xl mx-auto px-8 pb-10">
    {/* Page header */}
    <header className="py-8 border-b border-border">
      <h1 className="page-header">Page Title</h1>
      <p className="page-header-subtitle">Subtitle text</p>
    </header>

    {/* Content grid */}
    <div className="grid grid-cols-12 min-h-[calc(100vh-160px)]">
      {/* Main column (8 cols) */}
      <div className="col-span-8 border-r border-border p-8">
        ...
      </div>

      {/* Sidebar column (4 cols) */}
      <div className="col-span-4 p-8">
        ...
      </div>
    </div>
  </main>
</div>
```

### Numbered List Pattern
Used for classes, items, rankings:
```jsx
<div className="flex items-center gap-4">
  <span className="text-xs text-muted-foreground w-6 font-mono">
    {String(index + 1).padStart(2, "0")}
  </span>
  <div>
    <p className="text-sm font-medium">{title}</p>
    <p className="text-sm text-muted-foreground">{subtitle}</p>
  </div>
</div>
```

---

## Animation Timing Reference

| Animation | Duration | Easing | Use Case |
|-----------|----------|--------|----------|
| Fill hover | 170ms | `ease` | Interactive elements |
| Vertical fill | 200ms | `ease` | Calendar days, tabs |
| Nav indicator | 100ms | `easeOut` | Navigation sliding |
| Underline | 100ms | `easeOut` | Hover indicators |
| Content expand | 300ms | `cubic-bezier(0.4, 0, 0.2, 1)` | Accordions, dropdowns |
| Sidebar slide | 150ms | `ease-out` | Panel transitions |
| Opacity fade | 100-150ms | `ease-out` | Appearing elements |

---

## Implementation Checklist

### Required Dependencies
```json
{
  "framer-motion": "^10.x",
  "tailwindcss": "^3.x",
  "tailwindcss-animate": "^1.x",
  "@radix-ui/react-*": "latest",
  "lucide-react": "latest",
  "class-variance-authority": "latest",
  "clsx": "latest",
  "tailwind-merge": "latest"
}
```

### Google Fonts to Load
```html
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&family=Instrument+Serif:wght@400;600&family=Space+Grotesk:wght@400;500;600&display=swap" rel="stylesheet">
```

### Tailwind Config Essentials
```js
module.exports = {
  theme: {
    extend: {
      fontFamily: {
        sans: ['IBM Plex Sans', 'system-ui', 'sans-serif'],
        mono: ['IBM Plex Mono', 'monospace'],
      },
      borderRadius: {
        lg: "0",
        md: "0",
        sm: "0",
        DEFAULT: "0",
      },
      colors: {
        border: "hsl(var(--border))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```

### CSS Reset (Add to index.css)
```css
@layer base {
  * {
    border-radius: 0 !important;
  }

  body {
    @apply bg-background text-foreground font-sans;
  }
}
```

---

## Quick Reference: Class Names

| Pattern | Classes |
|---------|---------|
| Card | `border border-border bg-background` |
| Card header | `px-5 py-4 border-b border-border` |
| Section title | `text-sm font-medium uppercase tracking-wider text-muted-foreground` |
| Fill hover item | `fill-hover px-5 py-4 border-b border-border cursor-pointer` |
| Page header | `text-4xl font-medium tracking-tight` |
| Muted text | `text-xs text-muted-foreground` |
| Numbered index | `text-xs text-muted-foreground w-6 font-mono` |
| Button | `h-10 px-4 border border-foreground/20 hover:bg-foreground hover:text-background` |

---

## Brand Summary

**Visual Identity:**
- Sharp rectangles (zero radius)
- Warm cream background with near-black text
- Thin borders defining structure
- High contrast on interaction (black fills)

**Motion Identity:**
- Fast, snappy transitions (100-200ms)
- Directional fills (left-to-right, bottom-to-top)
- Smooth indicator sliding (Vercel-style)
- Purposeful, not decorative

**Typography Identity:**
- IBM Plex Sans for body
- Uppercase + tracking for section headers
- Monospace for numbers and codes
- Light weight for subtitles

**Interaction Identity:**
- Hover = invert (fill with foreground color)
- Active = filled state
- Focus = ring outline
- Everything clickable has visible hover state
