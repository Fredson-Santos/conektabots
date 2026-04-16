---
name: "Modern SaaS Design System"
description: "Professional, minimalist SaaS dashboard design patterns inspired by Stripe, Linear, and Vercel. Use when: building UI components, refactoring existing interfaces, designing dashboards, creating consistent design systems, ensuring premium visual quality."
applyTo: "frontend/**/*.tsx"
version: "1.0"
---

# 🎨 Modern SaaS Design System & Implementation Guide

This skill provides design patterns and implementation guidelines for building premium SaaS interfaces that match industry leaders like Stripe, Linear, and Vercel.

---

## 1️⃣ Design Philosophy

### Core Principles

- **Minimalism**: Remove everything unnecessary. Every element must serve a purpose.
- **Hierarchy**: Clear visual distinction between primary actions, secondary actions, and supporting information.
- **Breathing Room**: Use whitespace strategically. Don't overcrowd the interface.
- **Premium Feel**: Clean, modern, professional. No gradients, no animations unless purposeful.
- **Consistency**: Follow the grid system and spacing rules everywhere.
- **Accessibility**: WCAG compliant, keyboard navigation supported, sufficient contrast ratios.

### What to Remove Immediately
- ❌ Emojis (unprofessional for SaaS)
- ❌ Cartoon illustrations
- ❌ Bright gradient backgrounds
- ❌ Drop shadows on every element
- ❌ Overly rounded corners (use subtlety)
- ❌ Loading skeletons with animations
- ❌ Unnecessary decorative elements

### What to Adopt
- ✅ Clean typography (Inter, SF Pro, Helvetica Neue)
- ✅ Neutral color palette with one primary accent
- ✅ 8px grid system for spacing and alignment
- ✅ Subtle borders instead of shadows
- ✅ Outline/stroke icons (Heroicons, Lucide style)
- ✅ Generous whitespace
- ✅ Clear visual feedback (hover, active, disabled states)

---

## 2️⃣ Color System

### Primary Palette

```
Neutral Colors (Always available):
- White:        #FFFFFF
- Gray 50:      #F9FAFB
- Gray 100:     #F3F4F6
- Gray 200:     #E5E7EB
- Gray 300:     #D1D5DB
- Gray 400:     #9CA3AF
- Gray 500:     #6B7280
- Gray 600:     #4B5563
- Gray 700:     #374151
- Gray 800:     #1F2937
- Gray 900:     #111827
- Black:        #000000

Primary Accent (Brand):
- Blue 500:     #2563EB  (Primary action, active states)
- Blue 600:     #1D4ED8  (Hover on buttons)
- Blue 50:      #EFF6FF  (Background for alerts/highlights)
- Blue 100:     #DBEAFE  (Border for focus states)

Semantic Colors:
- Success:      #10B981  (Green)
- Warning:      #F59E0B  (Amber)
- Danger:       #EF4444  (Red)
- Info:         #0EA5E9  (Cyan)
```

### Tailwind CSS Configuration

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#EFF6FF',
          100: '#DBEAFE',
          500: '#2563EB',
          600: '#1D4ED8',
          700: '#1E40AF',
        },
        success: '#10B981',
        warning: '#F59E0B',
        danger: '#EF4444',
      },
      spacing: {
        'xs': '4px',    // 8px grid (half)
        'sm': '8px',    // 8px grid
        'md': '16px',   // 8px grid (2x)
        'lg': '24px',   // 8px grid (3x)
        'xl': '32px',   // 8px grid (4x)
        '2xl': '48px',  // 8px grid (6x)
      },
      borderRadius: {
        'sm': '4px',
        'md': '6px',
        'lg': '8px',
        'xl': '12px',
      },
      fontSize: {
        'xs': ['12px', { lineHeight: '16px' }],
        'sm': ['14px', { lineHeight: '20px' }],
        'base': ['16px', { lineHeight: '24px' }],
        'lg': ['18px', { lineHeight: '28px' }],
        'xl': ['20px', { lineHeight: '28px' }],
      },
      boxShadow: {
        'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
      },
    },
  },
}
```

### Usage Rules

- **Gray for text**: Gray 700 (primary text), Gray 500 (secondary), Gray 400 (disabled)
- **Blue for actions**: Button, links, active states
- **Color sparingly**: Use accent color for ~20% of elements
- **Semantic colors only for status**: Success = green, danger = red (no other use)

---

## 3️⃣ Typography System

### Font Stack

```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
```

### Type Scales

| Size | Purpose | Tailwind Class |
|------|---------|-----------------|
| 12px | Small labels, captions | `text-xs` |
| 14px | Body copy, form labels | `text-sm` |
| 16px | Primary body text | `text-base` |
| 18px | Subsection headings | `text-lg` |
| 20px | Section headings | `text-xl` |
| 24px | Page titles | `text-2xl` |
| 32px | Major headings | `text-4xl` |

### Font Weights

```
Light:      300  (Rarely used, only for emphasis)
Regular:    400  (Default body text)
Medium:     500  (Labels, group headings)
Semibold:   600  (Strong emphasis, section titles)
Bold:       700  (Page titles, CTAs)
```

### Usage Examples

```jsx
// Page Title
<h1 className="text-4xl font-bold text-gray-900">Bots Management</h1>

