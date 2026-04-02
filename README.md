# ⏱️ Freelance Timer Pro

Free, open source time tracking and invoicing for Windows freelancers.

**[Download the Installer](https://github.com/wujibi/FreelanceTimerPro/releases/latest)** | **[Website](https://freelancetimer.pro)**

---

## ✨ Features

- **Timer & Manual Entry** — Track time with start/stop timer or enter hours manually
- **Client Management** — Store client contacts, companies, and project details
- **Global Tasks** — Reusable tasks available across all projects (e.g., "Meeting", "Admin")
- **Flexible Billing** — Hourly rates and lump sum project support
- **PDF Invoices** — Generate professional branded invoices with your company logo
- **Email Invoicing** — Send invoices directly via Gmail
- **Excel Export** — Export time entries to .xlsx spreadsheets
- **Smart Filtering** — Filter time entries by Unbilled/Billed/All status
- **Payment Tracking** — Mark invoices as paid with payment dates
- **Google Drive Sync** — Optional sync across multiple computers
- **Themes** — Built-in color themes with live switcher

---

## 💻 Installation

**Easiest way — download the installer:**
👉 [FreelanceTimerPro_Setup_v2.0.9.exe](https://github.com/wujibi/FreelanceTimerPro/releases/latest)

Run the installer, follow the wizard, launch from Start Menu. Done.

> **Note:** Windows Defender may show a security warning for unsigned apps.
> Click "More info" → "Run anyway". This is normal for free open source software.

---

## 🛠️ Run from Source

1. **Clone the repository:**
   ```bash
   git clone https://github.com/wujibi/FreelanceTimerPro.git
   cd FreelanceTimerPro
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app:**
   ```bash
   python main.py
   ```

   **Windows shortcut/double-click option:** use `launcher.pyw` from the project root.

**Requirements:** Python 3.8+, Windows 10/11

---

## 📁 Project Structure

```
FreelanceTimerPro/
├── main.py              # Canonical application entry point
├── launcher.pyw         # Windows launcher (double-click/shortcut)
├── gui.py               # Main UI
├── models.py            # Database models
├── db_manager.py        # Database connection manager
├── invoice_generator.py # PDF generation
├── email_sender.py      # Email functionality
├── config.py            # Database path configuration
├── themes/              # Color theme modules
├── assets/              # Icons and images
└── data/                # Local database (created on first run)
```

---

## 🔧 Configuration

The app automatically stores your database locally in the `data/` folder.

**Optional Google Drive sync:** If a `My Drive/FreelanceTimerPro/data/` folder exists on your machine, the app will use that instead — syncing your data across computers automatically.

---

## 📝 Version History

See [CHANGELOG.md](CHANGELOG.md) for full version history.

**Current version:** 2.0.9 

---

## 📫 Contact & Support

- **Website:** [freelancetimer.pro](https://freelancetimer.pro)
- **Email:** support@freelancetimer.pro
- **Issues:** [GitHub Issues](https://github.com/wujibi/FreelanceTimerPro/issues)
- **Author:** Brian Hood

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

Copyright (c) 2026 Brian Hood 
