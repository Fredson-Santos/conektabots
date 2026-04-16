# Bots Management CRUD - Test Scenarios

## Test Environment Setup

```bash
# Prerequisites
- Backend running: http://localhost:8000
- Frontend running: npm run dev
- JWT token in localStorage (from login)
- Tenant ID available from auth context
```

## Test Cases

### 1. Load Bots List

**Scenario**: User navigates to /dashboard/bots

**Steps**:
1. Go to http://localhost:3000/dashboard/bots
2. Wait for initial load

**Expected**:
- ✅ Page loads without errors
- ✅ "Bots Management" title visible
- ✅ "Create Bot" button visible
- ✅ Loading skeleton shows briefly
- ✅ Table or "No bots" message displays
- ✅ If bots exist: Table shows with correct columns
- ✅ Pagination visible if > 20 bots

**Possible Issues**:
- 401 error → Token expired (check localStorage)
- 403 error → Tenant isolation issue
- Network error → Backend not running
- No data → Check GET /api/v1/bots response

---

### 2. Create Bot - Valid Data

**Scenario**: User creates a new bot with all required fields

**Steps**:
1. Click "Create Bot" button
2. Fill form:
   - Bot Name: "My Testing Bot"
   - API ID: "123456789"
   - API Hash: "abcdef1234567890"
   - Phone: "+55 11 9 9999-9999"
3. Click "Create Bot" button in modal

**Expected**:
- ✅ Modal opens with title "Create New Bot"
- ✅ Form fields are empty
- ✅ Submit button text says "Create Bot"
- ✅ Submit button shows spinner while loading
- ✅ Modal closes after success
- ✅ New bot appears in table
- ✅ Success: POST 201/200 to /api/v1/bots

**Possible Issues**:
- Form won't submit → Field validation failing (red text shown)
- Modal stays open → API returned error (check console)
- Duplicate name → Backend validation (error shown in modal)

---

### 3. Form Validation - Invalid Data

**Scenario 1: Empty Bot Name**
- Leave "Bot Name" empty
- Expected: Red error "Bot name is required"
- Submit button disabled

**Scenario 2: Bot Name Too Short**
- Enter "A" in Bot Name
- Expected: Red error "Bot name must be at least 2 characters"

**Scenario 3: Bot Name Too Long**
- Enter 51+ characters in Bot Name
- Expected: Red error "Bot name must not exceed 50 characters"

**Scenario 4: Empty API ID**
- Clear API ID field
- Expected: Red error "API ID is required"

**Scenario 5: Empty API Hash**
- Clear API Hash field
- Expected: Red error "API Hash is required"

**Scenario 6: Empty Phone**
- Clear Phone field
- Expected: Red error "Phone number is required"

**Expected for All**:
- ✅ Red border on input
- ✅ Red background on input
- ✅ Red error text below input
- ✅ Submit button disabled (grayed out)
- ✅ Error clears when user types valid value
- ✅ Form cannot submit while errors exist

---

### 4. Edit Bot

**Scenario**: User edits existing bot

**Steps**:
1. Find bot in table
2. Click "Edit" button
3. Modal opens with title "Edit Bot: [Bot Name]"
4. Form fields pre-populated with current data
5. Change Bot Name to "Updated Bot Name"
6. Click "Update Bot" button

**Expected**:
- ✅ Modal title shows "Edit Bot: " + original name
- ✅ All fields show current bot data
- ✅ Submit button text says "Update Bot"
- ✅ PATCH request sent to /api/v1/bots/{id}
- ✅ Modal closes
- ✅ Table shows updated data

**Possible Issues**:
- Modal doesn't show bot data → API didn't fetch correctly
- Submit fails → Validation error on backend
- Data doesn't update → PATCH response not handled

---

### 5. Toggle Bot Status

**Scenario**: User toggles active/inactive status

**Steps**:
1. Find bot in table
2. Click toggle button in Status column (green/gray switch)
3. Wait for API call

**Expected**:
- ✅ Toggle button visually switches (green ↔ gray)
- ✅ Status text changes (Active ↔ Inactive)
- ✅ Spinner appears on toggle during loading
- ✅ PATCH request to /api/v1/bots/{id} with ativo: true/false
- ✅ Change persisted (refresh page → status remains)

