# ⏰ Time Tracker Pro v2.0

Professional desktop time tracking and invoicing application built with Python and tkinter.

## ✨ Key Features

- **Timer & Manual Entry** - Track time with start/stop timer or enter hours manually (decimal format supported)
- **Global Tasks** - Create reusable tasks available across all projects (e.g., "Meeting", "Admin")
- **Client Management** - Store client contacts, companies, and project details
- **Flexible Billing** - Support for hourly rates and lump sum projects
- **PDF Invoices** - Generate professional branded invoices with company logo
- **Excel Export** - Export time entries to .xlsx spreadsheets with professional formatting
- **Smart Filtering** - Filter time entries by Unbilled/Billed/All status
- **Payment Tracking** - Mark invoices as paid with payment dates
- **Google Drive Sync** - Sync database across multiple computers
- **Hierarchical Views** - Organized display of tasks and time entries by Client → Project → Task

## 🚀 Quick Start

1. **Install Python 3.8+** if not already installed
2. **Clone repository:**
   ```bash
   git clone https://github.com/wujibi/TimeTrackerApp.git
   cd TimeTrackerApp
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
4. **Run application:**
   ```bash
   python main.py
   
## 📖 Basic Workflow
1. **Company Info** - Set up your business details and logo
2. **Clients** - Add client contact information
3. **Projects** - Create projects with hourly or lump sum billing
4. **Tasks**- Define tasks (project-specific or global)
5. **Timer** - Track time or add manual entries
6. **Invoices** - Generate PDF invoices from unbilled hours
7. **Billed Invoices** - Track payment status

## 📁 Project Structure
- main.py / launcher.pyw - Application entry points
- gui.py - Main UI (4100+ lines)
- models.py - Database models
- db_manager.py - Database connection manager
- invoice_generator.py - PDF generation
- config.py - Database path configuration
- data/time_tracker.db - SQLite database

## 🔧 Configuration
Edit config.py to set database location:

- Default: Google Drive sync location
- Fallback: Local ./data/time_tracker.db

## 📝 Recent Updates (v2.0.1)
- **Excel Export** - Export time entries to spreadsheets (filter or selection based)
- New clock icon across all application instances
- Time entries filter (Unbilled/Billed/All)
- Global tasks feature with hierarchical display
- Enhanced timer integration

See [CHANGELOG.md](CHANGELOG.md) for full version history.

## 📫 Contact
Brian Hood - briahood@gmail.com

License: Proprietary - All Rights Reserved
