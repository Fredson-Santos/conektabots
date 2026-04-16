# 📦 ConektaBots Component Library

**Version**: 1.0.0  
**Total Components**: 60+  
**Status**: Specification Ready for Development

---

## 📋 Table of Contents

- [Atomic Components](#atomic-components)
- [Form Components](#form-components)
- [Data Display Components](#data-display-components)
- [Navigation Components](#navigation-components)
- [Feedback Components](#feedback-components)
- [Layout Components](#layout-components)

---

## Atomic Components

### Button

**Purpose**: Primary interactive element for user actions

**Variants**:
```tsx
// Primary - main action
<Button variant="primary">Save Changes</Button>

// Secondary - alternative action
<Button variant="secondary">Cancel</Button>

// Danger - destructive action
<Button variant="danger">Delete</Button>

// Ghost - minimal style
<Button variant="ghost">Learn More</Button>

// Loading - async operation
<Button variant="primary" isLoading>Processing...</Button>
```

**Props Interface**:
```tsx
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  isLoading?: boolean;
  isDisabled?: boolean;
  fullWidth?: boolean;
  children: React.ReactNode;
}
```

**States**:
| State | Appearance | Cursor |
|-------|-----------|--------|
| Default | Base color, shadow-sm | pointer |
| Hover | 1px translate-up, shadow | pointer |
| Active | Pressed visual | pointer |
| Focus | 2px blue outline ring | pointer |
| Disabled | Gray-300 bg, gray text | not-allowed |
| Loading | Spinner overlay, disabled | default |

**Accessibility**:
- ✅ Keyboard focus ring visible (2px blue)
- ✅ `aria-disabled` when disabled
- ✅ `aria-loading` when loading
- ✅ Text color ensures 7:1 contrast

**Usage Examples**:
```jsx
// Primary action with icon
<Button variant="primary" icon={<SaveIcon />} iconPosition="left">
  Save Changes
</Button>

// Danger button with confirmation
<Button variant="danger" isDisabled={!confirmed}>
  Delete Permanently
</Button>

// Full-width mobile button
<Button fullWidth className="md:w-auto">
  Continue
</Button>
```

---

### Input

**Purpose**: Text entry field with validation states

**Variants**:
```tsx
// Text input
<Input type="text" placeholder="Enter bot name" />

// Email input
<Input type="email" placeholder="your@email.com" />

// Password input
<Input type="password" placeholder="••••••••" />

// Number input
<Input type="number" placeholder="0" min="0" max="100" />

// Readonly input
<Input value="Read-only value" readOnly />
```

**Props Interface**:
```tsx
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
  icon?: React.ReactNode;
  isLoading?: boolean;
  size?: 'sm' | 'md' | 'lg';
  state?: 'default' | 'error' | 'success';
}
```

**States**:
| State | Border | Background | Notes |
|-------|--------|-----------|-------|
| Default | Gray-300 | White | Normal input |
| Focused | Blue-500 | White + shadow | 2px blue ring |
| Error | Red-500 | Red-50 | Error message below |
| Success | Green-500 | Green-50 | Check icon |
| Disabled | Gray-200 | Gray-100 | Cursor disabled |

**Accessibility**:
- ✅ `<label>` associated via `htmlFor`
- ✅ Focus ring 2px blue
- ✅ Error text linked via `aria-describedby`
- ✅ Success icon with `aria-label`

**Usage Examples**:
```jsx
// With label and validation
<Input
  label="Email Address"
  type="email"
  state={email.isValid ? 'success' : 'error'}
  error={email.error}
  hint="We'll never share your email"
  onChange={handleEmailChange}
/>

// Search input with icon
<Input
  icon={<MagnifyingGlassIcon />}
  placeholder="Search bots..."
  type="search"
/>
```

---

### Select / Dropdown

**Purpose**: Choose single option from list

**Props Interface**:
```tsx
interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  hint?: string;
  options: Array<{ value: string; label: string }>;
  size?: 'sm' | 'md' | 'lg';
}
```

**Usage**:
```jsx
<Select
  label="Select Marketplace"
  options={[
    { value: 'shopee', label: 'Shopee' },
    { value: 'mercadolivre', label: 'Mercado Livre' },
    { value: 'amazon', label: 'Amazon' }
  ]}
  value={selectedMarketplace}
  onChange={handleMarketplaceSelect}
/>
```

**Accessibility**:
- ✅ Keyboard navigation (Arrow keys, Enter)
- ✅ Screen reader announces options
- ✅ Focus indicator visible

---

### Checkbox

**Purpose**: Binary choice (on/off)

**Props Interface**:
```tsx
interface CheckboxProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  size?: 'sm' | 'md' | 'lg';
  indeterminate?: boolean;
}
```

**States**:
```tsx
// Unchecked
<Checkbox label="Remember me" />

// Checked
<Checkbox label="Enable notifications" defaultChecked />

// Indeterminate (partial selection)
<Checkbox label="Select all items" indeterminate />

// Disabled
<Checkbox label="Already active" disabled />
```

**Accessibility**:
- ✅ Keyboard space-bar to toggle
- ✅ Focus ring visible
- ✅ Screen reader announces state

---

### Radio

**Purpose**: Single choice from mutually exclusive options

**Props Interface**:
```tsx
interface RadioGroupProps {
  name: string;
  label?: string;
  options: Array<{ value: string; label: string }>;
  value?: string;
  onChange: (value: string) => void;
  error?: string;
}

interface RadioProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
}
```

**Usage**:
```jsx
<RadioGroup
  name="schedule-frequency"
  label="How often should this rule run?"
  options={[
    { value: 'realtime', label: 'Real-time (immediate)' },
    { value: 'hourly', label: 'Hourly' },
    { value: 'daily', label: 'Daily at 3 AM' }
  ]}
  value={frequency}
  onChange={setFrequency}
/>
```

---

### Toggle Switch

**Purpose**: On/off switch (alternative to checkbox)

**Props Interface**:
```tsx
interface ToggleSwitchProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  description?: string;
  size?: 'sm' | 'md' | 'lg';
}
```

**Usage**:
```jsx
<ToggleSwitch
  label="Enable auto-reply"
  description="Automatically respond to messages when offline"
  checked={autoReplyEnabled}
  onChange={handleAutoReplyToggle}
/>
```

**States**:
- Off: Gray background, toggle on left
- On: Blue background, toggle on right
- Disabled: Gray background with reduced opacity

---

### Badge

**Purpose**: Label, tag, or status indicator

**Props Interface**:
```tsx
interface BadgeProps {
  variant?: 'primary' | 'secondary' | 'success' | 'danger' | 'warning';
  size?: 'sm' | 'md' | 'lg';
  icon?: React.ReactNode;
  children: React.ReactNode;
  onRemove?: () => void;
}
```

**Variants**:
```jsx
// Status badges
<Badge variant="success">Active</Badge>
<Badge variant="danger">Paused</Badge>
<Badge variant="warning">Processing</Badge>

// With icon
<Badge variant="primary" icon={<CheckIcon />}>Completed</Badge>

// Removable (tag-like)
<Badge variant="secondary" onRemove={() => removeTag()}>
  react
</Badge>
```

**Usage**:
| Variant | Background | Text | Use Case |
|---------|-----------|------|----------|
| primary | Blue-100 | Blue-900 | Neutral info |
| secondary | Gray-200 | Gray-900 | Secondary |
| success | Green-100 | Green-900 | Success/Active |
| danger | Red-100 | Red-900 | Error/Danger |
| warning | Orange-100 | Orange-900 | Warning/Caution |

---

### Label

**Purpose**: Form field label with required indicator

**Props Interface**:
```tsx
interface LabelProps extends React.LabelHTMLAttributes<HTMLLabelElement> {
  required?: boolean;
  htmlFor: string;
  children: React.ReactNode;
}
```

**Usage**:
```jsx
<Label htmlFor="bot-name" required>
  Bot Name
</Label>
<Input id="bot-name" placeholder="My Bot" />
```

---

### Helper Text & Error Message

**Purpose**: Contextual information and validation feedback

**Props Interface**:
```tsx
interface HelperTextProps {
  children: React.ReactNode;
  type?: 'default' | 'error' | 'success' | 'warning';
  icon?: React.ReactNode;
}
```

**Usage**:
```jsx
// Helper text
<HelperText type="default">
  Use lowercase letters and numbers only
</HelperText>

// Error text
<HelperText type="error" icon={<ExclamationIcon />}>
  This bot name is already in use
</HelperText>

// Success text
<HelperText type="success" icon={<CheckIcon />}>
  Bot name is available
</HelperText>
```

---

## Form Components

### FormGroup

**Purpose**: Container combining label, input, and validation

**Props Interface**:
```tsx
interface FormGroupProps {
  label: string;
  required?: boolean;
  error?: string;
  hint?: string;
  children: React.ReactNode; // Input component
}
```

**Usage**:
```jsx
<FormGroup
  label="Bot Name"
  required
  error={errors.name}
  hint="Unique identifier for this bot"
>
  <Input
    placeholder="Enter bot name"
    value={formData.name}
    onChange={handleNameChange}
  />
</FormGroup>
```

---

### DatePicker

**Purpose**: Select single date with calendar UI

**Props Interface**:
```tsx
interface DatePickerProps {
  label?: string;
  value?: Date;
  onChange: (date: Date) => void;
  minDate?: Date;
  maxDate?: Date;
  error?: string;
}
```

**Usage**:
```jsx
<DatePicker
  label="Schedule Start Date"
  value={startDate}
  onChange={setStartDate}
  minDate={new Date()}
/>
```

---

### TimePicker

**Purpose**: Select time (hours, minutes, optional seconds)

**Props Interface**:
```tsx
interface TimePickerProps {
  label?: string;
  value?: string; // "14:30"
  onChange: (time: string) => void;
  format?: '12h' | '24h';
  error?: string;
}
```

**Usage**:
```jsx
<TimePicker
  label="Send at"
  value={sendTime}
  onChange={setSendTime}
  format="24h"
/>
```

---

### TextArea

**Purpose**: Multi-line text input

**Props Interface**:
```tsx
interface TextAreaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  hint?: string;
  maxLength?: number;
  showCharacterCount?: boolean;
  minRows?: number;
  maxRows?: number;
}
```

**Usage**:
```jsx
<TextArea
  label="Auto-reply Message"
  placeholder="Enter your auto-reply message..."
  maxLength={500}
  showCharacterCount
  minRows={4}
  value={message}
  onChange={handleMessageChange}
/>
```

---

### FileUpload

**Purpose**: Upload file(s) with drag-and-drop

**Props Interface**:
```tsx
interface FileUploadProps {
  label?: string;
  accept?: string; // ".csv,.json,.xlsx"
  maxSize?: number; // bytes
  multiple?: boolean;
  onUpload: (files: File[]) => void;
  error?: string;
}
```

**Usage**:
```jsx
<FileUpload
  label="Import Bot Rules"
  accept=".csv,.json"
  maxSize={5242880} // 5MB
  onUpload={handleFileUpload}
/>
```

**States**:
- Default: Dashed border, upload icon
- Drag-over: Blue border, highlight background
- Upload in progress: Spinner
- Error: Red border, error message

---

### SearchInput

**Purpose**: Search field with debounce and results

**Props Interface**:
```tsx
interface SearchInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  debounceMs?: number; // default 300
  onSearch: (query: string) => void;
  onResult?: React.ReactNode; // Custom results display
  isLoading?: boolean;
}
```

**Usage**:
```jsx
<SearchInput
  placeholder="Search bots..."
  debounceMs={300}
  onSearch={handleSearch}
  isLoading={isSearching}
/>
```

---

### MultiSelect

**Purpose**: Select multiple options from list

**Props Interface**:
```tsx
interface MultiSelectProps {
  label?: string;
  options: Array<{ value: string; label: string }>;
  value?: string[];
  onChange: (values: string[]) => void;
  error?: string;
  searchable?: boolean;
  placeholder?: string;
}
```

**Usage**:
```jsx
<MultiSelect
  label="Select Marketplaces"
  options={marketplaceOptions}
  value={selectedMarketplaces}
  onChange={setSelectedMarketplaces}
  searchable
  placeholder="Choose marketplaces..."
/>
```

---

## Data Display Components

### Table

**Purpose**: Display tabular data with sorting and pagination

**Props Interface**:
```tsx
interface TableProps<T> {
  columns: Array<{
    key: string;
    label: string;
    sortable?: boolean;
    render?: (value: any, row: T) => React.ReactNode;
  }>;
  data: T[];
  onSort?: (key: string, direction: 'asc' | 'desc') => void;
  pagination?: {
    page: number;
    pageSize: number;
    total: number;
    onPageChange: (page: number) => void;
  };
  isLoading?: boolean;
  emptyMessage?: string;
]
```

**Usage**:
```jsx
<Table
  columns={[
    { key: 'name', label: 'Bot Name', sortable: true },
    { key: 'status', label: 'Status', sortable: false },
    { key: 'actions', label: 'Actions', render: (_, row) => <Actions bot={row} /> }
  ]}
  data={bots}
  pagination={paginationState}
  onSort={handleSort}
  isLoading={isLoading}
/>
```

---

### Card

**Purpose**: Container for content grouping

**Props Interface**:
```tsx
interface CardProps {
  variant?: 'default' | 'elevated' | 'outline';
  padding?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  header?: React.ReactNode;
  footer?: React.ReactNode;
  onClick?: () => void;
  isHoverable?: boolean;
}
```

**Usage**:
```jsx
<Card header={<h3>Bot Statistics</h3>} padding="lg">
  <div className="space-y-4">
    {/* Content */}
  </div>
</Card>
```

---

### List / ListItem

**Purpose**: Vertical list of items, often with actions

**Props Interface**:
```tsx
interface ListProps {
  items: Array<{ id: string; [key: string]: any }>;
  renderItem: (item: any) => React.ReactNode;
  divider?: boolean;
  spacing?: 'sm' | 'md' | 'lg';
  emptyMessage?: string;
}

interface ListItemProps {
  icon?: React.ReactNode;
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
  onClick?: () => void;
  selected?: boolean;
}
```

**Usage**:
```jsx
<List items={bots} spacing="md">
  {(bot) => (
    <ListItem
      icon={<RobotIcon />}
      title={bot.name}
      subtitle={bot.status}
      action={<EditButton />}
      onClick={() => selectBot(bot.id)}
    />
  )}
</List>
```

---

### Avatar

**Purpose**: User or entity profile picture

**Props Interface**:
```tsx
interface AvatarProps {
  src?: string;
  initials?: string;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  status?: 'active' | 'inactive' | 'away';
  alt?: string;
}
```

**Usage**:
```jsx
// With image
<Avatar src="https://..." alt="John Doe" size="md" />

// With initials fallback
<Avatar initials="JD" size="md" />

// With status
<Avatar src="..." size="lg" status="active" />
```

---

### AvatarGroup

**Purpose**: Display multiple avatars (commonly for teams)

**Props Interface**:
```tsx
interface AvatarGroupProps {
  avatars: Array<{ src?: string; initials: string }>;
  max?: number; // Show first N, "+X more"
  size?: 'sm' | 'md' | 'lg';
  onClick?: () => void;
}
```

**Usage**:
```jsx
<AvatarGroup
  avatars={[
    { src: 'user1.jpg', initials: 'JD' },
    { src: 'user2.jpg', initials: 'SM' }
  ]}
  max={3}
  size="sm"
/>
```

---

### Progress Bar

**Purpose**: Show completion percentage

**Props Interface**:
```tsx
interface ProgressBarProps {
  value: number; // 0-100
  label?: string;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'success' | 'warning' | 'danger';
  showPercentage?: boolean;
}
```

**Usage**:
```jsx
<ProgressBar
  value={65}
  label="Rule Processing"
  showPercentage
  size="md"
/>
```

---

### Stat Block

**Purpose**: Display metric with label (dashboard card)

**Props Interface**:
```tsx
interface StatBlockProps {
  value: string | number;
  label: string;
  icon?: React.ReactNode;
  trend?: { value: number; direction: 'up' | 'down' };
  onClick?: () => void;
}
```

**Usage**:
```jsx
<StatBlock
  value={1234}
  label="Messages Sent"
  icon={<CheckIcon />}
  trend={{ value: 12, direction: 'up' }}
/>
```

---

### Timeline

**Purpose**: Show chronological sequence of events

**Props Interface**:
```tsx
interface TimelineProps {
  items: Array<{
    id: string;
    timestamp: Date;
    title: string;
    description?: string;
    icon?: React.ReactNode;
    status?: 'completed' | 'pending' | 'failed';
  }>;
}
```

**Usage**:
```jsx
<Timeline
  items={[
    {
      timestamp: new Date(),
      title: 'Bot activated',
      status: 'completed'
    },
    {
      timestamp: new Date(),
      title: 'Rule #1 executed',
      status: 'completed'
    }
  ]}
/>
```

---

### Breadcrumb

**Purpose**: Navigation hierarchy showing current location

**Props Interface**:
```tsx
interface BreadcrumbProps {
  items: Array<{ label: string; href?: string }>;
  separator?: React.ReactNode;
  onClick?: (href: string) => void;
}
```

**Usage**:
```jsx
<Breadcrumb
  items={[
    { label: 'Dashboard', href: '/' },
    { label: 'Bots', href: '/bots' },
    { label: 'My Bot' }
  ]}
/>
```

---

## Navigation Components

### Navbar / Header

**Purpose**: Top navigation bar with logo, menu, user profile

**Props Interface**:
```tsx
interface NavbarProps {
  logo?: React.ReactNode;
  title?: string;
  menu?: React.ReactNode;
  rightActions?: React.ReactNode; // Profile, notifications
  sticky?: boolean;
}
```

**Usage**:
```jsx
<Navbar
  logo={<ConektaBotsLogo />}
  menu={<NavMenu items={menuItems} />}
  rightActions={
    <>
      <NotificationBell />
      <UserProfile />
    </>
  }
  sticky
/>
```

---

### Sidebar / Navigation Menu

**Purpose**: Vertical navigation menu (collapsible on mobile)

**Props Interface**:
```tsx
interface SidebarProps {
  items: Array<{
    id: string;
    label: string;
    icon: React.ReactNode;
    href: string;
    children?: Array<...>; // Sub-menu
  }>;
  collapsed?: boolean;
  onItemSelect?: (id: string) => void;
  activeItemId?: string;
}
```

**Usage**:
```jsx
<Sidebar
  items={menuItems}
  activeItemId={currentPage}
  collapsed={isMobileOpen ? false : true}
/>
```

---

### Tabs

**Purpose**: Switch between content sections

**Props Interface**:
```tsx
interface TabsProps {
  tabs: Array<{ id: string; label: string; icon?: React.ReactNode }>;
  activeTabId: string;
  onTabChange: (id: string) => void;
  variant?: 'horizontal' | 'vertical';
  children: React.ReactNode; // Tab content
}
```

**Usage**:
```jsx
<Tabs
  tabs={[
    { id: 'details', label: 'Details' },
    { id: 'settings', label: 'Settings' },
    { id: 'history', label: 'History' }
  ]}
  activeTabId={activeTab}
  onTabChange={setActiveTab}
>
  {activeTab === 'details' && <DetailsTab />}
  {activeTab === 'settings' && <SettingsTab />}
  {activeTab === 'history' && <HistoryTab />}
</Tabs>
```

---

### Pagination

**Purpose**: Navigate through pages of data

**Props Interface**:
```tsx
interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  pageSize?: number;
  totalItems?: number;
  showJumpToPage?: boolean;
}
```

**Usage**:
```jsx
<Pagination
  currentPage={page}
  totalPages={Math.ceil(total / pageSize)}
  onPageChange={setPage}
  totalItems={total}
/>
```

---

### Stepper

**Purpose**: Multi-step form or process wizard

**Props Interface**:
```tsx
interface StepperProps {
  steps: Array<{
    id: string;
    label: string;
    description?: string;
  }>;
  activeStepId: string;
  onStepChange?: (id: string) => void;
  completed?: string[];
  hasErrors?: string[];
}
```

**Usage**:
```jsx
<Stepper
  steps={[
    { id: 'basic', label: 'Basic Info' },
    { id: 'rules', label: 'Create Rules' },
    { id: 'review', label: 'Review' }
  ]}
  activeStepId={currentStep}
  onStepChange={setCurrentStep}
/>
```

---

## Feedback Components

### Alert / Toast

**Purpose**: Brief notification message

**Props Interface**:
```tsx
interface AlertProps {
  variant?: 'default' | 'success' | 'error' | 'warning' | 'info';
  title?: string;
  message: string;
  action?: React.ReactNode; // CTA button
  onClose?: () => void;
  autoCloseDuration?: number; // milliseconds
  icon?: React.ReactNode;
}
```

**Usage**:
```jsx
// Alert in page
<Alert
  variant="success"
  title="Bot Created"
  message="Your bot is now active and ready to use"
/>

// Toast notification
<Toast
  variant="error"
  message="Failed to save settings"
  autoCloseDuration={5000}
  onClose={dismissToast}
/>
```

---

### Modal / Dialog

**Purpose**: Modal dialog for confirmations and critical content

**Props Interface**:
```tsx
interface ModalProps {
  isOpen: boolean;
  title: string;
  children: React.ReactNode;
  onClose: () => void;
  actions?: React.ReactNode; // Footer buttons
  size?: 'sm' | 'md' | 'lg';
  closeOnBackdropClick?: boolean;
  closeOnEscape?: boolean;
}
```

**Usage**:
```jsx
<Modal
  isOpen={isDeleteConfirmOpen}
  title="Delete Bot?"
  onClose={closeModal}
  size="sm"
  actions={
    <>
      <Button variant="secondary" onClick={closeModal}>
        Cancel
      </Button>
      <Button variant="danger" onClick={handleDelete}>
        Delete
      </Button>
    </>
  }
>
  <p>This action cannot be undone. All rules and history will be deleted.</p>
</Modal>
```

---

### Drawer / Sidebar Panel

**Purpose**: Off-canvas panel for additional content

**Props Interface**:
```tsx
interface DrawerProps {
  isOpen: boolean;
  title: string;
  children: React.ReactNode;
  onClose: () => void;
  position?: 'left' | 'right';
  size?: 'sm' | 'md' | 'lg';
}
```

**Usage**:
```jsx
<Drawer
  isOpen={isFilterPanelOpen}
  title="Filters"
  position="right"
  size="md"
  onClose={closeFilterPanel}
>
  {/* Filter components */}
</Drawer>
```

---

### Tooltip

**Purpose**: Contextual help text on hover

**Props Interface**:
```tsx
interface TooltipProps {
  content: React.ReactNode;
  position?: 'top' | 'right' | 'bottom' | 'left';
  delay?: number; // milliseconds
  children: React.ReactNode;
}
```

**Usage**:
```jsx
<Tooltip content="Click to expand details" position="top">
  <button>ℹ️</button>
</Tooltip>
```

---

### Popover

**Purpose**: Small overlay with content (more complex than tooltip)

**Props Interface**:
```tsx
interface PopoverProps {
  trigger: React.ReactNode;
  content: React.ReactNode;
  position?: 'top' | 'right' | 'bottom' | 'left';
  onClose?: () => void;
  closeOnClickOutside?: boolean;
}
```

**Usage**:
```jsx
<Popover
  trigger={<HelpIcon />}
  content={<HelpGuide />}
  position="right"
  closeOnClickOutside
/>
```

---

### Loading Skeleton

**Purpose**: Placeholder while loading content

**Props Interface**:
```tsx
interface SkeletonProps {
  type?: 'text' | 'card' | 'avatar' | 'line' | 'circle';
  width?: string | number;
  height?: string | number;
  count?: number;
  animation?: 'pulse' | 'shimmer';
}
```

**Usage**:
```jsx
{isLoading ? (
  <Skeleton type="card" height={200} count={3} animation="pulse" />
) : (
  <CardList items={items} />
)}
```

---

### Empty State

**Purpose**: Message when no data to display

**Props Interface**:
```tsx
interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode; // CTA button
}
```

**Usage**:
```jsx
{bots.length === 0 ? (
  <EmptyState
    icon={<RobotIcon />}
    title="No bots created yet"
    description="Create your first bot to get started"
    action={<Button variant="primary">Create Bot</Button>}
  />
) : (
  <BotList bots={bots} />
)}
```

---

### Error Boundary

**Purpose**: Catch and display React errors gracefully

**Props Interface**:
```tsx
interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}
```

**Usage**:
```jsx
<ErrorBoundary
  onError={(error, info) => logErrorToService(error, info)}
  fallback={<ErrorFallback />}
>
  <ComplexComponent />
</ErrorBoundary>
```

---

## Layout Components

### Container / Wrapper

**Purpose**: Max-width page wrapper with responsive padding

**Props Interface**:
```tsx
interface ContainerProps {
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '7xl';
  padding?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
}
```

**Usage**:
```jsx
<Container maxWidth="lg" padding="lg">
  <h1>Page Title</h1>
  {/* Content */}
</Container>
```

---

### Grid System

**Purpose**: 12-column responsive grid (Tailwind-based)

**Patterns**:
```jsx
// 3 equal columns, stack on mobile
<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
  <Card>Col 1</Card>
  <Card>Col 2</Card>
  <Card>Col 3</Card>
</div>

// 2-1 layout
<div className="grid grid-cols-1 md:grid-cols-3 gap-6">
  <div className="md:col-span-2">Main content</div>
  <aside>Sidebar</aside>
</div>

// Auto-fit cards
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
  {items.map(item => <Card key={item.id} {...item} />)}
</div>
```

---

### Flex Utilities

**Purpose**: Flexible layouts with Tailwind flex classes

**Common Patterns**:
```jsx
// Center content
<div className="flex items-center justify-center h-screen">
  <Spinner />
</div>

// Space between (header layout)
<div className="flex items-center justify-between">
  <Logo />
  <Nav />
  <UserMenu />
</div>

// Column with gap
<div className="flex flex-col gap-4">
  <Input />
  <Input />
  <Button>Submit</Button>
</div>

// Responsive flex direction
<div className="flex flex-col md:flex-row gap-6">
  <Sidebar className="w-full md:w-64" />
  <main className="flex-1">Main content</main>
</div>
```

---

### Dashboard Layout

**Purpose**: Standard app layout (sidebar + header + main content)

**Structure**:
```jsx
<div className="flex flex-col h-screen">
  {/* Navbar */}
  <Navbar sticky />
  
  <div className="flex flex-1 overflow-hidden">
    {/* Sidebar */}
    <Sidebar className="w-64 hidden md:block" />
    
    {/* Main Content */}
    <main className="flex-1 overflow-auto bg-gray-50 dark:bg-gray-950">
      <Container maxWidth="7xl" padding="lg">
        {children}
      </Container>
    </main>
  </div>
</div>
```

---

### Form Layout

**Purpose**: Responsive form with 1-2 column layouts

**Pattern - Stacked (mobile) → 2 columns (desktop)**:
```jsx
<form className="grid grid-cols-1 md:grid-cols-2 gap-6">
  <FormGroup label="First Name">
    <Input />
  </FormGroup>
  
  <FormGroup label="Last Name">
    <Input />
  </FormGroup>
  
  {/* Full width field */}
  <div className="md:col-span-2">
    <FormGroup label="Message">
      <TextArea />
    </FormGroup>
  </div>
  
  {/* Actions */}
  <div className="md:col-span-2 flex gap-4 justify-end">
    <Button variant="secondary">Cancel</Button>
    <Button variant="primary">Submit</Button>
  </div>
</form>
```

---

### Card Grid (Bots, Rules, Schedules)

**Purpose**: Responsive grid of item cards

**Pattern**:
```jsx
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
  {items.map(item => (
    <Card key={item.id} className="hover:shadow-lg transition-shadow">
      <CardHeader>
        <h3>{item.name}</h3>
        <Badge variant={item.status}>{item.status}</Badge>
      </CardHeader>
      <CardContent>{item.description}</CardContent>
      <CardFooter>
        <Button variant="ghost" size="sm">Edit</Button>
        <Button variant="ghost" size="sm">Delete</Button>
      </CardFooter>
    </Card>
  ))}
</div>
```

---

### Settings Page Layout

**Purpose**: Sidebar navigation with content panels

**Pattern**:
```jsx
<div className="grid grid-cols-1 md:grid-cols-4 gap-8">
  {/* Settings Navigation */}
  <nav className="md:col-span-1">
    <ul className="space-y-2">
      {settingsSections.map(section => (
        <li key={section.id}>
          <button
            className={`w-full text-left px-4 py-2 rounded ${
              activeSection === section.id
                ? 'bg-blue-50 dark:bg-blue-900 text-blue-600'
                : 'hover:bg-gray-100'
            }`}
            onClick={() => setActiveSection(section.id)}
          >
            {section.label}
          </button>
        </li>
      ))}
    </ul>
  </nav>
  
  {/* Content Panel */}
  <div className="md:col-span-3">
    <Card>
      {activeSection === 'general' && <GeneralSettings />}
      {activeSection === 'notifications' && <NotificationSettings />}
      {activeSection === 'integration' && <IntegrationSettings />}
    </Card>
  </div>
</div>
```

---

## Component Specification Template

Each component should document:

### Template (Copy for each new component)

```markdown
### ComponentName

**Purpose**: One-sentence description

**Variants**:
- Variant 1: Description
- Variant 2: Description

**Props Interface**:
\`\`\`tsx
interface ComponentNameProps {
  prop1: string;
  prop2?: number;
  prop3?: 'option1' | 'option2';
  children?: React.ReactNode;
}
\`\`\`

**States**:
| State | Appearance | Behavior |
|-------|-----------|----------|
| Default | | |
| Hover | | |
| Active | | |
| Disabled | | |
| Error | | |

**Accessibility**:
- ✅ Feature 1
- ✅ Feature 2

**Usage Examples**:
\`\`\`jsx
// Example 1
<Component prop1="value" />

// Example 2
<Component variant="secondary" disabled />
\`\`\`

**Do's & Don'ts**:
- ✅ DO: Guideline 1
- ❌ DON'T: Guideline 2
```

---

## Implementation Order (Priority)

### Phase 1 (Week 1): Foundation
1. Button, Input, Label
2. Select, Checkbox, Radio
3. Badge, Alert

### Phase 2 (Week 2): Forms
4. FormGroup, TextArea, FileUpload
5. DatePicker, TimePicker
6. Form Layout

### Phase 3 (Week 3): Data Display
7. Card, Table, List
8. Avatar, Badge, Stat Block
9. Empty State, Loading Skeleton

### Phase 4 (Week 4): Navigation & Layout
10. Navbar, Sidebar, Tabs
11. Dashboard Layout
12. Breadcrumb, Pagination, Stepper

### Phase 5 (Week 5): Feedback & Polish
13. Modal, Toast, Tooltip
14. Drawer, Popover
15. Error Boundary

---

**Component Library Status**: ✅ Specifications Complete  
**Ready for Development**: Yes  
**Total Estimated Components**: 60+  
**Estimated Development Time**: 4-5 weeks

