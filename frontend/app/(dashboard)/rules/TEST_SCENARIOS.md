# Test Scenarios - Rules Management CRUD

**Document Version**: 1.0.0  
**Last Updated**: April 2026  
**Status**: Ready for QA

---

## 📋 Test Categories

1. [Functional Tests](#functional-tests)
2. [UI/UX Tests](#uiux-tests)
3. [Security Tests](#security-tests)
4. [Performance Tests](#performance-tests)
5. [Accessibility Tests](#accessibility-tests)
6. [Error Handling Tests](#error-handling-tests)

---

## Functional Tests

### TC-001: Create Rule with All Steps Complete

**Preconditions**:
- User is logged in
- At least 1 bot exists

**Steps**:
1. Navigate to Rules Management page
2. Click "Nova Regra" button
3. **Step 1**: Select a bot
4. **Step 2**: Add source chats (@vendas, @sales)
5. **Step 3**: Add destination chats (@suporte)
6. **Step 4**: Add keyword filter (tipo: "incluir", valor: "problema")
7. **Step 5**: Check "Deve ter emoji" condition
8. **Step 6**: Select media type "Fotos ou Vídeos", enable "Converter links"
9. **Step 7**: Enter rule name "Reenviar para Suporte" and prefix "[SUPORTE] "
10. Click "Salvar Regra"

**Expected Result**:
- Rule is created successfully
- Wizard closes
- New rule appears in table
- Toast shows success message
- Rules table refreshes

**Acceptance Criteria**:
- ✅ Rule created with all nested children (origens, destinos, filtros, condicoes)
- ✅ Rule appears in table within 1-2 seconds
- ✅ Rule name and bot visible in table
- ✅ Initial status is "Ativa"

---

### TC-002: Create Rule with Minimum Fields

**Preconditions**:
- User is logged in
- At least 1 bot exists

**Steps**:
1. Click "Nova Regra"
2. Step 1: Select bot
3. Step 2: Add 1 source chat
4. Step 3: Add 1 destination chat
5. Steps 4-6: Skip (leave defaults)
6. Step 7: Enter rule name "Minimal Rule"
7. Submit

**Expected Result**:
- Rule created successfully with minimal configuration
- filtros array is empty
- condicoes array is empty
- filtro_midia defaults to "todos"
- converter_link defaults to false

---

### TC-003: Edit Existing Rule

**Preconditions**:
- User is logged in
- At least 1 rule exists

**Steps**:
1. Find rule in table
2. Click "Editar" button
3. Modify rule name to "Updated Rule Name"
4. Modify prefix
5. Change media type
6. Click "Salvar Regra"

**Expected Result**:
- Rule is updated
- Wizard closes
- Table shows updated name
- Updated timestamp changes

---

### TC-004: Delete Rule with Confirmation

**Preconditions**:
- User is logged in
- At least 1 rule exists

**Steps**:
1. Find rule in table
2. Click "Deletar" button
3. Modal appears asking for confirmation
4. Click "Cancelar" (dismiss)

**Expected Result**:
- Modal closes
- Rule still exists in table
- No deletion occurs

**Second Part**:
1. Click "Deletar" again
2. Modal appears
3. Click "Deletar" confirmation button

**Expected Result**:
- Modal closes
- Rule disappears from table
- Success message shown
- Table refreshes

---

### TC-005: Toggle Rule Active/Inactive

**Preconditions**:
- User is logged in
- At least 1 Active rule exists

**Steps**:
1. Find active rule in table (status: "Ativa")
2. Click the status badge
3. Status should change to "Inativa"
4. Click again
5. Status should change back to "Ativa"

**Expected Result**:
- Status toggles instantly
- API call succeeds
- No page reload needed
- ativo field updates

---

### TC-006: Pagination

**Preconditions**:
- User is logged in
- At least 25 rules exist

**Steps**:
1. Navigate to Rules page
2. Table shows first 20 rules
3. Pagination controls visible at bottom
4. Click "Próximo →" button
5. Table shows rules 21-25 (or max)
6. Page number indicator shows "2"
7. Click page "1" button
8. Table returns to first 20 rules

**Expected Result**:
- Pagination works correctly
- Only 20 items displayed per page
- Navigation between pages works
- Counter shows "Exibindo X-Y de Z"

---

### TC-007: Search Rules

**Preconditions**:
- User is logged in
- Multiple rules exist with different names

**Steps**:
1. Navigate to Rules page
2. Type "suporte" in search box
3. Wait 500ms
4. Table filters to show only rules with "suporte" in name

**Expected Result**:
- Search is case-insensitive
- Pagination resets to page 1
- Results update in real-time
- Clear search shows all rules again

---

### TC-008: Add Multiple Origins

**Preconditions**:
- User is creating new rule
- At Step 2

**Steps**:
1. Enter "@vendas" in origin input
2. Click "+ Adicionar"
3. "@vendas" appears as tag below
4. Enter "@sales" in origin input
5. Click "+ Adicionar"
6. "@sales" appears as tag
7. Enter "-1001234567890" (group ID format)
8. Click "+ Adicionar"
9. Three origins now visible

**Expected Result**:
- Multiple origins can be added
- Each shows as a distinct tag with X to remove
- Can proceed to next step with multiple origins

---

### TC-009: Add/Remove Keyword Filters

**Preconditions**:
- User is creating new rule
- At Step 4

**Steps**:
1. Select "Incluir" from tipo dropdown
2. Enter "promoção" in palavra input
3. Click "+ Adicionar"
4. Filter appears as green badge: [Incluir] promoção
5. Select "Bloquear" from tipo
6. Enter "spam" in palavra
7. Click "+ Adicionar"
8. Filter appears as red badge: [Bloquear] spam
9. Click X on first filter
10. Filter is removed

**Expected Result**:
- Multiple filter types supported
- Visual distinction (green vs red)
- Can add/remove filters dynamically
- Filters persist in form state

---

### TC-010: Media Type Selection

**Preconditions**:
- User is creating new rule
- At Step 6

**Steps**:
1. Default is "Todos (sem filtro)"
2. Change to "Only Fotos"
3. Change to "Fotos ou Vídeos"
4. Check "Converter links de afiliado"
5. Proceed to next step

**Expected Result**:
- Selected media type saved to formData
- Converter link checkbox toggles
- Values appear in Step 7 review

---

### TC-011: Review Step Pre-fill

**Preconditions**:
- User at Step 7 of wizard

**Steps**:
1. Observe "Resumo da Regra" section
2. Bot name displayed
3. All origens listed with blue badges
4. All destinos listed with green badges
5. All filters shown
6. Media type displayed
7. Summary is complete

**Expected Result**:
- All previous steps' data visible
- Can edit rule name and prefix at this step
- Changes are reflected in summary

---

## UI/UX Tests

### TC-020: Progress Bar Animation

**Steps**:
1. Start creating new rule
2. Observe progress bar at 14% (1/7)
3. Click "Próximo →" to Step 2
4. Progress bar animates to 28%
5. Continue through steps
6. At Step 7, progress bar at 100%

**Expected Result**:
- Smooth animation of progress bar
- Accurate percentage calculation
- Visual indicator of progress

---

### TC-021: Step Validation Prevents Progression

**Steps**:
1. At Step 1, don't select a bot
2. "Próximo →" button should be disabled or grayed out
3. Select a bot
4. "Próximo →" button becomes enabled
5. At Step 2, proceed without adding origins
6. Button should be disabled

**Expected Result**:
- Next button disabled when requirements not met
- Button enabled after requirements met
- No broken states

---

### TC-022: Loading States

**Steps**:
1. On initial load of Rules page, should show skeleton loaders
2. Wait for API response
3. When creating rule, "Salvar Regra" button shows "Saving..."
4. After success, dialog closes

**Expected Result**:
- Clear visual feedback of loading state
- Buttons disabled during loading
- No double-submissions possible

---

### TC-023: Modal Responsiveness

**Steps**:
1. Open wizard dialog on desktop (1920 width)
2. Dialog is centered, max-width: 2xl
3. Resize window to tablet (768px)
4. Dialog adapts, less padding
5. Resize to mobile (375px)
6. Dialog full-width with padding
7. Content scrollable without breaking layout

**Expected Result**:
- Modal responsive on all screen sizes
- Readable on mobile
- No hidden buttons or inputs
- Scrollable content if too tall

---

### TC-024: Table Responsiveness

**Steps**:
1. View table on desktop
2. All columns visible (Name, Bot, Status, Actions)
3. Resize to tablet
4. Horizontal scroll appears if needed
5. Resize to mobile
6. Actions stack vertically
7. Search input full-width

**Expected Result**:
- Table usable on all screen sizes
- No hidden content on mobile
- Buttons still clickable on small screens

---

## Security Tests

### TC-040: Multi-Tenant Isolation

**Preconditions**:
- Two different tenant accounts

**Steps**:
1. Log in as Tenant A
2. Create a rule "Rule A"
3. Verify rule appears in list
4. Open browser dev tools
5. Note rule ID
6. Log out

7. Log in as Tenant B
8. Navigate to Rules page
9. Verify "Rule A" doesn't appear
10. Try to access via direct URL: `/rules/{ruleId}` from Tenant A

**Expected Result**:
- Tenant B cannot see Rules from Tenant A
- API returns 404 or 403 if trying to access Tenant A's rules
- tenant_id from JWT automatically filters queries

---

### TC-041: JWT Token Included in Requests

**Steps**:
1. Open browser DevTools → Network tab
2. Create a new rule
3. Check POST /api/v1/regras request
4. View Headers
5. Verify Authorization: Bearer {token} present

**Expected Result**:
- All API requests include JWT token
- Token is valid and accepted by backend
- No 401 Unauthorized errors

---

### TC-042: Input Validation

**Steps**:
1. At Step 7 (Review), try rigorously short rule name (1 char: "a")
2. Should be accepted (min_length: 1)
3. Try very long rule name (100+ chars)
4. Should be truncated or show validation error (max_length: 64)
5. Try special characters: "<script>alert('xss')</script>"
6. Should be stored as plain text (not executed)

**Expected Result**:
- Input validation enforced
- No XSS vulnerabilities
- Special characters escaped

---

## Performance Tests

### TC-050: Large Rules List Load Time

**Preconditions**:
- 500+ rules in database for tenant

**Steps**:
1. Navigate to Rules page
2. Start performance timer
3. Wait for rules to load and display
4. Check Network tab for API response time

**Expected Result**:
- Initial load < 2 seconds
- API response < 1 second
- Table renders all 20 items
- Pagination enables fast navigation

---

### TC-051: Wizard Performance

**Steps**:
1. Open wizard
2. Navigate between steps quickly (click Next 5 times, then Back 5 times)
3. No lag or freezing

**Expected Result**:
- Smooth transitions between steps
- No memory leaks with rapid navigation
- Form state managed efficiently

---

### TC-052: Search Performance

**Steps**:
1. Type slowly in search box: "s", "su", "sup", "supo", "supor", "suport", "suporte"
2. Each keystroke should update results in < 100ms

**Expected Result**:
- Real-time search responsive
- No lag while typing
- Debouncing working (if implemented)

---

## Accessibility Tests

### TC-070: Keyboard Navigation

**Steps**:
1. Start at Rules page
2. Press Tab through all interactive elements
3. Focus ring visible on all elements
4. Press Enter on "Nova Regra" button
5. Wizard opens
6. Tab to Next button, press Enter
7. Wizard advances step

**Expected Result**:
- Full keyboard navigation support
- Focus ring visible (blue outline)
- All buttons/inputs accessible via Tab
- Enter activates buttons

---

### TC-071: Screen Reader Announcements

**Steps**:
1. Use screen reader (NVDA, JAWS, VoiceOver)
2. Navigate to Rules page
3. Screen reader announces: "Rules Management heading, level 1"
4. Tab to "Nova Regra" button
5. Screen reader announces: "New Rule button"
6. Table header announced as: "Name, Bot, Status, Actions columns"

**Expected Result**:
- Semantic HTML read correctly
- Labels associated with inputs
- Buttons have accessible names
- Table structure understood

---

### TC-072: Color Contrast

**Steps**:
1. Use color contrast checker tool (WebAIM, Contrast Ratio)
2. Check all text colors against backgrounds
3. Primary text (dark gray on white): Should be 7:1 or higher
4. Secondary text (medium gray on white): Should be 4.5:1 or higher
5. Button text on colored backgrounds

**Expected Result**:
- All text meets WCAG AA (4.5:1)
- Headings meet WCAG AAA (7:1)
- Color alone never indicates status (always + shape/text)

---

### TC-073: Focus Indicators

**Steps**:
1. Press Tab to navigate through page
2. Focus ring should be clearly visible
3. Focus ring should have sufficient contrast
4. Focus ring should not be hidden by other elements

**Expected Result**:
- Blue 2px focus ring visible
- Contrast ratio of focus ring meets accessibility standards
- Focus never lost

---

## Error Handling Tests

### TC-090: Network Error - Request Fails

**Preconditions**:
- Network disconnected or API down

**Steps**:
1. Try to create rule
2. API request fails
3. Error message displayed

**Expected Result**:
- User-friendly error message shown
- "Erro ao criar regra" or specific error from backend
- User can retry
- No data loss
- Form data preserved

---

### TC-091: Validation Error - Missing Required Field

**Steps**:
1. At Step 7, leave rule name empty
2. Try to "Salvar Regra"
3. Error message appears

**Expected Result**:
- "Preencha todos os campos obrigatórios" message shown
- Form doesn't submit
- User informed of missing field
- Can correct and resubmit

---

### TC-092: 404 Error - Rule Not Found

**Preconditions**:
- Try to edit/view nonexistent rule

**Steps**:
1. Manually edit URL to access nonexistent rule ID
2. API returns 404

**Expected Result**:
- Graceful error handling
- User redirected to rules list
- Error message shown: "Regra não encontrada"
- No crash or broken state

---

### TC-093: 403 Error - Unauthorized Access

**Preconditions**:
- Try to access rule from different tenant

**Steps**:
1. Get rule ID from different tenant
2. Try to edit via wizard
3. API returns 403

**Expected Result**:
- Blocked from accessing
- Error message: "Não autorizado"
- Redirected to own rules list
- Security maintained

---

### TC-094: 500 Error - Server Error

**Preconditions**:
- Backend returns 500 error

**Steps**:
1. Try to create/edit rule
2. Backend throws error
3. API returns 500

**Expected Result**:
- User sees: "Erro ao salvar regra"
- Stack trace not shown to user
- User can try again
- Form state preserved

---

## Edge Cases

### TC-100: Same Origin and Destination

**Steps**:
1. Add "@canal" as both origin and destination
2. Submit rule

**Expected Result**:
- Should be allowed (rule might forward messages back to source)
- No validation error
- Behavior depends on backend logic

---

### TC-101: Very Long Prefix Text

**Steps**:
1. Enter 200+ character prefix
2. Should be truncated or rejected (max_length: 255)

**Expected Result**:
- Validated on frontend
- Failed on submit if backend rejects

---

### TC-102: Special Characters in Chat Names

**Steps**:
1. Enter origin: "@мой_канал" (Cyrillic)
2. Enter origin: "🎉_channel" (Emoji)
3. Enter origin: "@canal-sales_v2.1" (Hyphens, underscores, dots)

**Expected Result**:
- All special characters accepted
- Unicode support
- Stored correctly in database

---

### TC-103: Rapid Submission (Spam Click)

**Steps**:
1. Quickly click "Salvar Regra" 5 times
2. Should debounce or disable button

**Expected Result**:
- Only one submission processed
- No duplicate rules created
- Button disabled after first click

---

## Regression Tests

### TC-110: After Update, Existing Rules Still Work

**Preconditions**:
- Rules created before last update

**Steps**:
1. Navigate to Rules page
2. Old rules display correctly
3. Can edit old rules
4. Can delete old rules

**Expected Result**:
- Backward compatibility maintained
- No data corruption
- Old rules continue to function

---

## Summary

**Total Test Cases**: 110+  
**Categories**: 6 (Functional, UI/UX, Security, Performance, Accessibility, Error Handling)

**Recommended Test Execution Order**:
1. Functional tests (core features)
2. Accessibility tests (important for users)
3. Security tests (critical for multi-tenant)
4. Error handling tests (robustness)
5. Performance tests (optimization)
6. Edge cases (unusual scenarios)

**Acceptance Criteria for Release**:
- ✅ All TC-001 to TC-050 passing (essential features)
- ✅ No critical accessibility violations
- ✅ Multi-tenant isolation verified
- ✅ < 5% failures in error handling
- ✅ Load time < 2 seconds for 500+ rules

---

**Status**: Ready for QA  
**Last Updated**: April 2026  
**Document Version**: 1.0.0
