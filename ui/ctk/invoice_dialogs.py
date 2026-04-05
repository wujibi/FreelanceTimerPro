"""Invoice preview and email dialogs for the CustomTkinter shell (ttk Toplevels)."""

from __future__ import annotations

import os
import sqlite3
import tempfile
from collections.abc import Callable
from datetime import datetime, timedelta
from tkinter import filedialog, messagebox, ttk

import tkinter as tk

import customtkinter as ctk

from ui.ctk.ttk_theme import (
    apply_ctk_aligned_ttk_theme,
    embedded_tk_frame_bg,
    get_tree_ui_font,
    get_tree_ui_font_bold,
)
from ui_helpers import center_dialog, center_dialog_clamped


def _default_invoice_colors() -> dict[str, str]:
    return {"text": "#13100f", "text_secondary": "#666666"}


def show_email_invoice_dialog_ctk(
    root: tk.Misc,
    parent_dialog: tk.Toplevel,
    db,
    company_model,
    client_name: str,
    client_email: str,
    client_id: int,
    entry_ids: list[int],
    invoice_items: list,
    total_amount: float,
    start_date: datetime,
    end_date: datetime,
    refresh_time_entries: Callable[[], None],
    load_invoiceable_entries: Callable[[], None],
    on_billing_updated: Callable[[], None] | None = None,
) -> None:
    """Send invoice email (same flow as InvoiceRuntimeMixin.show_email_invoice_dialog)."""
    from email_sender import EmailSender, EmailTemplate

    email_dialog = tk.Toplevel(parent_dialog)
    email_dialog.title("Email Invoice")
    email_dialog.geometry("600x700")
    email_dialog.transient(parent_dialog)
    email_dialog.grab_set()

    header_frame = ttk.Frame(email_dialog)
    header_frame.pack(fill="x", padx=20, pady=20)
    ttk.Label(header_frame, text="Email Invoice", font=("Arial", 16, "bold")).pack()
    ttk.Label(header_frame, text=f"To: {client_name} ({client_email})", font=("Arial", 10)).pack(pady=5)

    form_frame = ttk.LabelFrame(email_dialog, text="Email Details")
    form_frame.pack(fill="both", expand=True, padx=20, pady=10)

    ttk.Label(form_frame, text="Template:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
    template_var = tk.StringVar(value="Professional")
    template_combo = ttk.Combobox(
        form_frame,
        textvariable=template_var,
        values=EmailTemplate.get_template_names(),
        state="readonly",
    )
    template_combo.grid(row=0, column=1, sticky="ew", padx=10, pady=5)

    ttk.Label(form_frame, text="Subject:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
    subject_entry = ttk.Entry(form_frame, width=50)
    subject_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=5)

    ttk.Label(form_frame, text="CC (optional):").grid(row=2, column=0, sticky="w", padx=10, pady=5)
    cc_entry = ttk.Entry(form_frame, width=50)
    cc_entry.grid(row=2, column=1, sticky="ew", padx=10, pady=5)
    ttk.Label(form_frame, text="Separate multiple emails with commas", font=("Arial", 8), foreground="gray").grid(
        row=3, column=1, sticky="w", padx=10
    )

    ttk.Label(form_frame, text="Message:").grid(row=4, column=0, sticky="nw", padx=10, pady=5)
    message_text = tk.Text(form_frame, height=15, wrap="word")
    message_text.grid(row=4, column=1, sticky="ew", padx=10, pady=5)
    message_scroll = ttk.Scrollbar(form_frame, orient="vertical", command=message_text.yview)
    message_text.configure(yscrollcommand=message_scroll.set)
    message_scroll.grid(row=4, column=2, sticky="ns", pady=5)
    form_frame.columnconfigure(1, weight=1)

    def update_template(*args):
        del args
        template_name = template_var.get()
        template = EmailTemplate.get_template(template_name)
        if template:
            company = company_model.get()
            invoice_number = f"INV-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            date_range = f"{start_date.strftime('%m/%d/%y')} - {end_date.strftime('%m/%d/%y')}"
            variables = {
                "client_name": client_name,
                "client_email": client_email,
                "invoice_number": invoice_number,
                "invoice_date": datetime.now().strftime("%B %d, %Y"),
                "invoice_total": f"${total_amount:.2f}",
                "payment_terms": company[7] if company and len(company) > 7 else "Net 30",
                "due_date": (datetime.now() + timedelta(days=30)).strftime("%B %d, %Y"),
                "date_range": date_range,
                "company_name": company[1] if company else "Your Company",
                "company_email": company[4] if company and len(company) > 4 else "",
                "company_phone": company[3] if company and len(company) > 3 else "",
                "company_website": company[6] if company and len(company) > 6 else "",
            }
            subject = EmailTemplate.render_template(template["subject"], variables)
            body = EmailTemplate.render_template(template["body"], variables)
            subject_entry.delete(0, tk.END)
            subject_entry.insert(0, subject)
            message_text.delete("1.0", tk.END)
            message_text.insert("1.0", body)

    template_combo.bind("<<ComboboxSelected>>", update_template)
    update_template()

    button_frame = ttk.Frame(email_dialog)
    button_frame.pack(fill="x", padx=20, pady=20)

    def send_email():
        try:
            email_settings = db.get_email_settings()
            if not email_settings:
                messagebox.showerror("Error", "Email settings not found")
                return

            smtp_server = email_settings[1]
            smtp_port = email_settings[2]
            email_address = email_settings[3]
            email_password = email_settings[4]
            from_name = email_settings[5] if len(email_settings) > 5 else None
            sender = EmailSender(smtp_server, smtp_port, email_address, email_password)

            invoice_number = f"INV-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            temp_dir = tempfile.gettempdir()
            pdf_path = os.path.join(temp_dir, f"{invoice_number}.pdf")

            invoice_data = {
                "client_id": client_id,
                "client_name": client_name,
                "entry_ids": entry_ids,
                "items": invoice_items,
                "total": total_amount,
                "start_date": start_date,
                "end_date": end_date,
            }

            from invoice_generator import InvoiceGenerator

            generator = InvoiceGenerator(db)
            generator.generate_pdf(invoice_data, pdf_path, invoice_number)
            subject = subject_entry.get().strip()
            body_html = message_text.get("1.0", tk.END).strip()

            cc_addresses = None
            cc_text = cc_entry.get().strip()
            if cc_text:
                cc_addresses = [email.strip() for email in cc_text.split(",")]

            success, msg = sender.send_email(
                to_address=client_email,
                subject=subject,
                body_html=body_html,
                attachment_path=pdf_path,
                cc_addresses=cc_addresses,
                from_name=from_name,
            )

            try:
                os.remove(pdf_path)
            except Exception:
                pass

            if success:
                if messagebox.askyesno(
                    "Email Sent!",
                    f"Invoice emailed successfully to {client_email}!\n\nWould you like to mark these time entries as BILLED now?",
                ):
                    invoice_date = datetime.now()
                    cursor = db.conn.cursor()
                    placeholders = ",".join(["?" for _ in entry_ids])
                    cursor.execute(
                        f"""
                        UPDATE time_entries
                        SET is_billed = 1,
                            invoice_number = ?,
                            billing_date = ?
                        WHERE id IN ({placeholders})
                    """,
                        [invoice_number, invoice_date.strftime("%Y-%m-%d")] + entry_ids,
                    )
                    db.conn.commit()
                    db.save_billing_history(invoice_data, invoice_number, None)
                    refresh_time_entries()
                    load_invoiceable_entries()
                    if on_billing_updated:
                        on_billing_updated()
                    messagebox.showinfo(
                        "Success",
                        f"Invoice #{invoice_number} sent and {len(entry_ids)} entries marked as billed!",
                    )

                email_dialog.destroy()
                parent_dialog.destroy()
            else:
                messagebox.showerror("Send Failed", msg)

        except Exception as e:
            import traceback

            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to send email:\n\n{str(e)}")

    ttk.Button(button_frame, text="Send Invoice", command=send_email).pack(side="right", padx=5)
    ttk.Button(button_frame, text="Cancel", command=email_dialog.destroy).pack(side="right", padx=5)


def show_invoice_preview_dialog_ctk(
    root: tk.Misc,
    db,
    client_model,
    company_model,
    client_id: int | None,
    client_name: str,
    entry_ids: list[int],
    *,
    colors: dict[str, str] | None = None,
    refresh_time_entries: Callable[[], None],
    load_invoiceable_entries: Callable[[], None],
    open_edit_time_entry: Callable[[int], None],
    on_billing_updated: Callable[[], None] | None = None,
) -> None:
    """Invoice preview / create PDF (adapted from InvoiceRuntimeMixin.show_invoice_preview_dialog)."""
    cols = colors or _default_invoice_colors()

    # Keep ttk Treeview/Heading colors in sync with CTk appearance (Windows can look blank if style drifts).
    apply_ctk_aligned_ttk_theme(root)

    preview_dialog = tk.Toplevel(root)
    preview_dialog.title(f"Invoice Preview - {client_name}")
    host_bg = embedded_tk_frame_bg()
    preview_dialog.configure(bg=host_bg)
    preview_dialog.minsize(620, 500)
    # Default fits most laptops; clamped to screen so height never exceeds usable work area.
    center_dialog_clamped(root, preview_dialog, 760, 620)

    conn = db.conn
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    placeholders = ",".join(["?" for _ in entry_ids])
    cursor.execute(
        f"""
        SELECT te.id as entry_id, te.start_time, te.duration_minutes, te.description,
               p.name as project_name, p.hourly_rate as project_rate, p.is_lump_sum as project_lump_sum,
               p.lump_sum_amount as project_lump_amount,
               t.name as task_name, t.hourly_rate as task_rate, t.is_lump_sum as task_lump_sum,
               t.lump_sum_amount as task_lump_amount
        FROM time_entries te
        JOIN tasks t ON te.task_id = t.id
        JOIN projects p ON te.project_id = p.id
        WHERE te.id IN ({placeholders})
    """,
        entry_ids,
    )

    entries = cursor.fetchall()
    conn.row_factory = None

    project_groups: dict = {}
    for entry in entries:
        project_name = entry["project_name"]
        task_name = entry["task_name"]

        if project_name not in project_groups:
            project_groups[project_name] = {"tasks": {}, "subtotal": 0}

        if task_name not in project_groups[project_name]["tasks"]:
            project_groups[project_name]["tasks"][task_name] = {
                "minutes": 0,
                "rate": entry["task_rate"] or entry["project_rate"],
                "is_lump_sum": entry["task_lump_sum"] or entry["project_lump_sum"],
                "lump_sum_amount": entry["task_lump_amount"] or entry["project_lump_amount"],
            }

        project_groups[project_name]["tasks"][task_name]["minutes"] += entry["duration_minutes"] or 0

    invoice_items: list = []
    total_amount = 0.0
    total_hours = 0.0

    for project_name, project_data in project_groups.items():
        invoice_items.append(
            {
                "description": f"**{project_name}**",
                "quantity": "",
                "rate": "",
                "amount": "",
                "is_header": True,
            }
        )

        project_subtotal = 0.0
        for task_name, task_data in project_data["tasks"].items():
            hours = task_data["minutes"] / 60.0
            total_hours += hours

            if task_data["is_lump_sum"]:
                amount = task_data["lump_sum_amount"]
                invoice_items.append(
                    {
                        "description": f"  • {task_name}",
                        "quantity": "1",
                        "rate": f"${amount:.2f}",
                        "amount": amount,
                        "is_task": True,
                    }
                )
            else:
                amount = hours * (task_data["rate"] or 0)
                invoice_items.append(
                    {
                        "description": f"  • {task_name}",
                        "quantity": f"{hours:.2f} hrs",
                        "rate": f"${task_data['rate']:.2f}/hr",
                        "amount": amount,
                        "is_task": True,
                    }
                )

            project_subtotal += amount

        invoice_items.append(
            {
                "description": f"  {project_name} Subtotal",
                "quantity": "",
                "rate": "",
                "amount": project_subtotal,
                "is_subtotal": True,
            }
        )
        total_amount += project_subtotal

    start_dates = [datetime.fromisoformat(e["start_time"]) for e in entries]
    start_date = min(start_dates) if start_dates else datetime.now()
    end_date = max(start_dates) if start_dates else datetime.now()

    preview_state: dict = {
        "current_invoice_data": {
            "client_id": client_id,
            "client_name": client_name,
            "entry_ids": entry_ids,
            "items": invoice_items,
            "total": total_amount,
            "start_date": start_date,
            "end_date": end_date,
        }
    }

    header_frame = ttk.Frame(preview_dialog)

    ttk.Label(header_frame, text="INVOICE PREVIEW", font=("Arial", 16, "bold")).pack()
    ttk.Label(header_frame, text=f"Client: {client_name}", font=("Arial", 12)).pack(pady=5)
    ttk.Label(header_frame, text=f"Date: {datetime.now().strftime('%B %d, %Y')}", font=("Arial", 10)).pack()

    items_frame = ttk.LabelFrame(preview_dialog, text="Invoice Items")

    # Host ttk in a plain tk.Frame (same pattern as Invoices tab) so pack/expand reserves space reliably on Windows.
    tree_host = tk.Frame(items_frame, bg=host_bg, highlightthickness=0)
    tree_host.pack(fill="both", expand=True, padx=4, pady=4)

    items_tree = ttk.Treeview(
        tree_host, columns=("Description", "Quantity", "Rate", "Amount"), show="headings"
    )
    items_tree.heading("Description", text="Description")
    items_tree.heading("Quantity", text="Quantity")
    items_tree.heading("Rate", text="Rate")
    items_tree.heading("Amount", text="Amount")
    items_tree.column("Description", width=350)
    items_tree.column("Quantity", width=100)
    items_tree.column("Rate", width=100)
    items_tree.column("Amount", width=100)

    for item in invoice_items:
        if item.get("is_header"):
            items_tree.insert("", "end", values=(item["description"].replace("**", ""), "", "", ""), tags=("header",))
        elif item.get("is_subtotal"):
            items_tree.insert(
                "", "end", values=(item["description"], "", "", f"${item['amount']:.2f}"), tags=("subtotal",)
            )
        else:
            amount_display = f"${item['amount']:.2f}" if isinstance(item["amount"], (int, float)) else ""
            items_tree.insert("", "end", values=(item["description"], item["quantity"], item["rate"], amount_display))

    items_tree.tag_configure("header", font=get_tree_ui_font_bold(root), background="#e8f4f8")
    items_tree.tag_configure("subtotal", font=get_tree_ui_font_bold(root), background="#f0f0f0")
    # Cap visible rows so Treeview min height + header/totals/buttons fits the dialog; use scrollbar for the rest.
    visible_rows = max(5, min(12, len(invoice_items) + 2))
    items_tree.configure(height=visible_rows)
    vsb = ttk.Scrollbar(tree_host, orient="vertical", command=items_tree.yview)
    items_tree.configure(yscrollcommand=vsb.set)
    items_tree.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")

    total_frame = ttk.Frame(preview_dialog)
    ttk.Label(
        total_frame,
        text=f"Total Hours: {total_hours:.2f} hrs",
        font=("Arial", 12, "bold"),
        foreground=cols["text_secondary"],
    ).pack(side="left")
    ttk.Label(total_frame, text=f"TOTAL: ${total_amount:.2f}", font=("Arial", 14, "bold")).pack(side="right")

    button_frame = ctk.CTkFrame(preview_dialog, fg_color="transparent")
    _btn_font = ctk.CTkFont(size=13)
    _btn_h = 34

    def create_invoice():
        if messagebox.askyesno(
            "Confirm",
            f"Create invoice for ${total_amount:.2f}?\n\nThis will mark all selected time entries as BILLED.",
        ):
            invoice_date = datetime.now()
            invoice_number = f"INV-{invoice_date.strftime('%Y%m%d-%H%M%S')}"

            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                initialfile=f"Invoice_{client_name.replace(' ', '_')}_{invoice_number}.pdf",
            )

            if filename:
                try:
                    from invoice_generator import InvoiceGenerator

                    generator = InvoiceGenerator(db)
                    data = preview_state["current_invoice_data"]
                    generator.generate_pdf(data, filename, invoice_number)

                    update_placeholders = ",".join(["?" for _ in entry_ids])
                    cursor2 = db.conn.cursor()
                    cursor2.execute(
                        f"""
                        UPDATE time_entries
                        SET is_billed = 1,
                            invoice_number = ?,
                            billing_date = ?
                        WHERE id IN ({update_placeholders})
                    """,
                        [invoice_number, invoice_date.strftime("%Y-%m-%d")] + entry_ids,
                    )
                    db.conn.commit()
                    db.save_billing_history(data, invoice_number, filename)

                    refresh_time_entries()
                    load_invoiceable_entries()
                    if on_billing_updated:
                        on_billing_updated()
                    preview_dialog.destroy()
                    messagebox.showinfo(
                        "Success",
                        "Invoice created successfully!\n\n"
                        f"File: {filename}\n"
                        f"Invoice #: {invoice_number}\n"
                        f"Total: ${total_amount:.2f}\n\n"
                        f"{len(entry_ids)} time entries marked as billed.",
                    )
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to create invoice:\n\n{e}\n\nCheck console for details.")

    def edit_time_entries_from_preview():
        edit_window = tk.Toplevel(preview_dialog)
        edit_window.title("Edit Time Entries")
        center_dialog(root, edit_window, 700, 500)
        ttk.Label(edit_window, text="Select a time entry to edit:", font=("Arial", 12, "bold")).pack(padx=20, pady=10)

        tree_frame = ttk.Frame(edit_window)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        edit_tree = ttk.Treeview(
            tree_frame,
            columns=("Date", "Project", "Task", "Hours", "Description"),
            show="headings",
            selectmode="browse",
        )
        edit_tree.heading("Date", text="Date")
        edit_tree.heading("Project", text="Project")
        edit_tree.heading("Task", text="Task")
        edit_tree.heading("Hours", text="Hours")
        edit_tree.heading("Description", text="Description")
        edit_tree.column("Date", width=120)
        edit_tree.column("Project", width=120)
        edit_tree.column("Task", width=120)
        edit_tree.column("Hours", width=80)
        edit_tree.column("Description", width=200)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=edit_tree.yview)
        edit_tree.configure(yscrollcommand=scrollbar.set)
        edit_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        entry_placeholders2 = ",".join(["?" for _ in entry_ids])
        db.conn.row_factory = sqlite3.Row
        cursor3 = db.conn.cursor()
        cursor3.execute(
            f"""
            SELECT te.id as entry_id, te.start_time, te.end_time, te.duration_minutes,
                   te.description, p.name as project_name, t.name as task_name
            FROM time_entries te
            JOIN tasks t ON te.task_id = t.id
            JOIN projects p ON te.project_id = p.id
            WHERE te.id IN ({entry_placeholders2})
            ORDER BY te.start_time
        """,
            entry_ids,
        )
        time_entries = cursor3.fetchall()
        db.conn.row_factory = None

        for entry in time_entries:
            try:
                dt = datetime.fromisoformat(entry["start_time"])
                date_display = dt.strftime("%m/%d/%y %I:%M %p")
            except Exception:
                date_display = entry["start_time"][:10]

            hours = (entry["duration_minutes"] or 0) / 60.0
            edit_tree.insert(
                "",
                "end",
                values=(
                    date_display,
                    entry["project_name"],
                    entry["task_name"],
                    f"{hours:.2f}",
                    entry["description"] or "",
                ),
                tags=(f"entry_id_{entry['entry_id']}",),
            )

        btn_frame = ttk.Frame(edit_window)
        btn_frame.pack(fill="x", padx=20, pady=20)

        def edit_selected_entry():
            selection = edit_tree.selection()
            if not selection:
                messagebox.showerror("Error", "Please select a time entry to edit")
                return

            entry_id_local = None
            for tag in edit_tree.item(selection[0])["tags"]:
                if tag.startswith("entry_id_"):
                    entry_id_local = int(tag.replace("entry_id_", ""))
                    break

            if not entry_id_local:
                messagebox.showerror("Error", "Could not find entry ID")
                return

            edit_window.destroy()
            open_edit_time_entry(entry_id_local)

        def refresh_invoice_preview():
            edit_window.destroy()
            preview_dialog.destroy()
            load_invoiceable_entries()
            messagebox.showinfo(
                "Refreshed",
                "Invoice data refreshed. Select entries and preview again to see changes.",
            )

        ttk.Button(btn_frame, text="Edit Selected Entry", command=edit_selected_entry).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Refresh & Close", command=refresh_invoice_preview).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=edit_window.destroy).pack(side="right", padx=5)

    def email_invoice():
        email_settings = db.get_email_settings()
        if not email_settings:
            messagebox.showinfo(
                "Email not configured",
                "Open the Email tab and save SMTP settings (Settings view), then try again.",
            )
            return

        if client_id is None:
            messagebox.showerror("Error", "Client ID missing for this invoice.")
            return

        client = client_model.get_by_id(client_id)
        if not client or not client[3]:
            messagebox.showerror(
                "No Email Address",
                f"Client '{client_name}' doesn't have an email address on file.\n\nPlease add their email in the Clients tab first.",
            )
            return

        client_email = client[3]
        show_email_invoice_dialog_ctk(
            root,
            preview_dialog,
            db,
            company_model,
            client_name,
            client_email,
            client_id,
            entry_ids,
            invoice_items,
            total_amount,
            start_date,
            end_date,
            refresh_time_entries,
            load_invoiceable_entries,
            on_billing_updated=on_billing_updated,
        )

    ctk.CTkButton(
        button_frame,
        text="Edit Entries",
        width=118,
        height=_btn_h,
        font=_btn_font,
        command=edit_time_entries_from_preview,
    ).pack(side="left", padx=4)
    ctk.CTkButton(
        button_frame,
        text="Cancel",
        width=96,
        height=_btn_h,
        font=_btn_font,
        command=preview_dialog.destroy,
    ).pack(side="right", padx=4)
    ctk.CTkButton(
        button_frame,
        text="Create invoice",
        width=138,
        height=_btn_h,
        font=_btn_font,
        command=create_invoice,
    ).pack(side="right", padx=4)
    ctk.CTkButton(
        button_frame,
        text="Email invoice",
        width=124,
        height=_btn_h,
        font=_btn_font,
        command=email_invoice,
    ).pack(side="right", padx=4)

    # Pack bottom chrome first so a tall Treeview cannot squeeze buttons to zero height (Windows + fixed geometry).
    header_frame.pack(side="top", fill="x", padx=20, pady=20)
    button_frame.pack(side="bottom", fill="x", padx=20, pady=20)
    total_frame.pack(side="bottom", fill="x", padx=20, pady=10)
    items_frame.pack(fill="both", expand=True, padx=20, pady=10)

    preview_dialog.update_idletasks()
    preview_dialog.lift()
    preview_dialog.focus_force()
