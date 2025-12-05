Here's a comprehensive project guidance file for your knowledge base:

**project_guidance.md**

```markdown
# Time Tracker Pro - Development Guidance

## Current Status (as of development session)
- ✅ Core timer functionality working (Client → Project → Task flow)
- ✅ Invoice generation and PDF export working
- ✅ All CRUD operations functional (Clients, Projects, Tasks, Time Entries)
- ✅ Manual time entry working
- ✅ Company info and logo support
- ✅ Database operations stable

## Code Change Protocol

### IMPORTANT: One Change at a Time Rule
When providing code modifications, follow this protocol:

1. **Single Change Per Response**: Only provide ONE modification at a time
2. **Wait for Confirmation**: User will test and confirm before next change
3. **Clear Instructions**: Specify exactly which file and which method/section
4. **Change Format**:
   ```
   File: filename.py
   Method/Section: method_name() or "Section Description"
   Action: Replace/Add/Update
   Location: Line numbers or "after method X" or "before method Y"
   ```

### Example Change Format:
```
File: gui.py
Method: start_timer()  
Action: Replace
Location: Lines 245-267
Instructions: Replace the entire start_timer method with this updated version
```

## Future Development Roadmap

### High Priority Features
1. **One-Click Launch**
   - Create Windows batch file (.bat) for easy launching
   - Alternative: Create desktop shortcut
   - Consider Python executable creation (pyinstaller)

2. **UI/UX Improvements**
   - Modern color scheme
   - Better fonts and spacing
   - Icons for buttons
   - Status indicators
   - Progress bars for long operations
   - Tooltips for user guidance

### Medium Priority Features
3. **Enhanced Time Tracking**
   - Pause/resume timer functionality
   - Time tracking reminders/notifications
   - Automatic idle detection
   - Daily/weekly time summaries

4. **Reporting Enhancements**
   - Time reports by client/project/date range
   - Productivity analytics
   - Billable vs non-billable time tracking
   - Export reports to CSV/Excel

5. **Invoice Improvements**
   - Multiple invoice templates
   - Custom invoice numbering schemes
   - Invoice status tracking (sent/paid/overdue)
   - Email integration for sending invoices
   - Late payment reminders

### Low Priority Features
6. **Data Management**
   - Backup/restore functionality
   - Data export/import
   - Multiple database support
   - Cloud sync capabilities

7. **Advanced Features**
   - Multi-user support
   - Time approval workflows
   - Integration with accounting software
   - Mobile companion app
   - API for external integrations

## Current File Structure
```
time_tracker/
├── main.py              # Application entry point
├── database.py          # Database setup and connections
├── models.py           # Data models and business logic
├── gui.py              # Main GUI application (largest file)
├── invoice_generator.py # PDF invoice generation
├── time_tracker.db     # SQLite database file
└── requirements.txt    # Python dependencies
```

## Development Environment
- **IDE**: PyCharm Community (preferred)
- **Python Version**: 3.13
- **Key Dependencies**: 
  - tkinter (built-in GUI)
  - reportlab (PDF generation)
  - sqlite3 (built-in database)

## Known Issues to Monitor
- Rainbow Brackets plugin needed in PyCharm for code clarity
- Watch for indentation issues when copying code
- Database queries may need index optimization as data grows
- PDF generation error handling could be enhanced

## Code Quality Guidelines
- Follow PEP 8 style guidelines
- Use descriptive variable names
- Add docstrings to new methods
- Handle exceptions gracefully
- Test each change thoroughly before proceeding

## Debugging Tips
- Use PyCharm's debugger for complex issues
- Check console output for error messages
- Test with sample data before production use
- Keep backup of working database file

## Next Session Preparation
1. Upload all current project files to knowledge base
2. Start fresh chat with clear problem statement
3. Reference this guidance file for change protocol
4. Specify which feature/issue to work on next

## Change Log Template (for tracking progress)
```
Date: YYYY-MM-DD
Feature/Fix: Description
Files Modified: list of files
Status: Complete/In Progress/Testing
Notes: Any important details
```
```

