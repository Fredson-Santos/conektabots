# Quick Start - Rules Management

**TL;DR**: Get up and running in 5 minutes.

---

## 🚀 For Users

### I want to create a new rule

1. Go to Dashboard → **Rules Management** page
2. Click **+ Nova Regra** button
3. Follow the 7-step wizard:
   - Select your bot
   - Add source chats (where to read from)
   - Add destination chats (where to forward to)
   - Configure keyword filters (optional)
   - Set conditions (optional)
   - Choose media types (optional)
   - Name your rule and set prefix
4. Click **Salvar Regra**
5. Done! Your rule is now active

---

### I want to edit a rule

1. Go to Rules Management page
2. Find your rule in the table
3. Click **✎ Editar** button
4. Modify the rule name or prefix
5. Click **Salvar Regra**

**Note**: Currently, to change origins/destinations/filters, delete and recreate the rule.

---

### I want to delete a rule

1. Go to Rules Management page
2. Find your rule
3. Click **🗑 Deletar** button
4. Confirm in the modal
5. Done! Rule is deleted

---

### I want to pause a rule without deleting it

1. Find your rule in the table
2. Click the status badge (shows "Ativa" or "Inativa")
3. Status toggles instantly

---

## 👨‍💻 For Developers

### I need to use this component in my code

```typescript
// Import main component
import RulesPage from '@/app/(dashboard)/rules/page'

// Just render it
<RulesPage />
```

That's it! Everything works automatically.

---

### I need to interact with rules from my code

```typescript
import { useRules } from '@/app/(dashboard)/rules/hooks/useRules'

function MyComponent() {
  const { rules, list, create, update, delete: deleteRule } = useRules()

  // Load rules on mount
  useEffect(() => {
    list()
  }, [list])

  // Create a rule
  const handleCreate = async () => {
    const newRule = await create({
      nome: 'My Rule',
      bot_id: 'bot-uuid',
      origens: ['@source'],
      destinos: ['@target'],
      filtros: [],
      condicoes: [],
      filtro_midia: 'todos',
      converter_link: false,
    })
    console.log('Created:', newRule)
  }

  // Display rules
  return (
    <ul>
      {rules.map((rule) => (
        <li key={rule.id}>{rule.nome}</li>
      ))}
    </ul>
  )
}
```

---

### Where's the documentation?

- **📖 Full Guide**: `README.md` - Complete documentation
- **🧪 Testing**: `TEST_SCENARIOS.md` - 110+ test cases
- **📊 Status**: `IMPLEMENTATION_STATUS.md` - Detailed tracking
- **🚀 Advanced**: `ADVANCED_USAGE.md` - Advanced patterns

---

## 🎯 File Locations

```
frontend/app/(dashboard)/rules/
├── page.tsx                # ← Main page (just render this)
├── hooks/
│   └── useRules.ts          # ← CRUD operations
├── components/
│   ├── RulesTable.tsx       # ← Rules list with pagination
│   └── RuleWizard.tsx       # ← 7-step form
└── README.md               # ← Full documentation
```

---

## 🔧 API Endpoints

| Action | API Call | Status |
|--------|----------|--------|
| List | `GET /api/v1/regras` | ✅ Active |
| Get | `GET /api/v1/regras/{id}` | ✅ Active |
| Create | `POST /api/v1/regras` | ✅ Active |
| Update | `PATCH /api/v1/regras/{id}` | ✅ Active |
| Delete | `DELETE /api/v1/regras/{id}` | ✅ Active |

All endpoints automatically include JWT token and tenant_id filtering.

---

## ❓ FAQ

### Q: How many rules can I create?
A: Limited by your plan. Check PLAN_LIMITS in backend/models/enums.py

### Q: Can I preview a rule before activating?
A: Not yet - coming in Phase 2

### Q: How do I test if a rule works?
A: Enable it, watch the logs. Phase 2 will have a "Test Rule" feature.

### Q: Can I export my rules?
A: Not yet - coming in Phase 2

### Q: Why can't I edit the filters/origins after creating?
A: Backend limitation - delete and recreate for now. Phase 2 will fix this.

### Q: How do I debug issues?
A: Check: 1) Browser console, 2) Network tab, 3) README.md troubleshooting

---

## ⚡ Common Tasks

### Get all active rules from React
```typescript
const { rules } = useRules()
const active = rules.filter(r => r.ativo)
```

### Create rule for specific bot
```typescript
const { create } = useRules()
await create({
  nome: 'Bot Security',
  bot_id: botId,
  origens: ['@all'],
  destinos: ['@security'],
  filtros: [{ tipo: 'incluir', valor: 'hack' }],
  condicoes: [],
  filtro_midia: 'todos',
  converter_link: false,
})
```

### Listen to rule changes
```typescript
import { useRulesStore } from '@/app/(dashboard)/rules/hooks/useRules'

useRulesStore.subscribe((state) => {
  console.log('Rules updated:', state.rules)
})
```

---

## 🐛 Troubleshooting

### Rules not loading?
1. Check browser Network tab (API call failing?)
2. Check JWT token in Storage
3. Check API is running
4. Check `tenant_id` in JWT

### Wizard not opening?
1. Clear browser cache
2. Check console for errors
3. Verify API endpoint is correct
4. Check NEXT_PUBLIC_API_URL env var

### Delete not working?
1. Verify you're owner/admin role
2. Check API response in Network tab
3. Try page refresh

---

## 📚 Learn More

- **Basic Usage**: See README.md
- **Test Scenarios**: See TEST_SCENARIOS.md
- **Advanced**: See ADVANCED_USAGE.md
- **Implementation Details**: See IMPLEMENTATION_STATUS.md

---

## ✅ Ready to go!

Everything is set up and ready to use. Start with the main page component or the useRules hook.

Happy building! 🚀

---

**Last Updated**: April 15, 2026  
**Version**: 1.0.0