**Mobile Toggle**:
- ✅ Card layout shows toggle above bot actions
- ✅ Toggle works same as desktop

**Possible Issues**:
- Toggle doesn't change → API call failed
- Change reverts → API returns error
- Spinner never shows → Missing loading state

---

### 6. Delete Bot

**Scenario**: User deletes bot with confirmation

**Steps**:
1. Find bot in table
2. Click "Delete" button
3. Confirmation modal appears
4. Verify warning message shown
5. Click "Delete Bot" button in modal

**Expected**:
- ✅ Confirmation modal appears
- ✅ Title: "Delete Bot"
- ✅ Warning banner visible
- ✅ Shows bot name: "Are you sure you want to delete '[name]'?"
- ✅ Two buttons: "Cancel" (gray) and "Delete Bot" (red)
- ✅ DELETE request to /api/v1/bots/{id}
- ✅ Spinner shows during deletion
- ✅ Modal closes
- ✅ Bot removed from table

**Cancel Deletion**:
- Click "Cancel" button
- Expected: Modal closes, table unchanged

**Possible Issues**:
- Modal doesn't appear → Click handler not firing
- Delete fails → API returned 500 (check backend logs)
- Bot still in list → Table state not updated

---

### 7. Pagination

**Prerequisites**: > 20 bots in database

**Scenario**: User navigates pages

**Steps**:
1. Load /dashboard/bots
2. Verify "Page 1 of X" shown
3. Click "Next →" button
4. Wait for load

**Expected**:
- ✅ First page shows items 1-20
- ✅ "Next →" button enabled, "Previous ←" disabled
- ✅ Click Next → API called with page=2
- ✅ Table updates showing items 21-40
- ✅ Both buttons now enabled
- ✅ Click Previous → items 1-20 again

**Edge Cases**:
- Last page: "Previous ←" enabled, "Next →" disabled
- Single page (≤20 items): No pagination shown
- Exactly 20 items: Pagination not shown

**Possible Issues**:
- Pagination buttons don't work → onPageChange not called
- Page doesn't change → API not being called
- Items don't update → Bots state not refreshed

---

### 8. Empty State

**Scenario**: User navigates when no bots exist

**Steps**:
1. Delete all bots (if any)
2. Navigate to /dashboard/bots
3. Wait for load

**Expected**:
- ✅ No table shown
- ✅ Empty state message: "No bots yet"
- ✅ Helpful text: "Create your first bot to get started"
- ✅ Dashed border box with centered message

**Create from Empty**:
- Click "Create Bot" button in page header
- Expected: Modal opens with empty form
- After create: Empty state disappears, table appears

---

### 9. Network Error Handling

**Scenario**: Backend returns error

**Steps**:
1. Stop backend server (or force network error)
2. Try to create/edit/delete bot
3. Or refresh page to trigger GET

**Expected**:
- ✅ Error message appears: "Failed to [action]. Please try again."
- ✅ Modal stays open (create/edit)
- ✅ Modal shows red error banner
- ✅ User can retry after fixing issue

**500 Error from Backend**:
- Backend returns 500 error
- Expected: "Failed to [action]. Please try again."

**401 Unauthorized**:
- Token expired
- Expected: 
  - ① First request fails with 401
  - ② Automatic token refresh attempted
  - ③ If refresh succeeds: Original request retried
  - ④ If refresh fails: User redirected to login

---

### 10. Responsive Design - Mobile

**Scenario**: View on mobile device (375px width)

**Steps**:
1. Open DevTools (F12)
2. Set viewport to iPhone SE (375x667)
3. Navigate to /dashboard/bots

**Expected Table**:
- ✅ Table NOT visible (hidden with md: breakpoint)
- ✅ Card layout shows instead
- ✅ Card format:
  - Bot name (bold) at top
  - API ID (monospace) below
  - Status toggle on right side
  - Created date as small text
  - Edit/Delete buttons below data

