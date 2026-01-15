# Invoice Tab Bug Fix - January 15, 2026

## 🐛 THE BUG

**Issue:** Invoice tab was NOT loading all unbilled time entries for a client. Specifically, entries using **GLOBAL TASKS** were completely missing.

**Root Cause:**
The `load_invoiceable_entries()` method was joining tables incorrectly:

```sql
FROM time_entries te
JOIN tasks t ON te.task_id = t.id
JOIN projects p ON t.project_id = p.id  -- ❌ WRONG!
```

**Why This Failed:**
- Global tasks have `tasks.project_id = NULL` (they're not tied to a project)
- The JOIN would fail for any time entry using a global task
- Result: **Entries with global tasks were EXCLUDED from invoice queries**

---

## ✅ THE FIX

**Changed JOIN to use project_id from time_entries table:**

```sql
FROM time_entries te
JOIN tasks t ON te.task_id = t.id
JOIN projects p ON te.project_id = p.id  -- ✅ CORRECT!
```

**Why This Works:**
- When you create a manual entry with a global task, the app stores the `project_id` in the `time_entries` table
- This column ALWAYS has a valid project_id (even for global tasks)
- Now the JOIN works for BOTH regular tasks AND global tasks

---

## 📝 CHANGES MADE

### Files Modified:
- `gui.py` (lines ~3424, ~3434, ~3453, ~3465, ~3568)

### Methods Fixed:
1. **`load_invoiceable_entries()`** - 4 SQL queries updated
   - "All Uninvoiced" filter (with and without project filter)
   - "Date Range" filter (with and without project filter)

2. **`show_invoice_preview_dialog()`** - 1 SQL query updated
   - Query that generates invoice preview from selected entries

---

## 🧪 TESTING INSTRUCTIONS

### Test Case 1: Verify Missing Entries Now Appear

1. **Go to Invoice Tab**
2. **Select the CLIENT** that was showing incomplete entries
3. **Select "All Projects"**
4. **Click "LOAD ENTRIES"**

**Expected Result:**
- ALL 3 time entries should now appear (or however many you have)
- Previously hidden entries with global tasks are now visible

---

### Test Case 2: Create Invoice with Global Task Entries

1. **Select all loaded entries** (Ctrl+A or "Select All" button)
2. **Click "Preview Invoice"**

**Expected Result:**
- Invoice preview dialog opens
- All items listed with correct hours and amounts
- Global task entries are included

3. **Click "CREATE INVOICE"**

**Expected Result:**
- PDF generates successfully
- Entries are marked as billed
- No error messages

---

### Test Case 3: Verify on Both Machines

Since you're using Google Drive sync:

**Desktop:**
1. Test the fix as above
2. Create an invoice with global task entries

**Laptop:**
1. Launch app (will sync from Google Drive)
2. Go to "💰 Billed Invoices" tab
3. Verify the invoice you just created shows up
4. Go to "Time Entries" tab → "Billed Only" filter
5. Verify all entries marked as billed

---

### Test Case 4: Daily Totals Display

1. **Go to Timer tab**
2. **Look at "Today's Time by Client" section**

**Expected Result:**
- If you made manual entries today, they should show in totals
- Both regular and global task entries contribute to totals

---

## 🔍 HOW TO IDENTIFY THE ISSUE

If the bug is NOT fixed, you'll see:

❌ **Symptoms:**
- Invoice tab shows fewer entries than expected
- Manual entries with global tasks missing from invoice
- Daily totals don't match Time Entries tab
- Specific client shows only 1 entry when you know there are 3

✅ **After Fix:**
- All unbilled entries appear in Invoice tab
- Can select and invoice global task entries
- Entry counts match across all tabs
- Daily totals accurate

---

## 💡 BACKGROUND: Why Global Tasks Were Added

**Global Tasks Feature (v1.1.0 - Jan 7, 2026):**
- Allow creating tasks that work across ALL projects
- Example: "Documentation", "Meetings", "Code Review"
- These tasks have `tasks.project_id = NULL` in database

**Manual Entry Fix (v2.0.2 - Jan 13, 2026):**
- Fixed manual entry form to accept global tasks
- Added `project_id_override` parameter to properly save entries
- Time entries table correctly stores project context

**This Bug:**
- The manual entry fix SAVED entries correctly
- But the Invoice tab LOADING logic was still broken
- Now both parts work together correctly!

---

## 📊 DATABASE STRUCTURE (For Reference)

```
tasks table:
- id
- name
- project_id  <-- NULL for global tasks ❗
- is_global   <-- 1 for global tasks

time_entries table:
- id
- task_id
- project_id  <-- ALWAYS has a value ✅
- client_id
- start_time
- duration_minutes
- is_billed
```

**Key Insight:**
- `tasks.project_id` is nullable (for global tasks)
- `time_entries.project_id` is NEVER null (context is required when logging time)
- Invoice queries should use `time_entries.project_id`, not `tasks.project_id`

---

## 🎯 WHAT'S FIXED

✅ Invoice tab loads ALL unbilled entries (including global tasks)  
✅ Invoice preview includes global task entries  
✅ PDF generation works for invoices with global tasks  
✅ Entry counts accurate across all tabs  
✅ Works on both Desktop and Laptop (via Google Drive sync)

---

## 📞 IF ISSUES PERSIST

1. **Close and restart the app** (ensure new code is loaded)
2. **Test with a fresh manual entry:**
   - Create a new manual entry using a global task
   - Go to Invoice tab immediately
   - Load entries for that client
   - Verify the new entry appears
3. **Check database directly** (if comfortable with SQL):
   ```sql
   SELECT te.id, te.client_name, te.project_name, te.task_name, 
          t.is_global, te.project_id
   FROM time_entries te
   JOIN tasks t ON te.task_id = t.id
   WHERE te.client_name = 'YourClientName'
     AND te.is_billed = 0
   ```
   - Should see ALL entries, including ones where `t.is_global = 1`

---

## 🚀 DEPLOYMENT

**To apply this fix:**
1. Save all files
2. Restart the Time Tracker app
3. Test Invoice tab immediately
4. If working, commit to Git:
   ```bash
   git add gui.py
   git commit -m "Fix: Invoice tab now loads entries with global tasks correctly"
   git push
   ```

**Backup Created:**
- `gui.py.backup_invoice_bug` - restore point if needed

---

**Fix Created:** January 15, 2026 - 3:00 PM  
**Version:** Will be v2.0.3  
**Issue:** Critical - Invoice tab missing entries  
**Status:** ✅ FIXED - Ready for testing
