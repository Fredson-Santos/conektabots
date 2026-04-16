# Bots Management CRUD - Module Documentation

## Overview

Complete CRUD interface for managing Telegram bots in the ConektaBots dashboard. This module handles all bot lifecycle operations: create, read, update, delete, and status management with a responsive UI and robust error handling.

## Architecture

### Component Structure

```
app/(dashboard)/bots/
├── page.tsx                          # Main page orchestrator
├── hooks/
│   └── useBots.ts                   # Custom hook - API + state management
└── components/
    ├── BotsTable.tsx                # Data table display + pagination
    ├── BotForm.tsx                  # Form for create/edit
    ├── CreateBotModal.tsx           # Modal wrapper for form
    └── DeleteConfirmationModal.tsx  # Deletion confirmation
```

### Data Flow

```
Page (page.tsx)
  ├─ useBots hook (state + API)
  │  └─ getApi() [lib/api.ts] - Axios with auth interceptors
  ├─ BotsTable (display)
  ├─ CreateBotModal (create/edit)
  └─ DeleteConfirmationModal (delete)
```

## Components

### `page.tsx` - Main Page

**Responsibilities:**
- Orchestrate all components
- Manage modal states (create/edit/delete)
- Handle user actions (create, edit, delete, toggle, paginate)
- Call appropriate hook methods

**State Management:**
```typescript
- isCreateModalOpen: boolean
- editingBot: Bot | null (null = create mode, Bot = edit mode)
- deleteBot_modal: Bot | null
- isSubmitting: boolean
- isDeletingBot: boolean
```

**Key Methods:**
- `handleCreateBot()` - Create new bot
- `handleUpdateBot()` - Update existing bot
- `handleDeleteBot()` - Delete bot
- `handleToggleBotStatus()` - Toggle active/inactive
- `handlePageChange()` - Navigate pagination
- `handleEditBot()` - Open edit modal
- `handleCloseModal()` - Close create/edit modal

### `hooks/useBots.ts` - Custom Hook

**Exposes:**
```typescript
interface UseBotsReturn {
  // State
  bots: Bot[]
  loading: boolean
  error: string | null
  totalPages: number
  currentPage: number
  pageSize: number
  
  // Operations (async)
  fetchBots(page, pageSize): Promise<void>
  createBot(data): Promise<Bot>
  updateBot(id, data): Promise<Bot>
  deleteBot(id): Promise<void>
  toggleBotStatus(id, ativo): Promise<Bot>
  refetch(): Promise<void>
}
```

**API Calls:**
```
GET    /api/v1/bots?page=1&page_size=20      ← List bots
POST   /api/v1/bots                          ← Create bot
PATCH  /api/v1/bots/{id}                     ← Update bot
DELETE /api/v1/bots/{id}                     ← Delete bot
PATCH  /api/v1/bots/{id} {ativo:!current}    ← Toggle status
```

**Error Handling:**
- Try/catch wraps all API calls
- User-friendly error messages
- Network errors → state.error
- 401 Unauthorized → automatic token refresh (axios interceptor)

### `components/BotsTable.tsx` - Data Table

**Props:**
```typescript
interface BotsTableProps {
  bots: Bot[]
  loading: boolean
  onEdit: (bot: Bot) => void
  onDelete: (bot: Bot) => void
  onToggleStatus: (bot: Bot) => Promise<void>
  currentPage: number
  totalPages: number
  pageSize: number
  onPageChange: (page: number) => void
}
```

**Features:**
- **Desktop View**: Full data table with 5 columns
  - Bot Name, API ID, Status (toggle), Created Date, Actions (Edit/Delete)
  - Striped rows (alternating bg-white and bg-gray-50)
  - Hover effect for interactivity
  
- **Mobile View**: Card layout
  - Name, API ID at top
  - Status toggle inline
  - Responsive action buttons
  - Created date below

- **Pagination**: Shows when > 1 page
  - Previous/Next buttons with disabled states
  - Page indicator "Page X of Y"
  - Item count display

- **States**:
  - Loading: Skeleton placeholders
  - Empty: Helpful message + create button
  - Data: Full table with all interactions

### `components/BotForm.tsx` - Create/Edit Form

