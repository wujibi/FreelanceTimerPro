# Time Tracker Pro - Public Release Checklist

**Target Release Date:** TBD  
**Current Version:** 2.0.7 (Private)  
**Target Public Version:** 3.0.0 or 1.0.0 (Public)

---

## 🧹 CLEANUP - Remove Before Public Release

### Files to DELETE:
- [ ] `.idea/` folder (PyCharm IDE settings)
- [ ] `.idea_backup/` folder
- [ ] `__pycache__/` folder (Python cache)
- [ ] `cleanup_before_push.py` (dev script)
- [ ] `cleanup_junk_files.py` (dev script)
- [ ] `DELETE_OBSOLETE_FILES.bat` (dev script)
- [ ] `update_load_invoiceable.py` (dev script)
- [ ] `git_commit_v2.0.7.bat` (version-specific script)
- [ ] `launch_timetracker.bat - Shortcut.lnk` (local shortcut)
- [ ] `3.6.0)` (orphaned file?)
- [ ] `SESSION_END_TEMPLATE.md` (internal doc)
- [ ] `TIMETRACKER_CONTEXT.md` (Claude AI instructions)
- [ ] `CURRENT_STATUS.md` (internal status)
- [ ] `Time Tracker Pro V2 - Theme-Stylesheet System Implementation.md` (planning doc)

### Files to KEEP but REVIEW:
- [ ] `.gitignore` - Add more exclusions?
- [ ] `data/` folder - Should be empty for distribution
- [ ] `.venv/` - Should NOT be in repo (check .gitignore)
- [ ] `config.py` - Remove any hardcoded paths/secrets
- [ ] `GIT_USAGE.md` - Keep or remove? (for contributors)

### New .gitignore entries needed:
```
# IDE
.idea/
.vscode/
*.pyc
__pycache__/

# Virtual environments
.venv/
venv/
env/

# User data
data/time_tracker.db
data/*.db

# OS files
.DS_Store
Thumbs.db
desktop.ini

# Dev scripts
*_backup/
cleanup_*.py
SESSION_*.md
TIMETRACKER_CONTEXT.md
CURRENT_STATUS.md
```

---

## 📄 LEGAL & LICENSING

### Required Files:
- [ ] **LICENSE.txt** - Choose license type:
  - MIT License (most permissive, recommended)
  - Apache 2.0 (patent protection)
  - GPL v3 (copyleft, requires open source)
  - Proprietary (if going paid route)
  