// Section Heading
<h2 className="text-xl font-semibold text-gray-800">Recent Activity</h2>

// Body Text
<p className="text-base text-gray-700">Description of the feature or action</p>

// Label
<label className="text-sm font-medium text-gray-600">Email Address</label>

// Secondary Text
<span className="text-sm text-gray-500">Last updated 2 minutes ago</span>
```

---

## 4️⃣ Spacing & Grid System

### 8px Grid System

All spacing follows multiples of 8px:

```
4px  = xs (half grid)
8px  = sm
16px = md
24px = lg
32px = xl
48px = 2xl
64px = 3xl
```

### Application

```jsx
// Vertical spacing between elements
<div className="mb-md">First element</div>  {/* 16px margin-bottom */}
<div>Second element</div>

// Padding inside containers
<div className="p-lg">                     {/* 24px padding all sides */}
  Content here
</div>

// Horizontal spacing in flex layouts
<div className="flex gap-md">               {/* 16px gap between items */}
  <Item />
  <Item />
</div>

// Combinations
<div className="px-lg py-md">               {/* 24px horizontal, 16px vertical */}
  Form content
</div>
```

### Layout Patterns

**Card spacing**:
```jsx
<div className="p-lg space-y-lg">           {/* 16px gap between elements */}
  <div>Header</div>
  <div>Content</div>
  <div>Footer</div>
</div>
```

**Section spacing**:
```jsx
<div className="space-y-2xl">               {/* 48px between sections */}
  <Section />
  <Section />
  <Section />
</div>
```

---

## 5️⃣ Component Patterns

### 5a) Buttons

**Hierarchy**: Primary (Main action) > Secondary (Alternative) > Tertiary (Lower priority)

```jsx
// PRIMARY BUTTON (Strong action)
<button className="px-sm py-sm bg-primary-500 text-white font-medium text-sm rounded-md hover:bg-primary-600 transition-colors">
  Create Bot
</button>

// SECONDARY BUTTON (Alternative action)
<button className="px-sm py-sm bg-gray-100 text-gray-900 font-medium text-sm rounded-md hover:bg-gray-200 transition-colors border border-gray-200">
  Cancel
</button>

// TERTIARY BUTTON (Low priority, text-only)
<button className="px-sm py-sm text-primary-500 font-medium text-sm hover:text-primary-600 hover:bg-primary-50 rounded-md transition-colors">
  Learn More
</button>

// DANGER BUTTON
<button className="px-sm py-sm bg-red-600 text-white font-medium text-sm rounded-md hover:bg-red-700">
  Delete
</button>

// DISABLED STATE
<button disabled className="px-sm py-sm bg-gray-100 text-gray-400 font-medium text-sm rounded-md cursor-not-allowed">
  Disabled
</button>
```

**Component Interface**:

```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'tertiary' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  fullWidth?: boolean
  disabled?: boolean
  loading?: boolean
  icon?: React.ReactNode
  children: React.ReactNode
  onClick?: () => void
}
```

### 5b) Form Inputs

```jsx
// TEXT INPUT
<input
  type="text"
  placeholder="Enter your email"
  className="w-full px-md py-sm border border-gray-200 rounded-md text-gray-900 placeholder-gray-400 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 transition-all"
/>

// WITH LABEL & ERROR
<div className="space-y-sm">
  <label className="text-sm font-medium text-gray-700">Email Address</label>
  <input
    type="email"
    className="w-full px-md py-sm border border-red-300 rounded-md text-gray-900 bg-red-50 focus:outline-none focus:border-red-500"
  />
  <p className="text-xs text-red-600">Email is required</p>
</div>

// TEXTAREA
<textarea
  placeholder="Describe your issue"
  className="w-full px-md py-sm border border-gray-200 rounded-md text-gray-900 focus:outline-none focus:border-primary-500 resize-none"
  rows={5}
/>

