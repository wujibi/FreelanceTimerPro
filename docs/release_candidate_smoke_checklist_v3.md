# FreelanceTimerPro V3 Release-Candidate Smoke Checklist

Use this checklist for a fast confidence pass before a V3 release build.

## Scope

- UI mode: CustomTkinter default (`python main.py`)
- Data source: Dev DB copy (not live)
- Window size baseline: `1200x760`
- Themes to spot-check: Light + Dark

## Preflight

- Pull latest `FreelanceTimerPro-V3`.
- Start app and confirm no startup traceback.
- Confirm tabs load: `Timer`, `Clients`, `Projects`, `Tasks`, `Time Entries`, `Company`, `Invoices`, `Email`.

## Core Functional Smoke

### 1) Timer (Active)

- Select client/project/task and start timer.
- Let it run >= 10 seconds, then stop.
- Confirm success dialog and entry appears in `Time Entries`.
- Confirm daily totals update in Timer view.

### 2) Timer (Manual Entry)

- Add a valid Start/End entry for today.
- Add a valid Decimal Hours entry for today.
- Confirm both entries appear in `Time Entries`.
- Confirm daily totals update and no validation regressions.

### 3) Master Data CRUD

- `Clients`: create, update, delete a test record.
- `Projects`: create, update, delete a test record under a test client.
- `Tasks`: create and update task; verify delete guard for billed/invoiced tasks still warns and blocks.

### 4) Time Entries

- Filter `Unbilled`, `Billed`, `All` and verify counts look correct.
- Edit one entry and verify updated values persist.
- Delete one unbilled entry and verify removal.
- Export to Excel and confirm file is created.

### 5) Invoicing Path

- From unbilled entries, generate invoice.
- Open preview and verify line items + totals.
- Export PDF and confirm successful output.

### 6) Email + Company

- Verify Company fields save and reload.
- Verify Email template/send flow opens and validates inputs.

## UI Consistency Spot-Check (Quick)

- Confirm no clipped controls at `1200x760`.
- Confirm action buttons remain visible on all tabs.
- Confirm tree headers/columns are readable and resizable.
- Confirm light/dark theme contrast is acceptable for labels, inputs, and tables.

## Go / No-Go Gate

## Go

- No crashes or tracebacks in all steps above.
- Timer + Manual + Invoice Preview + PDF path all pass.
- CRUD operations succeed with expected guards.
- No blocking visual defect (missing controls, unusable text contrast).

## No-Go

- Any data-loss behavior, crash, or unhandled exception.
- Timer entry creation fails for valid selections.
- Invoice preview/PDF path fails.
- Any tab has blocked workflow due to layout/render regression.

## Triage Notes Template

- Build/date:
- Scenario:
- Expected:
- Actual:
- Severity: blocker / high / medium / low
- Repro steps:
- Screenshot path:

