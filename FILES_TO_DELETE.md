# Files to Delete Before Git Push

## 🗑️ Temporary/Utility Scripts (DELETE)
- ✅ `cleanup_junk_files.py` - One-time cleanup script
- ✅ `create_icon.py` - Already created icon, don't need script
- ✅ `fix_pycharm.bat` - PyCharm-specific utility
- ✅ `create_desktop_shortcut.vbs` - Manual shortcut creation
- ✅ `create_start_menu_shortcut.vbs` - Manual shortcut creation

## 📋 Temporary Documentation (DELETE)
- ✅ `git_push_instructions.md` - Temporary instructions
- ✅ `MANUAL_ENTRY_FIX_COMPLETE.md` - Old fix docs (info in CHANGELOG)
- ✅ `COMPLETE_VERIFICATION_TEST.md` - Testing doc (can delete after testing)
- ✅ `QUICK_TEST_INVOICE_FIX.md` - Testing doc (can delete after testing)
- ✅ `FIX_LAPTOP_SHORTCUT.md` - Troubleshooting doc (one-time issue)
- ✅ `INVOICE_BUG_FIX.md` - Detailed fix explanation (info will be in CHANGELOG)

## 💾 Backup Files (DELETE)
- ✅ `gui.py.backup_invoice_bug` - Temporary backup

## 🔗 Shortcut Files (DELETE from repo, keep local)
- ✅ `launch_timetracker.bat - Shortcut.lnk` - Windows shortcut

## 📁 Directories to Keep
- ✅ `.git` - Keep
- ✅ `.idea` - Keep (if using PyCharm)
- ✅ `.idea_backup` - DELETE (unnecessary)
- ✅ `.venv` - Keep (should be in .gitignore)
- ✅ `assets` - Keep
- ✅ `data` - Keep (should be in .gitignore)
- ✅ `__pycache__` - Keep (should be in .gitignore)

## ✅ Core Files to KEEP
- CHANGELOG.md - Essential
- config.py - Core
- CURRENT_STATUS.md - Essential
- db_manager.py - Core
- gui.py - Core
- invoice_generator.py - Core
- launcher.pyw - Core
- launch_timetracker.bat - Core launcher
- launch_timetracker.sh - Core launcher (Linux/Mac)
- main.py - Core
- models.py - Core
- README.md - Essential
- requirements.txt - Essential
- SESSION_END_TEMPLATE.md - Essential (AI assistant reference)
- timetracker.ico - Core asset
- TIMETRACKER_CONTEXT.md - Essential (AI assistant reference)
- .gitignore - Essential

---

## Summary:
**DELETE:** 13 files
**KEEP:** All core application files and essential docs