// SELECT
<select className="w-full px-md py-sm border border-gray-200 rounded-md text-gray-900 focus:outline-none focus:border-primary-500">
  <option>Select an option</option>
  <option>Option 1</option>
</select>

// CHECKBOX
<input
  type="checkbox"
  className="w-4 h-4 border border-gray-300 rounded accent-primary-500"
/>

// RADIO
<input
  type="radio"
  className="w-4 h-4 accent-primary-500"
/>
```

### 5c) Cards

```jsx
// SIMPLE CARD (with subtle border)
<div className="bg-white border border-gray-200 rounded-lg p-lg">
  <h3 className="text-lg font-semibold text-gray-900">Card Title</h3>
  <p className="text-sm text-gray-600 mt-sm">Card content goes here</p>
</div>

// CARD WITH DIVIDED SECTIONS
<div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
  <div className="border-b border-gray-200 p-lg">
    <h3 className="text-lg font-semibold text-gray-900">Title</h3>
  </div>
  <div className="p-lg">
    <p className="text-sm text-gray-600">Content here</p>
  </div>
  <div className="bg-gray-50 border-t border-gray-200 p-lg flex gap-sm">
    <button className="...">Action</button>
  </div>
</div>

// METRIC CARD (Compact)
<div className="bg-white border border-gray-200 rounded-lg p-lg">
  <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Metric Name</p>
  <p className="text-4xl font-bold text-gray-900 mt-md">1,234</p>
  <p className="text-xs text-gray-500 mt-sm">↑ 12% from last month</p>
</div>
```

### 5d) Alerts & Status Messages

```jsx
// SUCCESS ALERT
<div className="bg-green-50 border border-green-200 rounded-lg p-md">
  <div className="flex gap-md">
    <CheckCircleIcon className="w-5 h-5 text-green-600 flex-shrink-0" />
    <div>
      <h4 className="font-semibold text-green-900">Success!</h4>
      <p className="text-sm text-green-800 mt-xs">Your changes have been saved.</p>
    </div>
  </div>
</div>

// ERROR ALERT
<div className="bg-red-50 border border-red-200 rounded-lg p-md">
  <div className="flex gap-md">
    <XCircleIcon className="w-5 h-5 text-red-600 flex-shrink-0" />
    <div>
      <h4 className="font-semibold text-red-900">Error</h4>
      <p className="text-sm text-red-800 mt-xs">Something went wrong. Please try again.</p>
    </div>
  </div>
</div>

// WARNING ALERT
<div className="bg-amber-50 border border-amber-200 rounded-lg p-md">
  <div className="flex gap-md">
    <ExclamationIcon className="w-5 h-5 text-amber-600 flex-shrink-0" />
    <div>
      <h4 className="font-semibold text-amber-900">Warning</h4>
      <p className="text-sm text-amber-800 mt-xs">This action cannot be undone.</p>
    </div>
  </div>
</div>

// INFO ALERT
<div className="bg-blue-50 border border-blue-200 rounded-lg p-md">
  <div className="flex gap-md">
    <InfoIcon className="w-5 h-5 text-blue-600 flex-shrink-0" />
    <div>
      <h4 className="font-semibold text-blue-900">Info</h4>
      <p className="text-sm text-blue-800 mt-xs">New features available in settings.</p>
    </div>
  </div>
</div>
```

### 5e) Empty States

```jsx
// EMPTY STATE
<div className="flex flex-col items-center justify-center py-2xl px-lg text-center">
  <InboxIcon className="w-12 h-12 text-gray-400 mb-lg" />
  <h3 className="text-lg font-semibold text-gray-900">No bots yet</h3>
  <p className="text-sm text-gray-600 mt-sm max-w-sm">
    Create your first bot to get started with telegram automation.
  </p>
  <button className="mt-lg px-md py-sm bg-primary-500 text-white font-medium text-sm rounded-md hover:bg-primary-600">
    Create First Bot
  </button>
</div>
```

### 5f) Loading States

```jsx
// SKELETON (Subtle, no animation)
<div className="bg-gray-200 rounded-md h-12 w-full" />

// LOADING SPINNER (Minimal)
<div className="animate-spin w-5 h-5 border-2 border-gray-300 border-t-primary-500 rounded-full" />

