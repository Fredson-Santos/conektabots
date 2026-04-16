# Dashboard Layout Components

Professional SaaS dashboard layout system for ConektaBots, featuring responsive sidebar navigation, sticky header with breadcrumbs, and main content area.

## Components

### 1. **Sidebar** (`Sidebar.tsx`)

Left navigation with responsive behavior. Visible as fixed sidebar on desktop, drawer overlay on mobile.

#### Props

```typescript
interface SidebarProps {
  items: NavItem[]
  activeRoute?: string
  onItemClick?: (item: NavItem) => void
  isOpen?: boolean
  onClose?: () => void
}
```

#### Features

- **Desktop**: 240px fixed sidebar, always visible
- **Mobile**: Drawer overlay, slides in from left (z-50)
- **Active State**: Blue border + background highlight
- **Badges**: Optional count display (e.g., notifications)
- **Keyboard**: Escape to close drawer
- **Accessibility**: `aria-current="page"` on active item, semantic nav element

#### Usage

```tsx
import { Sidebar, navigationItems } from '@/app/components/layout'

<Sidebar
  items={navigationItems}
  isOpen={mobileDrawerOpen}
  onClose={() => setMobileDrawerOpen(false)}
/>
```

---

### 2. **Header** (`Header.tsx`)

Sticky top navigation bar with breadcrumbs, page title, and user menu.

#### Props

```typescript
interface HeaderProps {
  title?: string
  subtitle?: string
  breadcrumbs?: Breadcrumb[]
  user?: User
  onMobileMenuToggle?: () => void
  onLogout?: () => void
  actions?: React.ReactNode
}

interface Breadcrumb {
  label: string
  href?: string
}

interface User {
  name: string
  email: string
  avatar?: string
}
```

#### Features

- **Height**: 64px fixed
- **Breadcrumbs**: Responsive (hidden on mobile < 640px)
- **User Menu**: Dropdown with Settings + Logout
- **Keyboard**: Arrow keys navigate menu, Escape closes, Enter selects
- **Click Outside**: Closes dropdown automatically
- **Accessibility**: `aria-expanded`, `aria-haspopup` on dropdown button

#### Usage

```tsx
import { Header } from '@/app/components/layout'

<Header
  title="Bots Management"
  subtitle="View and manage your bots"
  breadcrumbs={[
    { label: 'Dashboard', href: '/dashboard' },
    { label: 'Bots' },
  ]}
  user={{
    name: 'John Doe',
    email: 'john@example.com',
  }}
  onMobileMenuToggle={() => setMenuOpen(!menuOpen)}
  onLogout={handleLogout}
/>
```

---

### 3. **DashboardLayout** (`DashboardLayout.tsx`)

Main container combining Sidebar, Header, and content area. Handles mobile drawer management.

#### Props

```typescript
interface DashboardLayoutProps {
  children: React.ReactNode
  sidebarItems?: NavItem[]
  title?: string
  subtitle?: string
  breadcrumbs?: Breadcrumb[]
  user?: User
  actions?: React.ReactNode
  onLogout?: () => void
}
```

#### Features

- **Responsive Grid**: Desktop sidebar + header + content
- **Mobile**: Single column with drawer navigation
- **Content Scrolling**: Main area scrolls independently, header sticky
- **Background**: Light gray (gray-50) for visual separation
- **Padding**: 24px desktop, 16px mobile (8px grid)
- **Layout**: pt-16 (header space), md:ml-60 (sidebar space)

#### Usage

```tsx
import { DashboardLayout, navigationItems } from '@/app/components/layout'

export default function BotsPage() {
  return (
    <DashboardLayout
      sidebarItems={navigationItems}
      title="Bots Management"
      breadcrumbs={[
        { label: 'Dashboard', href: '/dashboard' },
        { label: 'Bots' },
      ]}
      user={{
        name: 'John Doe',
        email: 'john@example.com',
      }}
      onLogout={() => router.push('/login')}
    >
      {/* Your page content here */}
      <div className="space-y-6">
        <h2 className="text-2xl font-bold">Bots</h2>
        {/* Page content */}
      </div>
    </DashboardLayout>
  )
}
```

---

## Navigation Items

Defined in `constants.ts`:

```typescript
export const navigationItems: NavItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    href: '/dashboard',
    icon: 'home',
  },
  {
    id: 'bots',
    label: 'Bots',
    href: '/dashboard/bots',
    icon: 'sparkles',
  },
  {
    id: 'marketplaces',
    label: 'Marketplaces',
    href: '/dashboard/marketplaces',
    icon: 'shopping-cart',
  },
  {
    id: 'settings',
    label: 'Settings',
    href: '/dashboard/settings',
    icon: 'cog-6-tooth',
  },
]
```

### Adding Navigation Badges

Pass badge count to show notifications:

```typescript
const navItems: NavItem[] = [
  {
    ...navigationItems[1],
    badge: 3, // Shows "3" in gray badge
  },
]
```

---

## Responsive Breakpoints

| Breakpoint | Sidebar | Menu | Header |
|------------|---------|------|--------|
| Mobile (<640px) | Hidden drawer | Hamburger | Title only |
| Tablet (640-1024px) | Hidden/drawer | Hamburger | Breadcrumbs + Title |
| Desktop (1024px+) | Fixed 240px | Visible | Full breadcrumbs |

