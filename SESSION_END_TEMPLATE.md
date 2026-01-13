# Session End Documentation Update Template

**Use this at the end of EVERY session where code changes were made**

---

## 📋 Checklist for AI Assistant

At the end of each session, ask the user:

> "Should I update the project documentation now?"

If yes, update these files:

---

### 1. **CHANGELOG.md** (ALWAYS update if code changed)

**Add new version section at top:**
```markdown
## [X.X.X] - YYYY-MM-DD

### Fixed
- [Describe what bugs were fixed]

### Added
- [Describe new features/files added]

### Changed
- [Describe what was modified]
- Files modified: [list files and key line numbers]

### Removed
- [Describe what was deleted]

### Technical
- Files modified: [list]
- Database schema: [changes or "No changes"]
- Dependencies: [new packages or "No new dependencies"]
- Git commit: [commit hash if pushed]
```

---

### 2. **TIMETRACKER_CONTEXT.md** (Update if significant changes)

**Update these sections:**

**"Recent Fixes" section:**
- Add date and brief description
- Keep only last 3-5 fixes (remove old ones)

**"Last Updated" footer:**
- Update date/time
- Update version number
- Update git commit hash
- Note session cost if significant

**"Known Issues" section:**
- Add new issues discovered
- Remove issues that were fixed

---

### 3. **CURRENT_STATUS.md** (Update after every session)

**Update these sections:**

**"Last Updated":**
- Current date/time

**"Recent Session Summary":**
- What was fixed
- Files modified
- Session cost
- Git commit

**"Known Issues":**
- Remove fixed issues
- Add new issues

**"Testing Status":**
- Update "Last Tested" date
- Note what was tested
- Mark tests as passed/pending

---

### 4. **Create Issue-Specific Documentation (Optional)**

If the fix was complex, create a detailed doc like:
- `MANUAL_ENTRY_FIX_COMPLETE.md`
- Include before/after code
- Explain root cause
- Document solution approach

---

## 📝 Example Session End Conversation

**AI:** "I've successfully fixed the manual entry bug. Should I update the project documentation now?"

**User:** "Yes please"

**AI:** 
- ✅ Updated `CHANGELOG.md` with v2.0.2 entry
- ✅ Updated `TIMETRACKER_CONTEXT.md` Recent Fixes section
- ✅ Updated `CURRENT_STATUS.md` with session summary
- ✅ Created `MANUAL_ENTRY_FIX_COMPLETE.md` with detailed explanation

**Documentation is now up to date!**

---

## 🚫 When NOT to Update Docs

Skip documentation updates if:
- No code changes were made (just discussion/planning)
- Only read files to answer questions
- Only helped with Git commands
- Session was exploratory/investigative

---

## ✅ Benefits of This System

1. **Always current** - Docs reflect actual state
2. **Historical record** - Know what changed when
3. **Smooth handoffs** - Next AI session has accurate context
4. **Troubleshooting** - Easy to see what might have broken
5. **Version tracking** - Clear progression of features

---

**Created:** January 13, 2026  
**Purpose:** Ensure documentation stays current after every work session