// LOADING TEXT
<p className="text-sm text-gray-500">Loading...</p>
```

---

## 6️⃣ Layout Patterns

### 6a) Sidebar Navigation

```jsx
<div className="flex h-screen bg-white">
  {/* SIDEBAR */}
  <nav className="w-64 border-r border-gray-200 p-lg">
    {/* Logo */}
    <div className="mb-2xl">
      <h1 className="text-xl font-bold text-gray-900">ConektaBots</h1>
    </div>

    {/* Navigation Items */}
    <div className="space-y-sm">
      <NavItem icon={<DashboardIcon />} label="Dashboard" active />
      <NavItem icon={<BotsIcon />} label="Bots" />
      <NavItem icon={<SettingsIcon />} label="Settings" />
    </div>
  </nav>

  {/* MAIN CONTENT */}
  <main className="flex-1 bg-gray-50 overflow-auto">
    {/* Header */}
    <div className="border-b border-gray-200 bg-white px-2xl py-lg flex items-center justify-between">
      <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
      <UserMenu />
    </div>

    {/* Content */}
    <div className="p-2xl">
      {/* Page content */}
    </div>
  </main>
</div>
```

### 6b) Header with Breadcrumbs

```jsx
<div className="bg-white border-b border-gray-200 px-2xl py-lg">
  <div className="flex items-center gap-sm mb-lg">
    <a href="/" className="text-sm text-primary-500 hover:text-primary-600">Dashboard</a>
    <ChevronRightIcon className="w-4 h-4 text-gray-400" />
    <span className="text-sm text-gray-600">Bots</span>
  </div>
  <h1 className="text-4xl font-bold text-gray-900">Bots Management</h1>
</div>
```

### 6c) Table with Hover States

```jsx
<div className="border border-gray-200 rounded-lg overflow-hidden">
  <table className="w-full">
    <thead className="bg-gray-50 border-b border-gray-200">
      <tr>
        <th className="px-lg py-md text-left text-sm font-semibold text-gray-900">Name</th>
        <th className="px-lg py-md text-left text-sm font-semibold text-gray-900">Status</th>
        <th className="px-lg py-md text-right text-sm font-semibold text-gray-900">Actions</th>
      </tr>
    </thead>
    <tbody className="divide-y divide-gray-200">
      {items.map((item) => (
        <tr key={item.id} className="hover:bg-gray-50 transition-colors">
          <td className="px-lg py-md text-sm text-gray-900">{item.name}</td>
          <td className="px-lg py-md text-sm"><Badge>{item.status}</Badge></td>
          <td className="px-lg py-md text-right flex gap-sm justify-end">
            <IconButton icon={<EditIcon />} />
            <IconButton icon={<DeleteIcon />} />
          </td>
        </tr>
      ))}
    </tbody>
  </table>
</div>
```

### 6d) Modal Dialog

```jsx
<div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
  <div className="bg-white rounded-lg max-w-md w-full mx-4">
    {/* Header */}
    <div className="border-b border-gray-200 p-lg">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">Dialog Title</h2>
        <button className="text-gray-400 hover:text-gray-600">
          <XIcon className="w-5 h-5" />
        </button>
      </div>
    </div>

    {/* Content */}
    <div className="p-lg space-y-lg">
      <p className="text-sm text-gray-600">Dialog content here</p>
    </div>

    {/* Footer */}
    <div className="border-t border-gray-200 p-lg flex gap-sm justify-end">
      <button className="...">Cancel</button>
      <button className="...">Confirm</button>
    </div>
  </div>
</div>
```

---

## 7️⃣ Icon Usage

### Icon System

- **Source**: Heroicons (official) or Lucide Icons (lightweight alternative)
- **Size**: Use consistent sizes (16px, 20px, 24px, 32px)
- **Stroke**: Always use `stroke-current` or fixed width (1.5-2px)
- **Color**: Inherit text color or set explicitly

```jsx
// Import
import { BeakerIcon } from '@heroicons/react/24/outline'

// Usage
<BeakerIcon className="w-5 h-5 text-gray-500" />

// Icon Button
<button className="p-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition">
  <SettingsIcon className="w-5 h-5" />
</button>

// With Text
<div className="flex items-center gap-sm">
  <CheckIcon className="w-5 h-5 text-green-600" />
  <span className="text-sm text-gray-900">Active</span>
</div>
```

---

## 8️⃣ Interaction & State Design

### Hover States

```jsx
// Button
"hover:bg-primary-600 transition-colors"

// Link
"hover:text-primary-600 hover:underline"

// Card
"hover:border-gray-300 hover:shadow-md transition-all"

// Row
"hover:bg-gray-50 transition-colors"
```

### Focus States (Keyboard)

```jsx
"focus:outline-none focus:ring-2 focus:ring-offset-0 focus:ring-primary-500"
```

### Active/Selected States

```jsx
// Active nav item
"border-l-4 border-primary-500 bg-primary-50"