- [ ] **PRIVACY_POLICY.md** - Data handling disclosure:
  - What data is collected (local only, no cloud)
  - Where data is stored (user's local machine)
  - No telemetry/tracking statement
  - Google Drive sync is optional
  
- [ ] **TERMS_OF_SERVICE.md** (if applicable)
  - Usage terms
  - Warranty disclaimer
  - Liability limitations

### Code Headers:
- [ ] Add copyright notice to all Python files:
```python
"""
Time Tracker Pro
Copyright (c) 2026 [Your Name/Company]
Licensed under [LICENSE TYPE]
"""
```

---

## 📱 APP IMPROVEMENTS

### New Tab: About/Help/Manual
- [ ] **About Tab** with sections:
  - [ ] App name, version, copyright
  - [ ] Brief description
  - [ ] Credits/attribution
  - [ ] License information
  - [ ] Website link (your new domain!)
  - [ ] GitHub repository link
  - [ ] Contact/support email
  - [ ] Check for updates button
  
- [ ] **Help Tab** (or combined with About):
  - [ ] Quick start guide
  - [ ] Feature overview
  - [ ] Common tasks walkthrough
  - [ ] Troubleshooting section
  - [ ] Link to full manual (online docs?)
  
- [ ] **User Manual** (external):
  - [ ] Full PDF documentation
  - [ ] Online documentation website
  - [ ] Video tutorials (optional)

### UI Polish:
- [ ] App icon in title bar (already have timetracker.ico)
- [ ] **New icon images** (user has generated new ones)
- [ ] Splash screen on startup (optional)
- [ ] First-run wizard/setup
- [ ] Sample data option for new users
- [ ] **Theme/Stylesheet System** - CSS-like customization
  - [ ] Implement theme switcher (see planning doc)
  - [ ] Create professional_gray.py starter theme
  - [ ] Theme folder structure + README
  - [ ] Allow users to customize colors
- [ ] Dark mode theme (future)
- [ ] **HTML preview rendering** (tkinterweb library)

---

## 🌐 BRANDING & WEB PRESENCE

### Your New Domain:
- [ ] **Domain name:** _________________________
- [ ] Website setup (landing page)
- [ ] Documentation hosting
- [ ] Download page
- [ ] Support/contact form
- [ ] Blog/changelog page
- [ ] Email: support@yourdomain.com

### Marketing Materials:
- [ ] Professional logo design
- [ ] Screenshots for website
- [ ] Demo video/GIF
- [ ] Feature comparison chart (Free vs Pro)
- [ ] Testimonials section

---

## 🔧 INSTALLER CREATION

### Windows Installer:
- [ ] PyInstaller EXE generation
- [ ] Inno Setup installer script
- [ ] Start menu shortcuts
- [ ] Desktop shortcut option
- [ ] File associations (.ttp files?)
- [ ] Uninstaller
- [ ] Auto-update mechanism
- [ ] Code signing certificate (optional but recommended)

### Mac Installer:
- [ ] PyInstaller app bundle
- [ ] DMG creation
- [ ] Apple Developer account
- [ ] Code signing
- [ ] Notarization
- [ ] Mac App Store submission (optional)

### Linux:
- [ ] AppImage (easiest)
- [ ] .deb package (Debian/Ubuntu)
- [ ] .rpm package (Fedora/RedHat)
- [ ] Snap package
- [ ] Flatpak

---

## 🆓 FREE vs 💰 PAID VERSIONS

### Feature Split Decision:
- [ ] **FREE Features** (what's included):
  - [ ] Time tracking (unlimited)
  - [ ] Client/Project/Task management
  - [ ] Invoice generation (PDF)
  - [ ] Email invoices (Gmail only)
  - [ ] Excel export
  - [ ] Local database
  
- [ ] **PAID/PRO Features** (premium):
  - [ ] All SMTP providers (Outlook, custom)
  - [ ] Cloud sync (Dropbox, OneDrive, etc.)
  - [ ] Advanced reporting
  - [ ] Custom branding on invoices
  - [ ] Team collaboration
  - [ ] Mobile app access
  - [ ] Priority support
  - [ ] Custom themes

### Implementation:
- [ ] License key system
- [ ] Activation mechanism
- [ ] Trial period (30 days?)
- [ ] Feature gating in code
- [ ] Upgrade prompts in UI
- [ ] Payment integration (Stripe, PayPal, Gumroad)

---

## 🔄 AUTO-UPDATE SYSTEM

### Update Checker:
- [ ] Version check API endpoint
- [ ] "Check for Updates" button in About tab
- [ ] Auto-check on startup (optional, with setting)
- [ ] Download new version button
- [ ] Release notes display
- [ ] Silent update option

### Distribution:
- [ ] GitHub Releases (for open source)
- [ ] Your website download page
- [ ] Update manifest JSON file
- [ ] Semantic versioning (X.Y.Z)

---

## 🧪 TESTING & QA

### Pre-Release Testing:
- [ ] Fresh install test (no existing data)
- [ ] Migration test (upgrade from older version)
- [ ] Uninstall test (clean removal)
- [ ] Windows 10 testing
- [ ] Windows 11 testing
- [ ] Mac testing (if applicable)
- [ ] Multiple screen resolutions
- [ ] High DPI displays
- [ ] Non-admin user testing

### Beta Testing:
- [ ] Recruit 5-10 beta testers
- [ ] Beta feedback form
- [ ] Bug tracking system (GitHub Issues)
- [ ] Beta period (2-4 weeks)

---

## 📚 DOCUMENTATION

### Essential Docs:
- [ ] **README.md** (public version):
  - [ ] Professional description
  - [ ] Feature list
  - [ ] Screenshots
  - [ ] Installation instructions
  - [ ] Quick start guide
  - [ ] Links to documentation
  - [ ] Support information
  
- [ ] **CHANGELOG.md** (already exists, review for public)
- [ ] **CONTRIBUTING.md** (if open source)
- [ ] **FAQ.md**
- [ ] **TROUBLESHOOTING.md**

### Online Documentation:
- [ ] GitHub Wiki or dedicated docs site
- [ ] Getting Started guide
- [ ] Feature tutorials
- [ ] API documentation (if applicable)
- [ ] Video tutorials

---

## 🚀 LAUNCH STRATEGY

### Pre-Launch:
- [ ] Build email list (landing page)
- [ ] Social media accounts (Twitter, LinkedIn, etc.)
- [ ] Product Hunt submission plan
- [ ] Reddit posts (r/productivity, r/selfhosted, etc.)
- [ ] Hacker News submission
- [ ] Press release
- [ ] Influencer outreach

### Launch Day:
- [ ] Final testing
- [ ] Deploy website
- [ ] Release installers
- [ ] Social media announcements
- [ ] Email list notification
- [ ] Community posts
- [ ] Monitor feedback

### Post-Launch:
- [ ] Respond to feedback
- [ ] Fix critical bugs quickly
- [ ] Plan first update
- [ ] Gather testimonials
- [ ] Analytics review

---

## ✅ FINAL CHECKLIST

### Before Going Public:
- [ ] All dev files removed
- [ ] License added
- [ ] Privacy policy added
- [ ] About tab implemented
- [ ] Help system implemented
- [ ] Installer created and tested
- [ ] Website live
- [ ] Support email working
- [ ] Documentation complete
- [ ] Beta testing done
- [ ] All critical bugs fixed
- [ ] Code reviewed
- [ ] Backups created
- [ ] Domain email configured
- [ ] SSL certificate installed (website)
- [ ] Analytics set up (optional)

---

## 🎯 PRIORITY ORDER

### Phase 1 - Cleanup (Do First):
1. Review/delete dev files
2. Update .gitignore
3. Remove hardcoded paths/secrets
4. Add LICENSE.txt
5. Clean up README.md for public

### Phase 2 - Essential Features:
1. About/Help tab
2. License key system (if going paid)
3. Auto-update checker
4. First-run wizard

### Phase 3 - Installers:
1. Windows installer (PyInstaller + Inno Setup)
2. Mac installer (if needed)
3. Code signing

### Phase 4 - Web Presence:
1. Set up domain/website
2. Create documentation
3. Support email configuration
4. Marketing materials

### Phase 5 - Launch:
1. Beta testing
2. Final polish
3. Public release
4. Marketing push

---

## 📝 NOTES

**Your New Domains:** 
- freelancetimer.pro (primary option?)
- freelancetimer.net (backup option?)
- Decision pending - both registered

**Target Launch Date:** _________________________

**Pricing Model:** 
- [ ] Completely free
- [ ] Freemium (free + paid)
- [ ] One-time purchase
- [ ] Subscription
- [ ] Open source + donations

**Support Strategy:**
- [ ] Email support
- [ ] Community forum
- [ ] Discord/Slack
- [ ] GitHub Issues
- [ ] Documentation only

---

**Last Updated:** February 3, 2026  
**Status:** Planning Phase

---

## 🔔 PENDING DECISIONS

- [ ] **App Name Change** - Confirm in other chat, then find/replace across all files
- [ ] **Domain Choice** - freelancetimer.pro vs .net
- [ ] **License Type** - Research needed (MIT, Apache, GPL, Proprietary)
- [ ] **Pricing Model** - Free, Freemium, Paid?
- [ ] **Theme System** - When to implement (postponed until after invoicing)

**PyCharm Name Change Process:**
1. Ctrl+Shift+R (Replace in Files)
2. Search: "Time Tracker Pro" (and variations)
3. Replace: "[New Name]"
4. Review matches before replacing
5. Update file names manually (timetracker.ico, etc.)
6. Test thoroughly after rename