**Props:**
```typescript
interface BotFormProps {
  bot?: Bot | null          // null = create, Bot = edit
  onSubmit: (data) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
}
```

**Fields:**
1. **Bot Name** - text input
   - Validation: 2-50 characters, required
   - Error: "Bot name is required" or "Must be 2-50 characters"

2. **API ID** - text input
   - Validation: required
   - Error: "API ID is required"

3. **API Hash** - text input
   - Validation: required
   - Error: "API Hash is required"

4. **Phone Number** - tel input
   - Validation: required
   - Error: "Phone number is required"

**Validation:**
- Client-side before submit
- Real-time error clearing as user types
- Submit button disabled if errors exist
- Form shows green border on valid fields

**Styling:**
- Error state: red border, red background, red error text
- Valid state: blue focus ring
- Disabled state: gray background with cursor-not-allowed

### `components/CreateBotModal.tsx` - Modal Wrapper

**Props:**
```typescript
interface CreateBotModalProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (data) => Promise<void>
  bot?: Bot | null
  isLoading?: boolean
}
```

**Features:**
- Centered fixed modal on top of page
- Backdrop with blur effect (can click to close)
- Sticky header with title and close button
- Form content with scroll support for small screens
- Dynamic title: "Create New Bot" or "Edit Bot: {name}"

### `components/DeleteConfirmationModal.tsx` - Delete Confirmation

**Props:**
```typescript
interface DeleteConfirmationModalProps {
  isOpen: boolean
  bot: Bot | null
  isLoading?: boolean
  onConfirm: () => Promise<void>
  onCancel: () => void
}
```

**Features:**
- Red-themed warning dialog
- Shows bot name: "Are you sure you want to delete 'BotName'?"
- Warning banner with risk explanation
- Two buttons: Cancel (gray) and Delete Bot (red)
- Loading state during deletion

## Interfaces & Types

### Bot
```typescript
interface Bot {
  id: string              // UUID
  nome: string            // Bot name
  api_id: string          // Telegram API ID
  api_hash?: string       // Telegram API Hash (encrypted server-side)
  telefone?: string       // Phone number used for login
  ativo: boolean          // Active/inactive status
  criado_em: string       // ISO timestamp
  tenant_id: string       // Multi-tenant isolation
}
```

### BotCreateInput
```typescript
interface BotCreateInput {
  nome: string
  api_id: string
  api_hash: string
  telefone: string
}
```

## Styling & Design