// Active tab
"border-b-2 border-primary-500 text-primary-600"
```

### Disabled States

```jsx
"disabled:opacity-50 disabled:cursor-not-allowed"
```

### Loading States

```jsx
"animate-pulse opacity-50"
```

---

## 9️⃣ Responsive Design

### Breakpoints

```
sm:  640px   (Mobile)
md:  768px   (Tablet)
lg:  1024px  (Desktop)
xl:  1280px  (Large Desktop)
2xl: 1536px  (Very Large)
```

### Mobile-First Approach

```jsx
// Stack vertically on mobile, grid on desktop
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-lg">
  <Card />
  <Card />
  <Card />
</div>

// Hide on mobile, show on larger screens
<div className="hidden lg:block">
  Sidebar navigation
</div>

// Adjust padding
<div className="p-md md:p-lg lg:p-2xl">
  Content
</div>
```

### Mobile Navigation

```jsx
// Desktop: Fixed sidebar
// Mobile: Collapsible hamburger menu
<div className="flex">
  <nav className="hidden md:block w-64 border-r border-gray-200">
    {/* Desktop nav */}
  </nav>
  <main className="flex-1">
    <div className="md:hidden flex items-center p-lg border-b border-gray-200">
      <button><MenuIcon /></button>
    </div>
  </main>
</div>
```

---

## 🔟 Component Best Practices

### Do's ✅

- Use semantic HTML (`<button>`, `<input>`, `<nav>`)
- Ensure all interactive elements are keyboard accessible
- Use `aria-label` for icon-only buttons
- Maintain consistent spacing and sizing
- Use TypeScript interfaces for all components
- Test hover, focus, and active states
- Keep components composable and reusable
- Use Tailwind CSS utilities (not custom CSS)

### Don'ts ❌

- Don't use `<div>` for buttons (use `<button>`)
- Don't forget focus states (keyboard users)
- Don't break the grid system
- Don't use inconsistent spacing
- Don't add animations without purpose
- Don't use magic numbers in spacing/sizing
- Don't nest too many components (keep it flat)

---

## 1️⃣1️⃣ Implementation Checklist

**Before Calling a Component Complete**:

- [ ] All states are styled (default, hover, focus, active, disabled, loading)
- [ ] Typography is consistent with scale
- [ ] Spacing follows 8px grid system
- [ ] Colors match palette (no random colors)
- [ ] Icons are from approved library (Heroicons/Lucide)
- [ ] Responsive at all breakpoints (mobile, tablet, desktop)
- [ ] Keyboard accessible (Tab, Enter, Escape)
- [ ] No emojis or unauthorized characters
- [ ] TypeScript types are defined
- [ ] Component is exported and documented

---

## 1️⃣2️⃣ Example: Complete Component (Reference)

```typescript
'use client'

import React from 'react'
import { CheckIcon, ExclamationIcon } from '@heroicons/react/24/outline'

interface StatusBadgeProps {
  status: 'active' | 'inactive' | 'error'
  label: string
}

/**
 * StatusBadge - Displays current status with visual indicator
 * 
 * @param status - Status type (active | inactive | error)
 * @param label - Text label for the status
 */
export function StatusBadge({ status, label }: StatusBadgeProps) {
  const styles = {
    active: 'bg-green-50 text-green-700 border border-green-200',
    inactive: 'bg-gray-100 text-gray-700 border border-gray-200',
    error: 'bg-red-50 text-red-700 border border-red-200',
  }

  const icons = {
    active: <CheckIcon className="w-4 h-4" />,
    inactive: null,
    error: <ExclamationIcon className="w-4 h-4" />,
  }

  return (
    <span className={`inline-flex items-center gap-sm px-md py-sm rounded-md text-sm font-medium ${styles[status]}`}>
      {icons[status]}
      {label}
    </span>
  )
}
```

---

## Summary Table

| Aspect | SaaS Standard | Avoid |
|--------|---------------|-------|
| **Colors** | Neutral + 1 accent | Rainbow, gradients |
| **Typography** | Inter, 400/500/600/700 weight | Comic Sans, all caps |
| **Spacing** | 8px grid multiples | Random values |
| **Icons** | Outline, consistent size | Mixed styles, emojis |
| **Shadows** | Subtle, purposeful | Heavy drop shadows |
| **Rounded** | 4-12px, subtle | 50% (too round) |
| **States** | Clear hover/focus/active | No visual feedback |
| **Empty states** | Helpful, centered | Blank screen |
| **Responsive** | Mobile-first | Desktop-only |

---

**These patterns are proven effective across enterprise SaaS platforms. Consistency across all components creates a cohesive, premium user experience.**