---

## Styling Details

### Colors

- **Sidebar Background**: White (`bg-white`)
- **Sidebar Border**: Gray 200 (`border-gray-200`)
- **Active Item**: Blue 50 background + Blue 500 border + Blue 600 text
- **Hover**: Gray 100 background
- **Header**: White with bottom border
- **Main Background**: Gray 50 (`bg-gray-50`)

### Spacing (8px Grid)

- **Logo Height**: 40px (py-5 = 20px from 8px base)
- **Nav Item Padding**: 12px (px-3 = 12px, py-3 = 12px)
- **Gap Between Items**: 8px (space-y-1)
- **Header Height**: 64px (h-16)
- **Sidebar Width**: 240px (w-60)
- **Content Padding**: 24px on desktop (px-8), 16px on mobile (px-4)

### Typography

- **Logo**: 16px font, bold weight 700
- **Nav Label**: 14px font, medium weight 500
- **Header Title**: 18px font, semibold weight 600
- **Breadcrumb**: 14px font, regular weight 400

### Shadows & Borders

- **Borders**: 1px solid gray-200 (subtle dividers)
- **Dropdown Shadow**: `shadow-lg` (10px 15px -3px)
- **Focus Ring**: 2px blue-500 with offset 2px

---

## Keyboard Navigation

### Desktop

- **Tab**: Cycle through nav items
- **Enter**: Navigate to item href
- **Focus Visible**: Blue ring around focused elements

### Mobile Drawer

- **Escape**: Close drawer
- **Tab**: Cycle through nav items in drawer
- **Enter**: Navigate to item, auto-close drawer

### Header Dropdown

- **Click**: Toggle menu open/closed
- **Arrow Down**: Focus logout button
- **Escape**: Close menu
- **Tab**: Cycle through menu items

---

## Accessibility

- ✅ Semantic HTML: `<nav>`, `<header>`, `<main>`, `<aside>` elements
- ✅ ARIA Labels: `aria-label`, `aria-expanded`, `aria-current="page"`
- ✅ Focus Management: Visible focus rings on buttons/links
- ✅ Keyboard Navigation: Full support (Tab, Enter, Escape, Arrow keys)
- ✅ Screen Readers: Proper heading hierarchy, button labels
- ✅ Color Contrast: WCAG AA compliant (4.5:1 for text)

---

## Customization

### Changing Colors

Edit Tailwind config or use default classes:

```tsx
// Active state color
className="bg-blue-50 border-blue-500"  // Change to your primary color

// Hover state
className="hover:bg-gray-100"           // Adjust hover tone
```

### Changing Sidebar Width

```tsx
// Sidebar.tsx
<aside className="w-60">  {/* Change to w-52, w-64, etc */}
  {/* ... */}
</aside>
```

### Adding Menu Sections

Extend `NavItem` interface:

```typescript
interface NavItem {
  // ... existing props
  section?: string     // "Main", "Admin", etc
  separator?: boolean  // Show divider before item
}
```

---

## Common Patterns

### Page with Actions Button

```tsx
<DashboardLayout
  title="Bots"
  actions={
    <Button variant="primary" size="sm">
      + New Bot
    </Button>
  }
>
  {/* Content */}
</DashboardLayout>
```

### Page without Sidebar (Full Width)

```tsx
// Don't use DashboardLayout, use Header only
<Header title="Login" />
<main className="pt-16">
  {/* Full-width content */}
</main>
```

### Dynamic Active Route

```tsx
// DashboardLayout automatically uses usePathname() for active state
// No need to pass activeRoute unless you're overriding
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Drawer doesn't close | Ensure `onClose` callback is connected to drawer state |
| Header overlapping content | Add `pt-16` to main content container |
| Sidebar not visible on mobile | Check `isOpen` state and hamburger click handler |
| User menu not keyboard accessible | Verify arrow key handlers in Header.tsx |
| Wrong active item highlighted | Check that `href` matches current route exactly |

---

## Testing Checklist

- [ ] Sidebar shows all 4 nav items
- [ ] Active item highlighted correctly (blue border + bg)
- [ ] Desktop sidebar visible, mobile drawer hidden by default
- [ ] Hamburger menu opens drawer
- [ ] Escape closes drawer
- [ ] Click outside drawer closes it
- [ ] Header breadcrumbs clickable and responsive
- [ ] User menu dropdown opens/closes on click
- [ ] User menu keyboard accessible (arrow keys, escape)
- [ ] Content scrolls independently of header
- [ ] Mobile responsive at 320px, 768px, 1024px
- [ ] No console errors or warnings
- [ ] Tab navigation cycles through elements
- [ ] Focus rings visible on all interactive elements
- [ ] Active route persists after page reload

---

## Files

```
app/components/layout/
├── Sidebar.tsx            – Navigation sidebar
├── Header.tsx             – Top navigation with breadcrumbs
├── DashboardLayout.tsx    – Main layout container
├── constants.ts           – Navigation items definition
├── index.ts               – Central exports
└── README.md (this file)
```

---

## Version

- **Version**: 1.0
- **Framework**: Next.js 15 + TypeScript + Tailwind CSS
- **Icons**: Heroicons outline
- **Last Updated**: April 2026