**Responsive Actions**:
- ✅ Create button takes full width on mobile
- ✅ Modal still centered, takes max-w-md
- ✅ Form inputs take full width in modal
- ✅ Buttons stack vertically on mobile

**Possible Issues**:
- Table visible on mobile → Tailwind md: breakpoint not working
- Modal not centered → Fixed positioning issue
- Buttons cut off → Overflow hidden somewhere

---

### 11. Keyboard Navigation

**Scenario**: User navigates form with keyboard

**Steps**:
1. Open Create Bot modal
2. Press Tab → Focus on first input (Bot Name)
3. Press Tab → Focus moves to next field
4. Continue Tab through all fields and buttons
5. Focus on Create Bot button
6. Press Enter → Form submits

**Expected**:
- ✅ All inputs receive focus (blue ring visible)
- ✅ Tab order: Name → API ID → API Hash → Phone → Create → Cancel
- ✅ Shift+Tab reverses order
- ✅ Blue focus ring visible on inputs
- ✅ Enter in last input triggers submit

**Possible Issues**:
- Focus ring not visible → Missing focus:ring-blue-500
- Tab skips fields → Z-index or visibility issue
- Enter doesn't submit → No form onSubmit handler

---

### 12. Concurrent Operations

**Scenario**: User tries multiple operations simultaneously

**Steps**:
1. Open Create modal
2. Quickly click Create button twice
3. Observe behavior

**Expected**:
- ✅ First click triggers request
- ✅ Second click ignored (button disabled during loading)
- ✅ Only one POST sent (no duplicates)
- ✅ Modal closes once

**Multiple Modals**:
- Click Edit while Create modal open
- Expected: Modal stays create (edit click ignored)

**Possible Issues**:
- Duplicate requests sent → No loading state guard
- Multiple modals appear → State management issue

---

### 13. Form State Persistence

**Scenario**: User fills form, cancels, reopens

**Steps**:
1. Click Create Bot
2. Fill in some fields (not all)
3. Click Cancel
4. Click Create Bot again

**Expected**:
- ✅ Form is empty (fresh state)
- ✅ Previous values not retained
- ✅ No validation errors shown

**Edit Then Create**:
1. Click Edit on existing bot
2. Form populates with bot data
3. Click Cancel
4. Click Create Bot button

**Expected**:
- ✅ Create modal shows empty form
- ✅ No data from previous bot shown

---

## Performance Tests

### Load Time
- Measure time from click to modal visible
- Expected: < 500ms
- Check DevTools Performance tab

### Large Lists
- Add 1000 bots to database
- Load /dashboard/bots
- Expected:
  - ✅ Only first 20 loaded (pagination)
  - ✅ No page lag
  - ✅ Table scrolls smoothly

### Re-renders
- Check DevTools React Profiler
- Expected: Components only re-render when state changes
- No unnecessary re-renders on hover or input change

---

## Accessibility Tests

### Screen Reader (Windows: NVDA, Mac: VoiceOver)
- Read page: "Bots Management" visible
- Read table: Headers announced, row data read
- Read form: Labels read for each input
- Read modals: Title and buttons announced

### Keyboard Only
- Tab through all interactive elements
- No elements unreachable via keyboard
- Focus rings visible
- Can dismiss modals with Escape key (if implemented)

### Color Contrast
- Use WAVE or Lighthouse audit
- All text: WCAG AA (4.5:1 ratio)
- Status colors: Color + icon/text, not color alone

---

## Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Test on Each**:
- Load page
- Create bot
- Edit bot
- Delete bot
- Check console for errors

---

## Regression Tests (Run After Each Change)

- [ ] Can create bot
- [ ] Can list bots with pagination
- [ ] Can edit bot
- [ ] Can delete bot
- [ ] Can toggle status
- [ ] Mobile responsive
- [ ] Form validation works
- [ ] Error messages display
- [ ] No console errors

---

## Known Limitations / Future Tests

- [ ] Search/filter functionality (not yet implemented)
- [ ] Bulk operations (not yet implemented)
- [ ] Rate limiting (depends on backend)
- [ ] Offline support with service workers
- [ ] Undo/redo functionality