### Design System
- **Primary Color**: Blue (#2563eb) from Tailwind
- **Secondary**: Gray scale for text and borders
- **Status Colors**: Green (active), Gray (inactive)
- **Alert Colors**: Red (delete/errors), Yellow (warnings)

### Tailwind Classes
- Tables: border-collapse, striped rows, hover effects
- Modals: fixed positioning, backdrop blur, z-50 stacking
- Forms: consistent input styling, error states, disabled states
- Buttons: blue primary, gray secondary, red destructive

### Responsive Breakpoints
- **Mobile (< 768px)**: Card layout, vertical stacked
- **Tablet (768px - 1024px)**: Hybrid approach
- **Desktop (> 1024px)**: Full table, side-by-side layouts

## Error Handling

### API Errors
```typescript
try {
  await createBot(data)
} catch (err) {
  // Error message stored in state.error
  // User sees friendly message in alert
  // Specific error details logged to console
}
```

### Validation Errors
```typescript
const errors: FormErrors = {
  nome?: string         // Field-level validation error
  api_id?: string
  api_hash?: string
  telefone?: string
}
// Displayed inline under each field
// Real-time clearing as user types
```

### Network Errors
- 5xx errors → "Failed to [action]. Please try again."
- Connection timeouts → Messages from axios error object
- Automatic retry possible via page refresh or refetch button

## Usage Examples

### Basic Usage
```typescript
// In page.tsx
const {
  bots,
  loading,
  fetchBots,
  createBot,
  updateBot,
  deleteBot,
  toggleBotStatus,
} = useBots()

// Fetch on mount
useEffect(() => {
  fetchBots(1, 20) // page, pageSize
}, [])

// Create bot
const handleCreate = async (data: BotCreateInput) => {
  const newBot = await createBot(data)
  // Modal closes, list refreshes
}

// Edit bot
const handleEdit = async (id: string, data: BotCreateInput) => {
  await updateBot(id, data)
  // List updates with new data
}

// Delete bot
const handleDelete = async (id: string) => {
  await deleteBot(id)
  // Bot removed from list
}

// Toggle status
const handleToggle = async (id: string, currentStatus: boolean) => {
  await toggleBotStatus(id, currentStatus)
  // Status flipped: active → inactive or vice versa
}
```

## Testing Checklist

- [ ] Load page: List displays with first 20 bots
- [ ] Click "Create Bot": Modal opens with empty form
- [ ] Fill form validation: Errors show for empty/invalid fields
- [ ] Submit valid form: POST succeeds, modal closes, list refreshes
- [ ] Pagination: Previous/Next buttons navigate pages
- [ ] Click Edit: Modal opens with pre-filled bot data
- [ ] Update bot: PATCH succeeds, table updates
- [ ] Click toggle: Active/inactive switches immediately
- [ ] Click Delete: Confirmation modal appears
- [ ] Confirm delete: Bot removed from list
- [ ] Network error: User-friendly error message displayed
- [ ] Mobile view: Card layout renders correctly
- [ ] Keyboard nav: Tab through form fields, submit with Enter
- [ ] Loading states: Skeletons show while fetching

## Performance Considerations

- **Pagination**: Limits API payload → only 20 items per page
- **Lazy Rendering**: Components only mount when needed
- **Optimistic Updates**: (Future) Update UI before API response
- **Memoization**: useCallback for handler functions to prevent re-renders
- **Error Boundary**: (Future) Add error boundary for crash handling

## Security Notes

- **Multi-tenant Isolation**: All queries filter by tenant_id
- **RBAC**: Backend validates user permissions for each action
- **Token Refresh**: Axios interceptors handle 401 → automatic refresh
- **Input Validation**: Client-side validation + server-side validation
- **Encrypted Fields**: API Hash encrypted server-side, never exposed in responses
- **Soft Deletes**: Bots marked as deleted, not hard-deleted from DB

## Future Enhancements

1. **Search/Filter**: Filter bots by name (client-side)
2. **Inline Editing**: Edit fields directly in table (UX experiment)
3. **Bulk Operations**: Select multiple bots, perform batch actions
4. **Export**: Export bot list as CSV
5. **Sorting**: Click headers to sort by name, date, status
6. **Caching**: Cache bots list in React Query or similar
7. **Optimization**: Virtual scrolling for large lists
8. **Analytics**: Show bot performance metrics

## Troubleshooting

### Bots not loading
- Check network tab: Is GET /api/v1/bots being called?
- Check browser console: Any error messages?
- Verify JWT token in localStorage
- Check backend logs for 401 or 500 errors

### Form validation not working
- Check browser console for JavaScript errors
- Verify form state is updating (DevTools React extension)
- Check field change handlers are firing

### Modal not closing after submit
- Check if API call succeeded (network tab)
- Verify onSubmit callback calls onClose()
- Check for errors preventing state update

### Status toggle not working
- Check network PATCH request in network tab
- Verify server returns updated bot with new ativo value
- Check console for API errors

## Related Files

- `/lib/api.ts` - Axios instance with auth interceptors
- `/lib/auth.ts` - JWT token management
- `/lib/constants.ts` - API_URL and ENDPOINTS
- `/components/dashboard/StatCard.tsx` - Reusable stat component
- `/components/AuthForm.tsx` - Form components (InputField, FormButton)
- `/app/(dashboard)/layout.tsx` - Dashboard layout wrapper

## Code Style

- **TypeScript**: Strict mode, full type hints
- **React**: Functional components with hooks
- **CSS**: Tailwind with semantic class names
- **Naming**: camelCase for variables/functions, PascalCase for components
- **Comments**: JSDoc for complex logic, inline for "why" not "what"
- **Props**: Interface for each component's props
- **Error Messages**: User-friendly, actionable text

## References

- [React Hooks Documentation](https://react.dev/reference/react)
- [Axios Documentation](https://axios-http.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Next.js Client Components](https://nextjs.org/docs/getting-started/react-essentials#client-components)
