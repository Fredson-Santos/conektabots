# 📐 Layout Patterns & Templates

**ConektaBots** standard layout patterns for common use cases

---

## Table of Contents

1. [Dashboard Main Layout](#dashboard-main-layout)
2. [List/Table View with Filters](#listtable-view-with-filters)
3. [Form Pages (Create/Edit)](#form-pages)
4. [Modal Patterns](#modal-patterns)
5. [Card Grid Layouts](#card-grid-layouts)
6. [Settings Page Layout](#settings-page-layout)
7. [Empty & Error States](#empty--error-states)
8. [Responsive Breakpoints](#responsive-breakpoints)

---

## Dashboard Main Layout

### Desktop View (1440px+)

```
┌─────────────────────────────────────────────────────────────┐
│ NAVBAR (sticky)                                    [Profile] │
├──────────┬─────────────────────────────────────────────────┤
│          │                                                  │
│ SIDEBAR  │         MAIN CONTENT (flex-1)                  │
│          │                                                  │
│ 256px    │     [Container max-w-7xl padding-lg]           │
│          │                                                  │
│          │                                                  │
└──────────┴─────────────────────────────────────────────────┘
```

### Mobile View (<768px)

```
┌──────────────────────────────┐
│ NAVBAR [Menu]         [Prof] │
├──────────────────────────────┤
│                              │
│    MAIN CONTENT              │
│    (full width)              │
│                              │
│ Sidebar hidden, uses drawer  │
└──────────────────────────────┘
```

### HTML/JSX Structure

```jsx
export default function DashboardLayout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="flex flex-col h-screen bg-gray-50 dark:bg-gray-950">
      {/* Top Navbar */}
      <header className="sticky top-0 z-40 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
        <nav className="flex items-center justify-between px-6 py-4 max-w-7xl mx-auto w-full">
          <div className="flex items-center gap-4">
            {/* Mobile menu toggle */}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 md:hidden rounded-md hover:bg-gray-100 dark:hover:bg-gray-800"
            >
              <MenuIcon className="w-5 h-5" />
            </button>
            
            {/* Logo */}
            <ConektaBotsLogo className="w-8 h-8" />
            <h1 className="text-xl font-bold hidden sm:inline">ConektaBots</h1>
          </div>

          {/* Right actions */}
          <div className="flex items-center gap-4">
            <NotificationBell />
            <UserProfileMenu />
          </div>
        </nav>
      </header>

      {/* Main layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar Navigation */}
        <aside
          className={`
            fixed inset-y-16 left-0 z-30 bg-gray-900 text-white w-64 
            transition-transform md:static md:inset-auto md:z-0 md:bg-gray-50 md:dark:bg-gray-900 md:text-gray-900 md:dark:text-gray-50
            ${sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
          `}
        >
          <SidebarNav
            items={navigationItems}
            onItemClick={() => setSidebarOpen(false)}
          />
        </aside>

        {/* Main content area */}
        <main className="flex-1 overflow-auto">
          <div className="px-6 py-8 lg:px-8 max-w-7xl">
            {children}
          </div>
        </main>

        {/* Mobile overlay when sidebar open */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 bg-black/50 z-20 md:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}
      </div>
    </div>
  )
}
```

---

## List/Table View with Filters

### Layout Structure

```
┌──────────────────────────────────────┐
│ [Title] [Action Button]              │
├──────────────────────────────────────┤
│ [Search] [Filter Button] [Sort]      │
├──────────┬──────────────────────────┤
│ FILTERS  │  TABLE/LIST              │
│  Sidebar │  (Paginated)             │
│   200px  │  Responsive columns      │
│          │                          │
│          │                          │
└──────────┴──────────────────────────┘
```

### Desktop HTML/JSX

```jsx
export function BotsList() {
  const [filters, setFilters] = useState({})
  const [sortBy, setSortBy] = useState('name')
  const [sortOrder, setSortOrder] = useState('asc')
  const [page, setPage] = useState(1)
  const [showFilters, setShowFilters] = useState(true)

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">Bots</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Manage your automation bots</p>
        </div>
        <Button variant="primary" icon={<PlusIcon />}>
          Create Bot
        </Button>
      </div>

      {/* Toolbar: Search, Filter, Sort */}
      <div className="flex gap-4 mb-6 flex-col sm:flex-row">
        <div className="flex-1">
          <SearchInput
            placeholder="Search bots..."
            onSearch={handleSearch}
            debounceMs={300}
          />
        </div>
        
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="px-4 py-2 border rounded-md flex items-center gap-2 hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          <AdjustmentsIcon className="w-5 h-5" />
          Filters
        </button>

        <Select
          options={[
            { value: 'name-asc', label: 'Name (A-Z)' },
            { value: 'name-desc', label: 'Name (Z-A)' },
            { value: 'active', label: 'Recently Active' },
            { value: 'created', label: 'Recently Created' }
          ]}
          value={`${sortBy}-${sortOrder}`}
          onChange={(val) => {
            const [field, order] = val.split('-')
            setSortBy(field)
            setSortOrder(order)
          }}
        />
      </div>

      {/* Content area with optional sidebar */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Filters Sidebar (hidden on mobile) */}
        {showFilters && (
          <aside className="lg:col-span-1">
            <Card className="p-4">
              <h3 className="font-semibold mb-4">Filters</h3>
              
              <div className="space-y-4">
                <FilterGroup label="Status">
                  <Checkbox label="Active" />
                  <Checkbox label="Paused" />
                  <Checkbox label="Inactive" />
                </FilterGroup>

                <FilterGroup label="Marketplace">
                  <Checkbox label="Shopee" />
                  <Checkbox label="Mercado Livre" />
                  <Checkbox label="Amazon" />
                </FilterGroup>

                <FilterGroup label="Date Range">
                  <DatePicker label="From" />
                  <DatePicker label="To" />
                </FilterGroup>

                <div className="flex gap-2 pt-4">
                  <Button variant="secondary" fullWidth size="sm">
                    Clear
                  </Button>
                  <Button variant="primary" fullWidth size="sm">
                    Apply
                  </Button>
                </div>
              </div>
            </Card>
          </aside>
        )}

        {/* Main Table */}
        <div className={showFilters ? 'lg:col-span-3' : 'lg:col-span-4'}>
          <Card>
            <Table
              columns={[
                { key: 'name', label: 'Name', sortable: true },
                { key: 'marketplace', label: 'Marketplace', sortable: true },
                { key: 'status', label: 'Status', sortable: true },
                { key: 'rules', label: 'Rules', sortable: false },
                { key: 'lastRun', label: 'Last Run', sortable: true },
                { 
                  key: 'actions',
                  label: 'Actions',
                  render: (_, bot) => <BotActionMenu bot={bot} />
                }
              ]}
              data={bots}
              isLoading={isLoading}
              onSort={(key, order) => {
                setSortBy(key)
                setSortOrder(order)
              }}
              pagination={{
                page,
                pageSize: 10,
                total: totalBots,
                onPageChange: setPage
              }}
            />
          </Card>
        </div>
      </div>
    </div>
  )
}
```

### Mobile View (Simplified)

On mobile, the filter sidebar becomes a drawer or is hidden:

```jsx
// Mobile: Simplified card view instead of table
{isMobile && (
  <div className="space-y-3">
    {bots.map(bot => (
      <Card key={bot.id} className="p-4">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="font-semibold">{bot.name}</h3>
            <p className="text-sm text-gray-600">{bot.marketplace}</p>
          </div>
          <Badge variant={bot.status === 'active' ? 'success' : 'secondary'}>
            {bot.status}
          </Badge>
        </div>
        <div className="flex gap-2 mt-4">
          <Button variant="ghost" size="sm" fullWidth>Edit</Button>
          <Button variant="ghost" size="sm" fullWidth>More</Button>
        </div>
      </Card>
    ))}
  </div>
)}
```

---

## Form Pages

### Create/Edit Bot Form

```
┌──────────────────────────────────────┐
│ [Back] Bot Configuration             │
├──────────────────────────────────────┤
│                                      │
│ [Tabs: Details | Rules | Settings]  │
│                                      │
│ ┌──────────────────────────────────┐ │
│ │ [Form 2-column layout]           │ │
│ │                                  │ │
│ │ [Submit] [Cancel]                │ │
│ └──────────────────────────────────┘ │
└──────────────────────────────────────┘
```

### Form Structure

```jsx
export function BotCreatePage() {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    marketplace: 'shopee',
    // ... more fields
  })
  const [activeTab, setActiveTab] = useState('details')
  const [errors, setErrors] = useState({})

  return (
    <div>
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <BackButton />
        <h1 className="text-3xl font-bold">Create New Bot</h1>
      </div>

      {/* Tabs */}
      <Tabs
        tabs={[
          { id: 'details', label: 'Details' },
          { id: 'rules', label: 'Rules' },
          { id: 'integrations', label: 'Integrations' }
        ]}
        activeTabId={activeTab}
        onTabChange={setActiveTab}
      />

      {/* Form Content */}
      <Card className="mt-6">
        {activeTab === 'details' && <BotDetailsForm />}
        {activeTab === 'rules' && <BotRulesForm />}
        {activeTab === 'integrations' && <BotIntegrationsForm />}
      </Card>

      {/* Form Actions */}
      <div className="flex gap-4 justify-end mt-6">
        <Button variant="secondary">Cancel</Button>
        <Button variant="primary" icon={<SaveIcon />}>
          Save Bot
        </Button>
      </div>
    </div>
  )
}

function BotDetailsForm() {
  return (
    <form className="grid grid-cols-1 md:grid-cols-2 gap-6 p-6">
      {/* 1st column */}
      <FormGroup label="Bot Name" required error={errors.name}>
        <Input
          placeholder="Enter bot name..."
          maxLength={50}
          onChange={(e) => updateField('name', e.target.value)}
        />
      </FormGroup>

      {/* 2nd column */}
      <FormGroup label="Marketplace" required>
        <Select
          options={marketplaceOptions}
          onChange={(val) => updateField('marketplace', val)}
        />
      </FormGroup>

      {/* Full width */}
      <div className="md:col-span-2">
        <FormGroup label="Description">
          <TextArea
            placeholder="Describe what this bot does..."
            minRows={4}
            maxLength={500}
          />
        </FormGroup>
      </div>

      {/* Settings */}
      <div className="md:col-span-2 border-t pt-6">
        <h3 className="font-semibold mb-4">Settings</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <FormGroup label="Timezone">
            <Select options={timezoneOptions} />
          </FormGroup>

          <FormGroup>
            <ToggleSwitch
              label="Enable Notifications"
              description="Get notified when rules are triggered"
            />
          </FormGroup>
        </div>
      </div>
    </form>
  )
}
```

### Mobile Form (Stacked)

```css
/* Mobile: Single column stack, larger touch targets */
form.grid-cols-1 {
  grid-template-columns: 1fr;
  gap: 1.5rem; /* Increased for mobile */
}

input, textarea, select {
  min-height: 48px; /* Touch-friendly size */
  padding: 0.75rem; /* Comfortable for thumbs */
}

button {
  min-height: 44px; /* Touch minimum */
}

/* Stack buttons vertically on mobile */
@media (max-width: 640px) {
  div.flex.justify-end {
    flex-direction: column;
  }
  
  button {
    width: 100%;
  }
}
```

---

## Modal Patterns

### Confirmation Modal

```jsx
<Modal
  isOpen={isDeleteConfirmOpen}
  title="Delete Bot?"
  size="sm"
  onClose={() => setIsDeleteConfirmOpen(false)}
  actions={
    <div className="flex gap-4">
      <Button variant="secondary" onClick={() => setIsDeleteConfirmOpen(false)}>
        Cancel
      </Button>
      <Button variant="danger" onClick={handleDelete}>
        Delete Permanently
      </Button>
    </div>
  }
>
  <div className="space-y-4">
    <Alert
      variant="warning"
      title="This action cannot be undone"
      message="All rules, history, and configuration will be permanently deleted."
    />
    <p className="text-gray-600">
      Type <strong className="font-mono bg-gray-100 px-2 py-1">"{bot.name}"</strong> to confirm deletion.
    </p>
    <Input
      placeholder={`Type "${bot.name}" to confirm`}
      value={confirmText}
      onChange={(e) => setConfirmText(e.target.value)}
    />
  </div>
</Modal>
```

### Form Modal

```jsx
<Modal
  isOpen={isCreateRuleOpen}
  title="Create New Rule"
  size="md"
  onClose={() => setIsCreateRuleOpen(false)}
  actions={
    <div className="flex gap-4">
      <Button variant="secondary" onClick={() => setIsCreateRuleOpen(false)}>
        Cancel
      </Button>
      <Button variant="primary" onClick={handleCreateRule}>
        Create Rule
      </Button>
    </div>
  }
>
  <form className="space-y-6 p-6">
    <FormGroup label="Rule Name" required>
      <Input placeholder="e.g., Auto-reply to questions" />
    </FormGroup>

    <FormGroup label="Trigger" required>
      <Select
        options={[
          { value: 'keyword', label: 'Keyword Match' },
          { value: 'time', label: 'Time-based' },
          { value: 'custom', label: 'Custom Filter' }
        ]}
      />
    </FormGroup>

    <FormGroup label="Action" required>
      <Select
        options={[
          { value: 'reply', label: 'Send Reply' },
          { value: 'forward', label: 'Forward to Staff' },
          { value: 'tag', label: 'Add Tag' }
        ]}
      />
    </FormGroup>
  </form>
</Modal>
```

### Alert Modal

```jsx
<Modal
  isOpen={isAlertOpen}
  title="Action Successful"
  size="sm"
  onClose={() => setIsAlertOpen(false)}
  actions={
    <Button variant="primary" fullWidth>
      OK
    </Button>
  }
>
  <div className="flex flex-col items-center gap-4 py-4">
    <CheckCircleIcon className="w-12 h-12 text-green-600" />
    <p className="text-center">
      Your bot has been created successfully and is now<br />
      <strong>active</strong> and ready to process messages.
    </p>
  </div>
</Modal>
```

---

## Card Grid Layouts

### 4-Column Grid (Dashboard Cards)

```jsx
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
  {bots.map(bot => (
    <Card
      key={bot.id}
      className="group hover:shadow-lg transition-shadow cursor-pointer"
      onClick={() => selectBot(bot.id)}
    >
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div>
            <h3 className="font-semibold text-lg">{bot.name}</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {bot.marketplace}
            </p>
          </div>
          <Badge 
            variant={bot.status === 'active' ? 'success' : 'secondary'}
          >
            {bot.status}
          </Badge>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-4 mb-4 pb-4 border-b border-gray-200 dark:border-gray-700">
          <div>
            <p className="text-2xl font-bold">{bot.ruleCount}</p>
            <p className="text-xs text-gray-600">Rules</p>
          </div>
          <div>
            <p className="text-2xl font-bold">{bot.messageCount}</p>
            <p className="text-xs text-gray-600">Messages</p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <Button variant="ghost" size="sm" fullWidth>
            Edit
          </Button>
          <Button variant="ghost" size="sm" fullWidth>
            More
          </Button>
        </div>
      </div>
    </Card>
  ))}
</div>
```

### Rule Cards with Status

```jsx
<div className="space-y-3">
  {rules.map(rule => (
    <Card
      key={rule.id}
      className="p-4 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
    >
      <div className="flex items-center justify-between">
        {/* Left: Rule Info */}
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <Avatar initials={rule.name.substring(0, 2).toUpperCase()} size="sm" />
            <div>
              <h3 className="font-semibold">{rule.name}</h3>
              <p className="text-sm text-gray-600">
                When: {rule.trigger} → Then: {rule.action}
              </p>
            </div>
          </div>
        </div>

        {/* Middle: Status */}
        <div className="hidden sm:block mx-4">
          <Badge variant={rule.active ? 'success' : 'secondary'}>
            {rule.active ? 'Active' : 'Inactive'}
          </Badge>
        </div>

        {/* Right: Execution Count */}
        <div className="hidden md:block text-right mr-4">
          <p className="text-sm font-semibold">{rule.executionCount}</p>
          <p className="text-xs text-gray-600">executions</p>
        </div>

        {/* Actions Menu */}
        <DropdownMenu>
          <Button variant="ghost" size="sm">⋮</Button>
          <Menu>
            <MenuItem onClick={() => editRule(rule.id)}>Edit</MenuItem>
            <MenuItem onClick={() => toggleRuleActive(rule.id)}>
              {rule.active ? 'Deactivate' : 'Activate'}
            </MenuItem>
            <MenuItem variant="danger" onClick={() => deleteRule(rule.id)}>
              Delete
            </MenuItem>
          </Menu>
        </DropdownMenu>
      </div>
    </Card>
  ))}
</div>
```

---

## Settings Page Layout

```
┌─────────────────────────────────────┐
│ Settings                            │
├────────────┬──────────────────────┤
│  General   │                      │
│  Billing   │  [Settings Content]  │
│ Integr...  │                      │
│ Privacy    │                      │
│            │                      │
└────────────┴──────────────────────┘
```

### Implementation

```jsx
export function SettingsPage() {
  const [activeSection, setActiveSection] = useState('general')

  const sections = [
    { id: 'general', label: 'General', icon: <CogIcon /> },
    { id: 'billing', label: 'Billing', icon: <CreditCardIcon /> },
    { id: 'integrations', label: 'Integrations', icon: <ClipboardIcon /> },
    { id: 'privacy', label: 'Privacy & Security', icon: <ShieldCheckIcon /> },
    { id: 'notifications', label: 'Notifications', icon: <BellIcon /> }
  ]

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">Settings</h1>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Settings Navigation */}
        <nav className="lg:col-span-1">
          <div className="space-y-2">
            {sections.map(section => (
              <button
                key={section.id}
                onClick={() => setActiveSection(section.id)}
                className={`
                  w-full flex items-center gap-3 px-4 py-3 rounded-md text-left transition-colors
                  ${activeSection === section.id
                    ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 font-semibold'
                    : 'hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300'
                  }
                `}
              >
                {section.icon && <section.icon className="w-5 h-5" />}
                {section.label}
              </button>
            ))}
          </div>
        </nav>

        {/* Settings Panel */}
        <div className="lg:col-span-3">
          {activeSection === 'general' && <GeneralSettings />}
          {activeSection === 'billing' && <BillingSettings />}
          {activeSection === 'integrations' && <IntegrationsSettings />}
          {activeSection === 'privacy' && <PrivacySettings />}
          {activeSection === 'notifications' && <NotificationSettings />}
        </div>
      </div>
    </div>
  )
}
```

---

## Empty & Error States

### Empty State

```jsx
{items.length === 0 && (
  <Card className="p-12 text-center">
    <div className="flex flex-col items-center gap-4">
      <div className="p-4 bg-gray-100 dark:bg-gray-800 rounded-full">
        <RobotIcon className="w-12 h-12 text-gray-400" />
      </div>
      
      <div>
        <h3 className="text-lg font-semibold mb-2">No bots created yet</h3>
        <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-sm">
          Create your first bot to start automating messages on your marketplace.
        </p>
      </div>

      <Button variant="primary" icon={<PlusIcon />}>
        Create Your First Bot
      </Button>
    </div>
  </Card>
)}
```

### Error State

```jsx
{error && (
  <Alert
    variant="error"
    title="Failed to load bots"
    message={error.message}
    action={
      <Button variant="secondary" size="sm" onClick={retryLoad}>
        Try Again
      </Button>
    }
  />
)}
```

### Loading State

```jsx
{isLoading && (
  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
    {[...Array(6)].map((_, i) => (
      <Skeleton key={i} type="card" height={200} animation="pulse" />
    ))}
  </div>
)}
```

---

## Responsive Breakpoints

ConektaBots uses Tailwind's standard breakpoints:

| Breakpoint | Size | Device | Grid Cols |
|-----------|------|--------|-----------|
| sm | 640px | Small mobile | 2 columns |
| md | 768px | Tablet | 2-3 columns |
| lg | 1024px | Desktop | 3-4 columns |
| xl | 1280px | Large desktop | 4-5 columns |
| 2xl | 1536px | Ultra-wide | 5-6 columns |

### Responsive Component Example

```jsx
<div className="grid gap-4">
  {/* Mobile: 1 col | Tablet: 2 cols | Desktop: 3 cols | Large: 4 cols */}
  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
    {items.map(item => <Card key={item.id}>{item}</Card>)}
  </div>

  {/* Responsive padding */}
  <div className="px-4 sm:px-6 lg:px-8">
    Content with responsive padding
  </div>

  {/* Hide on mobile, show on desktop */}
  <div className="hidden lg:block">
    Sidebar (desktop only)
  </div>

  {/* Show on mobile, hide on desktop */}
  <div className="lg:hidden">
    Mobile menu
  </div>
</div>
```

---

## Common Responsive Patterns

### Hero Section

```jsx
<section className="px-6 py-12 sm:py-16 lg:py-20">
  <div className="max-w-4xl mx-auto text-center">
    <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6">
      Automate Your Marketplace Messages
    </h1>
    <p className="text-lg sm:text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
      Custom rules and instant replies to delight your customers
    </p>
    <div className="flex flex-col sm:flex-row gap-4 justify-center">
      <Button size="lg" variant="primary">Get Started</Button>
      <Button size="lg" variant="secondary">Learn More</Button>
    </div>
  </div>
</section>
```

### Feature Grid

```jsx
<section className="px-6 py-12">
  <h2 className="text-3xl font-bold text-center mb-12">Features</h2>
  
  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
    {features.map(feature => (
      <Card key={feature.id} className="text-center">
        <div className="flex justify-center mb-4">
          {feature.icon}
        </div>
        <h3 className="font-semibold text-lg mb-2">{feature.title}</h3>
        <p className="text-gray-600">{feature.description}</p>
      </Card>
    ))}
  </div>
</section>
```

---

**Layout Patterns Status**: ✅ Complete  
**Ready for Implementation**: Yes

