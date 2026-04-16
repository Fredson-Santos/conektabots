# Advanced Usage Guide - Rules Management CRUD

**Document Version**: 1.0.0  
**For**: Advanced developers extending the Rules system  
**Level**: Intermediate to Expert

---

## 📋 Table of Contents

1. [Customizing the Wizard](#customizing-the-wizard)
2. [Extending the Hook](#extending-the-hook)
3. [Advanced Validation](#advanced-validation)
4. [Performance Optimization](#performance-optimization)
5. [Custom Step Components](#custom-step-components)
6. [Integrating with External Services](#integrating-with-external-services)
7. [Testing Patterns](#testing-patterns)
8. [Debugging](#debugging)

---

## Customizing the Wizard

### Adding a New Custom Step

Scenario: You want to add an 8th step for "Notifications" before review.

```typescript
// 1. In RuleWizard.tsx, update INITIAL_FORM_STATE
const INITIAL_FORM_STATE = {
  // ... existing fields
  notificacoes: [] as string[],  // New field
}

// 2. Update step count and add new step condition
{currentStep === 8 && (
  <StepNotifications
    value={formData.notificacoes}
    onChange={(notificacoes) => setFormData({ ...formData, notificacoes })}
  />
)}

// 3. Update step validation
const isStepValid = () => {
  switch (currentStep) {
    // ... existing cases
    case 8:
      return true // Notifications optional
    case 8:  // Review is now step 8
      return formData.nome.trim() !== ''
    // ...
  }
}

// 4. Create StepNotifications component
function StepNotifications({
  value,
  onChange,
}: {
  value: string[]
  onChange: (notificacoes: string[]) => void
}) {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Notifications</h3>
      {/* Your custom UI */}
    </div>
  )
}

// 5. Update header progress bar
p className="mt-1 text-sm text-gray-600">
  Passo {currentStep} de 8
</p>
```

### Styling the Wizard Modal

```typescript
// Override modal sizing
<div className="max-w-4xl">  {/* Instead of max-w-2xl */}
  {/* content */}
</div>

// Add custom background gradient
<div className="bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50">
  {/* Modal content */}
</div>
```

---

## Extending the Hook

### Adding Custom Queries

```typescript
import { useRules } from '@/app/(dashboard)/rules/hooks/useRules'

// Extend hook with custom methods
export const useRulesExtended = () => {
  const baseRules = useRules()
  const api = getApi()

  const getActiveRules = useCallback(async () => {
    const allRules = await baseRules.list()
    return allRules.filter((r) => r.ativo)
  }, [baseRules])

  const getRulesByBot = useCallback(
    async (botId: UUID) => {
      const allRules = await baseRules.list()
      return allRules.filter((r) => r.bot_id === botId)
    },
    [baseRules]
  )

  const getStatistics = useCallback(async () => {
    const response = await api.get('/regras/stats')
    return response.data
  }, [api])

  return {
    ...baseRules,
    getActiveRules,
    getRulesByBot,
    getStatistics,
  }
}

// Usage in component
const { getActiveRules, getRulesByBot } = useRulesExtended()
```

### Adding Optimistic Updates

```typescript
// In useRules hook
const optimisticToggle = useCallback(
  async (regraId: UUID, currentStatus: boolean) => {
    // 1. Instant UI update (optimistic)
    const updatedRule: Regra = {
      ...store.rules.find((r) => r.id === regraId)!,
      ativo: !currentStatus,
    }
    store.setRules(
      store.rules.map((r) => (r.id === regraId ? updatedRule : r))
    )

    // 2. Then make API call
    try {
      await api.patch(`/regras/${regraId}`, {
        ativo: !currentStatus,
      })
      // Success - keep optimistic update
    } catch (err) {
      // Revert optimistic update on error
      store.setRules(
        store.rules.map((r) =>
          r.id === regraId
            ? { ...r, ativo: currentStatus } // Restore original
            : r
        )
      )
      throw err
    }
  },
  [api, store]
)
```

### Polling for Updates

```typescript
// Auto-refresh rules every 30 seconds
useEffect(() => {
  const interval = setInterval(() => {
    list()
  }, 30000) // 30 seconds

  return () => clearInterval(interval)
}, [list])
```

---

## Advanced Validation

### Custom Validators

```typescript
// validators.ts
export const validateChatId = (chatId: string): boolean => {
  // Format: @channel_name or -1001234567890
  const formatRegex = /^(@[\w_]+|-\d{10,})$/
  return formatRegex.test(chatId)
}

export const validateDuplicateChatIds = (
  origins: string[],
  destinations: string[]
): boolean => {
  const originSet = new Set(origins)
  return !destinations.some((d) => originSet.has(d))
}

export const validateFilterLength = (value: string): boolean => {
  return value.length >= 2 && value.length <= 255
}

// In RuleWizard.tsx
const handleAddOrigin = () => {
  if (!validateChatId(input)) {
    setError('Formato de chat inválido: use @channel ou -10012345...')
    return
  }

  if (!validateDuplicateChatIds([...origens, input], destinos)) {
    setError('Este chat está configurado como destino também')
    return
  }

  onChange([...origens, input])
}
```

### Schema Validation with Zod

```typescript
import { z } from 'zod'

const RegraCreateSchema = z.object({
  nome: z.string().min(1).max(64),
  bot_id: z.string().uuid(),
  origens: z.array(z.string()).min(1),
  destinos: z.array(z.string()).min(1),
  filtros: z.array(
    z.object({
      tipo: z.enum(['incluir', 'bloquear']),
      valor: z.string().min(1).max(255),
    })
  ),
  condicoes: z.array(z.string()),
})

// Use in submit handler
const result = RegraCreateSchema.safeParse(formData)
if (!result.success) {
  setError(result.error.issues[0].message)
  return
}
```

---

## Performance Optimization

### Memoizing Components

```typescript
import { memo } from 'react'

// Prevent unnecessary re-renders
export const RulesTable = memo(function RulesTable({
  onEdit,
  onRefresh,
}: RulesTableProps) {
  // ... component code
})

export const RuleWizard = memo(function RuleWizard({
  mode,
  initialData,
  onComplete,
  onCancel,
}: RuleWizardProps) {
  // ... component code
})
```

### Virtual Scrolling for Large Lists

```typescript
import { FixedSizeList } from 'react-window'

// For > 1000 rules
function RulesTableVirtualized({ rules }: { rules: Regra[] }) {
  return (
    <FixedSizeList
      height={600}
      itemCount={rules.length}
      itemSize={80}
      width="100%"
    >
      {({ index, style }) => (
        <div style={style} className="border-b px-6 py-4">
          <p className="font-medium">{rules[index].nome}</p>
        </div>
      )}
    </FixedSizeList>
  )
}
```

### Debouncing Search

```typescript
import { useMemo } from 'react'

export function RulesTableOptimized({ rules }: Props) {
  const [searchTerm, setSearchTerm] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchTerm)
    }, 300)

    return () => clearTimeout(timer)
  }, [searchTerm])

  // Memoize filtered results
  const filtered = useMemo(
    () =>
      rules.filter((r) =>
        r.nome.toLowerCase().includes(debouncedSearch.toLowerCase())
      ),
    [rules, debouncedSearch]
  )

  return (
    <>
      <input
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        placeholder="Searching..."
      />
      {/* Render filtered */}
    </>
  )
}
```

---

## Custom Step Components

### Reusable Step Template

```typescript
/**
 * Custom step component template
 * @param value - Current value
 * @param onChange - Update function
 * @returns JSX for step
 */
type StepProps<T> = {
  value: T
  onChange: (value: T) => void
}

function StepTemplate<T>({ value, onChange }: StepProps<T>) {
  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Step Title
        </h3>
        <p className="text-sm text-gray-600">
          Description of this step
        </p>
      </div>

      {/* Your step UI */}

      {/* Always show helpful info */}
      <div className="rounded-lg bg-blue-50 p-3 border border-blue-200">
        <p className="text-xs text-blue-700">
          💡 Helpful tip about this step
        </p>
      </div>
    </div>
  )
}
```

---

## Integrating with External Services

### Slack Notifications on Rule Changes

```typescript
// In useRules hook
const create = useCallback(
  async (data: RegraCreateData) => {
    try {
      const response = await api.post<RegraFull>('/regras', data)

      // Notify Slack
      await api.post('/webhooks/slack', {
        event: 'rule.created',
        rule_name: data.nome,
        user: getCurrentUser(),
        timestamp: new Date(),
      })

      await list()
      return response.data
    } catch (err) {
      // Send error to Slack too
      await api.post('/webhooks/slack', {
        event: 'rule.create_failed',
        error: err.message,
      })
      throw err
    }
  },
  [api, list]
)
```

### Analytics Integration

```typescript
// Track user actions
const handleWizardComplete = async () => {
  // Send to analytics
  window.gtag?.event('rule_created', {
    steps_completed: 7,
    total_filters: formData.filtros.length,
    has_conditions: formData.condicoes.length > 0,
  })

  setWizardMode(null)
  await list()
}
```

---

## Testing Patterns

### Unit Test: useRules Hook

```typescript
import { renderHook, act } from '@testing-library/react'
import { useRules } from '@/app/(dashboard)/rules/hooks/useRules'

describe('useRules', () => {
  it('should list rules', async () => {
    const { result } = renderHook(() => useRules())

    await act(async () => {
      await result.current.list()
    })

    expect(result.current.rules).toHaveLength(5)
  })

  it('should create rule with children', async () => {
    const { result } = renderHook(() => useRules())

    const newRule = await act(async () => {
      return await result.current.create({
        nome: 'Test Rule',
        bot_id: 'bot-1',
        origens: ['@test'],
        destinos: ['@target'],
        filtros: [],
        condicoes: [],
        filtro_midia: 'todos',
        converter_link: false,
      })
    })

    expect(newRule.nome).toBe('Test Rule')
    expect(newRule.origens).toHaveLength(1)
  })

  it('should toggle rule status', async () => {
    const { result } = renderHook(() => useRules())

    const toggled = await act(async () => {
      return await result.current.toggle('rule-1', true)
    })

    expect(toggled.ativo).toBe(false)
  })
})
```

### Component Test: RuleWizard

```typescript
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { RuleWizard } from '@/app/(dashboard)/rules/components/RuleWizard'

describe('RuleWizard', () => {
  it('should display all 7 steps', () => {
    render(
      <RuleWizard
        mode="create"
        onComplete={jest.fn()}
        onCancel={jest.fn()}
      />
    )

    // On step 1
    expect(screen.getByText(/Qual bot/i)).toBeInTheDocument()

    // Click next 6 times
    for (let i = 0; i < 6; i++) {
      userEvent.click(screen.getByText('Próximo →'))
    }

    // Should be at step 7
    expect(screen.getByText(/Resumo da Regra/i)).toBeInTheDocument()
  })

  it('should require rule name on submit', async () => {
    const onComplete = jest.fn()
    const user = userEvent.setup()

    render(
      <RuleWizard
        mode="create"
        onComplete={onComplete}
        onCancel={jest.fn()}
      />
    )

    // Go to step 7
    for (let i = 0; i < 6; i++) {
      await user.click(screen.getByText('Próximo →'))
    }

    // Try to submit without name
    await user.click(screen.getByText('Salvar Regra'))

    // Should show error
    expect(screen.getByText(/campos obrigatórios/i)).toBeInTheDocument()
    expect(onComplete).not.toHaveBeenCalled()
  })
})
```

---

## Debugging

### Debug Mode

```typescript
// In development, add debug logging
if (process.env.NODE_ENV === 'development') {
  console.log('[RuleWizard] Step:', currentStep)
  console.log('[RuleWizard] Form Data:', formData)
}

// In browser console
localStorage.setItem('debug_rules', 'true')

// Enable verbose logging
const debug = localStorage.getItem('debug_rules') === 'true'
if (debug) {
  console.log('[DEBUG]', message, data)
}
```

### API Debugging

```typescript
// Intercept API calls for debugging
const api = getApi()
api.interceptors.request.use((config) => {
  console.log('[API REQUEST]', config.method?.toUpperCase(), config.url)
  console.log('[API BODY]', config.data)
  return config
})

api.interceptors.response.use(
  (response) => {
    console.log('[API RESPONSE]', response.status, response.data)
    return response
  },
  (error) => {
    console.error('[API ERROR]', error.response?.status, error.response?.data)
    return Promise.reject(error)
  }
)
```

### State Debugging

```typescript
// Debug Zustand store
import { useRulesStore } from '@/app/(dashboard)/rules/hooks/useRules'

// Subscribe to changes
useRulesStore.subscribe((state) => {
  console.log('[STORE UPDATE]', state)
})

// Get current state
const state = useRulesStore.getState()
console.log('[STORE STATE]', state)
```

---

## Performance Monitoring

### React DevTools Profiler

```typescript
import { Profiler } from 'react'

function onRenderCallback(id, phase, actualDuration) {
  console.log(`${id} (${phase}) took ${actualDuration}ms`)
}

export function RulesPageWithProfiler() {
  return (
    <Profiler id="RulesPage" onRender={onRenderCallback}>
      <RulesPage />
    </Profiler>
  )
}
```

### Performance Metrics

```typescript
// Measure key operations
const startTime = performance.now()
await list()
const endTime = performance.now()
console.log(`RulesList took ${endTime - startTime}ms`)

// Or use Web Vitals
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals'

getCLS(console.log) // Cumulative Layout Shift
getFID(console.log) // First Input Delay
getFCP(console.log) // First Contentful Paint
getLCP(console.log) // Largest Contentful Paint
getTTFB(console.log) // Time to First Byte
```

---

## Common Patterns & Recipes

### Conditional Step Rendering

```typescript
{/* Only show filters step if bot has filter capability */}
{bot?.supportsFilters && currentStep === 4 && (
  <StepFilters {...props} />
)}

{/* Alternate flow for certain users */}
{user.role === 'viewer' && currentStep === 7 && (
  <p className="text-sm text-gray-500">
    You can only view rules. Contact an admin to edit.
  </p>
)}
```

### Pre-population From Query Params

```typescript
// Get rule template from URL: /rules?template=shopee_webhook
const { template } = useSearchParams()

useEffect(() => {
  if (template === 'shopee_webhook') {
    setFormData({
      ...formData,
      nome: 'Shopee Orders',
      filtros: [
        { tipo: 'incluir', valor: 'shopee' },
      ],
    })
  }
}, [template])
```

### Export Rules as JSON

```typescript
const handleExportRules = (rules: Regra[]) => {
  const json = JSON.stringify(rules, null, 2)
  const blob = new Blob([json], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `rules_export_${new Date().toISOString()}.json`
  a.click()
}
```

---

## Best Practices Checklist

- [ ] Always validate on both client and server
- [ ] Use optimistic updates for better UX
- [ ] Debounce expensive operations
- [ ] Memoize heavy computations
- [ ] Test happy path and error paths
- [ ] Log important state changes
- [ ] Handle edge cases (empty lists, network errors)
- [ ] Provide helpful inline documentation
- [ ] Monitor performance in production
- [ ] Keep components small and focused

---

**Document Version**: 1.0.0  
**Last Updated**: April 15, 2026  
**Target Audience**: Advanced developers expanding the system
