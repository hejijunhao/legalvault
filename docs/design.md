# LegalVault — Brand UI & Design Blueprint

> **The intelligent lawyer's workstation.**
>
> This document defines the overarching visual identity, design principles, and UI guidelines for LegalVault. It serves as the single source of truth for anyone building, extending, or reviewing the interface.

---

## Table of Contents

1. [Design Philosophy](#1-design-philosophy)
2. [Brand Identity](#2-brand-identity)
3. [Color System](#3-color-system)
4. [Typography](#4-typography)
5. [Spacing & Layout](#5-spacing--layout)
6. [Border Radius & Elevation](#6-border-radius--elevation)
7. [Iconography](#7-iconography)
8. [Motion & Animation](#8-motion--animation)
9. [Component Library](#9-component-library)
10. [Surface & Material Effects](#10-surface--material-effects)
11. [Patterns & Conventions](#11-patterns--conventions)
12. [Dark Mode](#12-dark-mode)
13. [Accessibility](#13-accessibility)
14. [File Reference Map](#14-file-reference-map)

---

## 1. Design Philosophy

LegalVault's interface is built on four guiding principles:

### 1.1 Professional Authority
The legal domain demands trust. We pair a classic serif typeface (Libre Baskerville) for headings with a modern sans-serif (Inter) for body text. This duality communicates: *established expertise, delivered through modern technology*.

### 1.2 Calm Clarity
Legal research is mentally demanding. The interface stays out of the user's way with muted neutral backgrounds, generous whitespace, and restrained color use. The only vibrant color — our signature lime green — is reserved for interactive moments and progressive disclosure.

### 1.3 Invisible Complexity
Powerful AI workflows run under a simple surface. Complex multi-step research pipelines present as a single search box. Frosted-glass headers and staggered animations provide spatial awareness without visual clutter.

### 1.4 Intentional Motion
Every animation serves a purpose — guiding focus, confirming actions, or preserving spatial context. We never animate for decoration. Transitions are fast enough to feel responsive, slow enough to be perceived.

---

## 2. Brand Identity

### 2.1 Logo

| Property       | Value                                |
|----------------|--------------------------------------|
| File           | `/public/images/legalvault-logo.svg` |
| Header size    | `h-8 w-auto` (32px height)          |
| Auth page size | `h-10 w-auto` (40px height)         |
| Clear space    | Minimum 8px on all sides            |

The logo is always used as an SVG to ensure crispness at all resolutions. It links to the application root (`/`).

### 2.2 Product Name

- Rendered as **LegalVault** (one word, capital L and V).
- Uses the interface typeface (Inter) — not the serif heading face.
- Never styled with special effects, gradients, or color treatments.

### 2.3 Tagline

> *The intelligent lawyer's workstation.*

Used in metadata and marketing contexts. Not displayed in the application chrome.

---

## 3. Color System

LegalVault uses a dual-layer color architecture: **CSS custom properties** (via HSL) for theme-aware tokens, and **direct hex values** for brand-specific accents.

### 3.1 Brand Accent

| Name       | Value     | HSL              | Usage                                      |
|------------|-----------|------------------|---------------------------------------------|
| **LV Lime** | `#9FE870` | `97 70% 71%`    | Primary interactive accent — buttons, active states, citations, query-type pills |

This is the single brand color. It appears sparingly to create maximum impact.

### 3.2 Semantic Tokens (Light Mode)

| Token                  | HSL Value             | Approximate Hex | Role                         |
|------------------------|-----------------------|-----------------|------------------------------|
| `--background`         | `0 0% 100%`          | `#FFFFFF`       | Page background              |
| `--foreground`         | `222.2 84% 4.9%`     | `#0B0F1A`       | Primary text                 |
| `--primary`            | `222.2 47.4% 11.2%`  | `#0F172A`       | Dark navy — buttons, headings |
| `--primary-foreground` | `210 40% 98%`        | `#F8FAFC`       | Text on primary              |
| `--secondary`          | `210 40% 96.1%`      | `#F1F5F9`       | Subtle surface fill          |
| `--muted`              | `210 40% 96.1%`      | `#F1F5F9`       | Disabled/muted surfaces      |
| `--muted-foreground`   | `215.4 16.3% 46.9%`  | `#64748B`       | Secondary text               |
| `--destructive`        | `0 84.2% 60.2%`      | `#EF4444`       | Error/danger actions         |
| `--border`             | `214.3 31.8% 91.4%`  | `#E2E8F0`       | Default borders              |
| `--ring`               | `222.2 84% 4.9%`     | `#0B0F1A`       | Focus ring                   |
| `--radius`             | —                     | `0.5rem` (8px)  | Base border radius           |

### 3.3 Navigation Colors

| Element           | Value     | Usage                    |
|-------------------|-----------|--------------------------|
| Active nav link   | `#525766` | Current page indicator   |
| Inactive nav link | `#8992A9` | Default navigation text  |
| Icon stroke       | `#8992A9` | Header icons (bell, profile) |

### 3.4 Conversational UI Colors

| Element            | Value     | Usage                          |
|--------------------|-----------|--------------------------------|
| User message       | `#007AFF` | User chat bubble background    |
| Assistant message  | `#E9E9EB` | AI response bubble background  |
| Citation highlight | `#9FE870` | Source reference badges/links  |
| Title text         | `#111827` | Heading color (Gray-900)       |

### 3.5 Alert Semantic Colors

| Variant       | Border           | Background | Text         |
|---------------|------------------|------------|--------------|
| Destructive   | `red-500/50`     | `red-50`   | `red-600`    |
| Success       | `green-500/50`   | `green-50` | `green-600`  |
| Warning       | `yellow-500/50`  | `yellow-50`| `yellow-600` |
| Info          | `blue-500/50`    | `blue-50`  | `blue-600`   |

### 3.6 Background Gradients

**App shell** (light blue-gray sweep):
```
from-[#EFF2F5] via-[#E3E7EB] to-[#D9DEE3]
```

**Auth pages** (dark charcoal):
```css
linear-gradient(135deg, rgb(37, 38, 44) 0%, rgb(50, 55, 65) 50%, rgb(37, 38, 44) 100%)
```

### 3.7 Chart Colors (Tremor / Data Visualization)

| Token      | HSL              | Usage         |
|------------|------------------|---------------|
| `--chart-1`| `12 76% 61%`    | Orange-red    |
| `--chart-2`| `173 58% 39%`   | Teal          |
| `--chart-3`| `197 37% 24%`   | Dark blue     |
| `--chart-4`| `43 74% 66%`    | Yellow-gold   |
| `--chart-5`| `27 87% 67%`    | Orange        |

---

## 4. Typography

### 4.1 Typefaces

| Role        | Family               | Weights           | Source                                      |
|-------------|----------------------|-------------------|---------------------------------------------|
| **Display** | Libre Baskerville    | 400, 400i, 700    | Self-hosted WOFF2/WOFF (`/public/fonts/`)   |
| **Body**    | Inter                | 400               | Self-hosted WOFF2/WOFF (`/public/fonts/`)   |
| **System**  | System font stack    | (native)          | `-apple-system, BlinkMacSystemFont, Helvetica Neue, Arial, sans-serif` |

All fonts use `font-display: swap` to avoid flash of invisible text.

### 4.2 Type Scale

| Element               | Font Family         | Size     | Weight       | Style   | Tailwind Class                          |
|-----------------------|---------------------|----------|--------------|---------|-----------------------------------------|
| Page heading          | Libre Baskerville   | 32px     | 400 (normal) | Italic  | `text-[32px] font-normal italic font-baskerville` |
| Card title            | Inter               | 24px     | 600          | Normal  | `text-2xl font-semibold`                |
| Dialog title          | Inter               | 18px     | 600          | Normal  | `text-lg font-semibold`                 |
| Navigation link       | Inter               | 16px     | 400          | Normal  | `text-base font-normal`                 |
| Body text             | Inter               | 14px     | 400          | Normal  | `text-sm`                               |
| Label                 | Inter               | 14px     | 500          | Normal  | `text-sm font-medium`                   |
| Badge / caption       | Inter               | 12px     | 600          | Normal  | `text-xs font-semibold`                 |
| Small / helper text   | Inter               | 12px     | 400          | Normal  | `text-xs`                               |

### 4.3 Search Input

The main search input uses Libre Baskerville via the `.search-input` class, creating a distinctive editorial feel for the primary interaction point.

### 4.4 Text Wrapping

All headings (`h1`–`h6`) apply:
```css
overflow-wrap: break-word;
word-wrap: break-word;
word-break: break-word;
hyphens: auto;
```

---

## 5. Spacing & Layout

### 5.1 Spacing Scale

LegalVault uses the default Tailwind spacing scale (`4px` base unit) with one custom extension:

| Token | Value     | Usage                    |
|-------|-----------|--------------------------|
| `25`  | `6.25rem` | 100px — large section gap |

Common spacing values in use:
- `gap-2` (8px) — tight grouping (icon + label)
- `gap-3` (12px) — related items
- `gap-4` (16px) — standard section padding
- `gap-6` (24px) — section separation
- `space-y-8` (32px) — major content blocks

### 5.2 Page Layout

```
┌─────────────────────────────────────────────────┐
│  MainHeader (sticky, top-0, z-50, h-16)         │
│  ┌──────── max-w-[1440px] mx-auto ────────────┐ │
│  │ Logo        Nav Links       Icons  Profile  │ │
│  └─────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────┤
│                                                   │
│    ┌────── max-w-3xl mx-auto px-4 ────────┐     │
│    │                                        │     │
│    │         Page Content                   │     │
│    │                                        │     │
│    └────────────────────────────────────────┘     │
│                                                   │
│    Background: gradient (EFF2F5 → E3E7EB → D9DEE3) │
└─────────────────────────────────────────────────┘
```

### 5.3 Container Widths

| Context              | Max Width   | Tailwind             |
|----------------------|-------------|----------------------|
| Page shell           | 1440px      | `max-w-[1440px]`     |
| Content column       | 768px       | `max-w-3xl`          |
| Standard padding     | 16px        | `px-4`               |
| Header height        | 64px        | `h-16`               |

### 5.4 Navigation Structure

Four primary sections, evenly spaced:
1. **Workspace** — `/workspace`
2. **Library** — `/library`
3. **Research** — `/research` (primary feature)
4. **Paralegal** — `/paralegal`

Navigation uses `space-x-8` (32px gap) between items.

---

## 6. Border Radius & Elevation

### 6.1 Border Radius Scale

| Token | Value                          | Pixels | Usage                              |
|-------|--------------------------------|--------|------------------------------------|
| `sm`  | `calc(var(--radius) - 4px)`    | 4px    | Small elements, badges             |
| `md`  | `calc(var(--radius) - 2px)`    | 6px    | Buttons, inputs                    |
| `lg`  | `var(--radius)`                | 8px    | Cards, dialogs, alerts             |
| `xl`  | (Tailwind default)             | 12px   | Larger containers                  |
| `2xl` | (Tailwind default)             | 16px   | Search input, message bubbles      |
| `full`| 9999px                         | Pill   | Avatars, pill buttons, query chips |

### 6.2 Shadow Scale

| Level            | Value                                          | Usage                            |
|------------------|-------------------------------------------------|----------------------------------|
| `shadow-sm`      | Tailwind default                                | Cards, secondary buttons         |
| `shadow-md`      | Tailwind default                                | Dropdown menus                   |
| `shadow-lg`      | Tailwind default                                | Dialogs, modals                  |
| Input focus       | `0 0 10px rgba(0,0,0,0.05)`                   | Search input glow                |
| Header scroll     | `0 8px 32px rgba(0,0,0,0.02)`                 | Frosted header on scroll         |

### 6.3 Text Shadows (Specialty)

| Class           | Value                                     | Usage              |
|-----------------|-------------------------------------------|--------------------|
| `.text-shadow-sm`| `0px 4px 4px rgba(52, 52, 52, 0.25)`    | Emphasized overlay text |
| `.text-shadow-xs`| `0px 4px 4px rgba(52, 52, 52, 0.15)`    | Subtle overlay text |

---

## 7. Iconography

### 7.1 Libraries

| Library           | Version | Usage                            |
|-------------------|---------|----------------------------------|
| `lucide-react`    | 0.469   | Primary icon set (all UI icons)  |
| `@heroicons/react`| 2.2     | Supplementary icons              |

Lucide is the default choice. Heroicons should only be used when Lucide lacks a needed glyph.

### 7.2 Icon Sizes

| Size       | Tailwind      | Pixels | Usage                               |
|------------|---------------|--------|--------------------------------------|
| Small      | `h-3.5 w-3.5` | 14px   | Inline badges, compact indicators   |
| Default    | `h-4 w-4`     | 16px   | Buttons, menu items, inline icons   |
| Medium     | `h-5 w-5`     | 20px   | Standalone icons, nav items         |
| Large      | `h-6 w-6`     | 24px   | Header icons, feature icons         |

### 7.3 Icon Color

Icons generally inherit the text color of their context. Header icons use `stroke="#8992A9"` (Cold Grey) consistently. Icons inside active/selected states may switch to LV Lime or the foreground color.

### 7.4 Key Icons

| Icon           | Library  | Usage                         |
|----------------|----------|-------------------------------|
| `ArrowRight`   | Lucide   | Search submit, navigation CTA |
| `Gavel`        | Lucide   | Court cases category          |
| `BookText`     | Lucide   | Legislative category          |
| `Building2`    | Lucide   | Commercial category           |
| `Loader2`      | Lucide   | Loading spinner (`animate-spin`)|
| `AlertCircle`  | Lucide   | Error states                  |
| `X`            | Lucide   | Close / dismiss               |
| `Bookmark`     | Lucide   | Saved / featured indicators   |

---

## 8. Motion & Animation

Powered by **Framer Motion** (v11). All presets live in `src/lib/animations.ts`.

### 8.1 Transition Curves

| Name     | Definition                                      | Duration | Usage                      |
|----------|-------------------------------------------------|----------|----------------------------|
| `fast`   | `{ duration: 0.2 }`                             | 200ms    | Tooltips, micro-interactions|
| `normal` | `{ duration: 0.3 }`                             | 300ms    | Standard transitions       |
| `slow`   | `{ duration: 0.5 }`                             | 500ms    | Page-level entrances       |
| `spring` | `{ type: 'spring', stiffness: 300, damping: 30 }`| ~300ms | Bounce effects (badges)    |
| `smooth` | `{ duration: 0.8, ease: [0.04, 0.62, 0.23, 0.98] }` | 800ms | Hero/cinematic reveals  |

### 8.2 Animation Presets

| Preset           | Effect                           | Typical Use                     |
|------------------|----------------------------------|---------------------------------|
| `fadeIn`         | Opacity 0 → 1                   | Generic reveal                  |
| `fadeInUp`       | Opacity + Y 20px → 0            | Content blocks entering view    |
| `fadeInUpSmall`  | Opacity + Y 10px → 0            | Lighter content entry           |
| `fadeInDown`     | Opacity + Y -20px → 0           | Dropdown/overlay entry          |
| `slideInRight`   | Opacity + X 20px → 0            | Panel sliding in                |
| `slideInLeft`    | Opacity + X -20px → 0           | Reverse panel                   |
| `scaleIn`        | Opacity + Scale 0.95 → 1        | Dialogs, popovers               |
| `scaleInBounce`  | Opacity + Scale 0.5 → 1 (spring)| Celebratory / emphasis moments  |
| `expand`         | Height 0 → auto + Opacity       | Accordion / collapsible content |
| `popIn`          | Opacity + Y + Scale combined     | Chat message bubbles            |

### 8.3 Stagger Patterns

| Pattern    | Children Delay | Usage                    |
|------------|---------------|--------------------------|
| `list`     | 50ms          | Sequential list reveals  |
| `grid`     | 100ms         | Grid card entrances      |
| Custom     | Via `withStaggerIndex(preset, index)` | Fine control |

### 8.4 Scroll-Responsive Effects

The header performs a material transition on scroll:
- **Before scroll**: Fully transparent
- **After scroll (>10px)**: Frosted glass — `bg-white/25`, `backdrop-blur-2xl`, `backdrop-saturate-150`, subtle gradient and shadow

Transition duration: 300ms (`transition-all duration-300`).

---

## 9. Component Library

Built on **Radix UI** primitives, styled with **Tailwind CSS**, and varianted via **class-variance-authority (CVA)**.

### 9.1 Component Inventory

| Component       | Base              | Variants                                           |
|-----------------|-------------------|-----------------------------------------------------|
| **Button**      | HTML `<button>`   | default, destructive, outline, secondary, ghost, link × default, sm, lg, icon |
| **Input**       | HTML `<input>`    | Standard styling with focus ring                    |
| **Textarea**    | HTML `<textarea>` | Min-height 80px, auto-expanding                    |
| **Card**        | HTML `<div>`      | Header, Title, Description, Content, Footer slots  |
| **Badge**       | HTML `<div>`      | default, secondary, destructive, outline            |
| **Alert**       | HTML `<div>`      | default, destructive, success, warning, info        |
| **Dialog**      | Radix Dialog      | Overlay + Content + Close + Header/Footer           |
| **Tabs**        | Radix Tabs        | List, Trigger, Content                             |
| **Select**      | Radix Select      | Trigger, Content, Items with scroll                |
| **Checkbox**    | Radix Checkbox    | 4×4 with check icon                               |
| **Switch**      | Radix Switch      | 11×6 track with animated thumb                     |
| **Slider**      | Radix Slider      | Track height 2px                                   |
| **DropdownMenu**| Radix DropdownMenu| Full sub-menu, checkbox, radio support             |
| **HoverCard**   | Radix HoverCard   | Width 16rem, shadow-md                             |
| **ScrollArea**  | Radix ScrollArea  | Custom 2.5px thin scrollbar                        |
| **Tooltip**     | Radix Tooltip     | Standard positioning                               |
| **Progress**    | Radix Progress    | Height 4px, blue-400 indicator                     |
| **Avatar**      | Radix Avatar      | 10×10 with image + fallback                       |
| **Label**       | Radix Label       | 14px, weight 500                                   |
| **Skeleton**    | HTML `<div>`      | `animate-pulse` background                         |
| **BackButton**  | Custom            | Navigational back with customizable text           |
| **ExpandableBlock** | Custom        | Collapsible content section                        |

### 9.2 Button Variant Reference

```
┌──────────────┬──────────────────────────────────────────────────┐
│ Variant      │ Styling                                          │
├──────────────┼──────────────────────────────────────────────────┤
│ default      │ bg-primary, text-primary-fg, shadow, hover:90%   │
│ destructive  │ bg-destructive, shadow-sm, hover:90%             │
│ outline      │ border + bg-background, hover:accent             │
│ secondary    │ bg-secondary, shadow-sm, hover:80%               │
│ ghost        │ transparent, hover:accent                        │
│ link         │ text-primary, underline on hover                 │
├──────────────┼──────────────────────────────────────────────────┤
│ Size: sm     │ h-8, px-3, text-xs                               │
│ Size: default│ h-9, px-4, py-2                                  │
│ Size: lg     │ h-10, px-8                                       │
│ Size: icon   │ h-9 w-9 (square)                                │
└──────────────┴──────────────────────────────────────────────────┘
```

### 9.3 Shared Component Conventions

- **Disabled state**: `pointer-events-none opacity-50` (universal)
- **Focus ring**: `focus-visible:ring-1 focus-visible:ring-ring` on buttons; `focus-visible:ring-2 ring-offset-2` on inputs
- **All components** use `cn()` (a `clsx` + `twMerge` wrapper) for className composition
- **`asChild` pattern**: Buttons and some primitives support Radix `Slot` for composability

---

## 10. Surface & Material Effects

### 10.1 Frosted Glass

Used for the sticky header on research thread pages:

```css
background: rgba(255, 255, 255, 0.25);
backdrop-filter: blur(40px) saturate(1.5);
border-bottom: 1px solid rgba(255, 255, 255, 0.05);
box-shadow: 0 8px 32px rgba(0, 0, 0, 0.02);
background-image: linear-gradient(to bottom, rgba(255,255,255,0.3), rgba(255,255,255,0.2));
```

### 10.2 Auth Page Glass Card

The login card on the dark gradient background:

```css
background: rgba(255, 255, 255, 0.05);
border: 1px solid rgba(255, 255, 255, 0.1);
backdrop-filter: blur(extreme);
```

Input fields within auth use `bg-white/5` with `border-white/10`.

### 10.3 Opacity Layering System

LegalVault uses opacity-based layering for depth without heavy shadows:

| Layer           | Tailwind Classes                        |
|-----------------|-----------------------------------------|
| Surface subtle  | `bg-white/5`, `border-white/5`          |
| Surface light   | `bg-white/10`, `border-white/10`        |
| Surface medium  | `bg-white/25`                           |
| Surface strong  | `bg-white/30`                           |
| Hover overlay   | `hover:bg-black/5`                      |

---

## 11. Patterns & Conventions

### 11.1 Research Page Pattern

The research hub uses a **hero search** pattern:
1. Large italic serif heading (Libre Baskerville, 32px)
2. Full-width search input in a `rounded-2xl` card with soft shadow
3. Query type filter pills (Courts / Legislative / Commercial) — pill shape, LV Lime active state
4. Suggestion cards in a 3-column grid
5. Recent searches as a chronological list

### 11.2 Thread / Conversation Pattern

Research results use a **chat thread** layout:
1. Sticky frosted-glass header with back button + title + tabs
2. Messages centered in `max-w-3xl` container
3. User messages: right-aligned, blue (`#007AFF`) bubbles
4. AI messages: left-aligned, light gray (`#E9E9EB`) bubbles
5. Citations: numbered badges with LV Lime accent
6. Two tabs: "Answer" (conversation) and "Sources" (reference list)
7. Fixed-bottom input area

### 11.3 Card Pattern

Standard cards follow:
- White background, `rounded-lg`, `shadow-sm`, `border`
- `p-6` padding (via CardHeader/CardContent)
- Title in `text-2xl font-semibold`
- Optional description in `text-sm text-muted-foreground`

### 11.4 Form Pattern

- Labels: `text-sm font-medium` above inputs
- Inputs: `h-10` (40px) standard, `h-12` (48px) for prominent forms
- Error states: red border + red helper text below
- Submit buttons: full-width on auth pages, inline elsewhere
- Validation: disabled submit when input length < threshold

### 11.5 Empty & Loading States

- **Skeleton**: `animate-pulse` gray rectangles matching content shape
- **Spinner**: `Loader2` icon with `animate-spin`
- Empty states: centered text with muted foreground color

---

## 12. Dark Mode

### 12.1 Implementation

Dark mode uses class-based toggling (`darkMode: ['class']`). Adding `.dark` to the root `<html>` element activates the dark theme.

### 12.2 Dark Token Overrides

| Token                  | Light                 | Dark                   |
|------------------------|-----------------------|------------------------|
| `--background`         | `0 0% 100%`          | `222.2 84% 4.9%`      |
| `--foreground`         | `222.2 84% 4.9%`     | `210 40% 98%`         |
| `--primary`            | `222.2 47.4% 11.2%`  | `210 40% 98%`         |
| `--secondary`          | `210 40% 96.1%`      | `217.2 32.6% 17.5%`  |
| `--muted`              | `210 40% 96.1%`      | `217.2 32.6% 17.5%`  |
| `--muted-foreground`   | `215.4 16.3% 46.9%`  | `215 20.2% 65.1%`    |
| `--border`             | `214.3 31.8% 91.4%`  | `217.2 32.6% 17.5%`  |
| `--destructive`        | `0 84.2% 60.2%`      | `0 62.8% 30.6%`      |

### 12.3 Current Status

The dark mode token system is fully defined and component-ready. The application currently ships in **light mode by default**. No user-facing theme toggle exists yet. Alert variants include explicit `dark:` overrides (e.g., `dark:bg-red-950/10`).

---

## 13. Accessibility

### 13.1 Current Measures

- **Radix UI primitives** provide built-in ARIA roles, keyboard navigation, and focus management for all interactive components (dialogs, menus, tabs, checkboxes, etc.)
- **Focus rings**: visible `ring` styles on all interactive elements via `focus-visible:` pseudo-class
- **Semantic HTML**: alerts use `role="alert"`, headings follow hierarchy
- **Font sizing**: base size 14px (text-sm) with clear scale progression
- **Color contrast**: primary text (`#0B0F1A`) on white background exceeds WCAG AAA (21:1)

### 13.2 Guidelines for Contributors

- Always use Radix-based components for interactive elements — never build custom dropdowns, dialogs, or tabs from scratch
- Include `aria-label` on icon-only buttons
- Maintain focus trap within dialogs and menus
- Test keyboard navigation for all new interactive flows
- Ensure color is never the sole indicator of state — pair with icons or text

---

## 14. File Reference Map

| Concern                  | File Path                                 |
|--------------------------|-------------------------------------------|
| Tailwind configuration   | `frontend/tailwind.config.ts`             |
| CSS variables & globals  | `frontend/src/app/globals.css`            |
| Animation presets         | `frontend/src/lib/animations.ts`          |
| Utility functions (cn)   | `frontend/src/lib/utils.ts`               |
| UI primitives            | `frontend/src/components/ui/*.tsx`         |
| Main header / nav        | `frontend/src/components/ui/main-header.tsx` |
| Profile dropdown         | `frontend/src/components/ui/dropdown-profile-menu.tsx` |
| Logo asset               | `frontend/public/images/legalvault-logo.svg` |
| Self-hosted fonts        | `frontend/public/fonts/`                  |
| App layout (shell)       | `frontend/src/app/(app)/layout.tsx`       |
| Auth layout              | `frontend/src/app/(auth)/layout.tsx`      |

---

*This document should be updated as the design system evolves. When adding new components or modifying existing patterns, reflect those changes here to keep it as the authoritative design reference.*
