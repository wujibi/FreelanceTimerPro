# 🚀 QUICK TEST - Invoice Bug Fix

## What Was Wrong?
**Invoice tab was NOT showing entries that used GLOBAL TASKS.**

## What I Fixed?
Changed 5 SQL queries in `gui.py` to use the correct table join.

---

## ⚡ QUICK TEST (30 seconds)

1. **Close and restart** the Time Tracker app
2. **Go to Invoice tab**
3. **Select your client** (the one with 3 entries)
4. **Select "All Projects"**
5. **Click "LOAD ENTRIES"**

**✅ SUCCESS if you see ALL 3 entries now!**

---

## 📄 Detailed Test Document

See `INVOICE_BUG_FIX.md` for:
- Full explanation of the bug
- Why it happened
- Complete testing instructions
- Database structure details

---

**Fix Status:** ✅ Ready to test  
**Files Changed:** `gui.py` (5 lines)  
**Backup:** `gui.py.backup_invoice_bug`
