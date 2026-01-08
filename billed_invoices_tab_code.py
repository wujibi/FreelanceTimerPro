# ADD THIS METHOD TO gui.py AFTER create_invoice_tab() method
# This is the complete Billed Invoices tab implementation

def create_billed_invoices_tab(self):
    """Create the Billed Invoices tab with Paid/Unpaid views"""
    billed_frame = ttk.Frame(self.notebook)
    self.notebook.add(billed_frame, text="💰 Billed Invoices")
    
    # Top control frame
    control_frame = ttk.Frame(billed_frame)
    control_frame.pack(fill='x', padx=10, pady=10)
    
    # View selector
    view_label_frame = ttk.LabelFrame(control_frame, text="View")
    view_label_frame.pack(side='left', padx=5)
    
    self.invoice_view_var = tk.StringVar(value="unpaid")
    ttk.Radiobutton(view_label_frame, text="Unpaid", 
                   variable=self.invoice_view_var, value="unpaid",
                   command=self.refresh_billed_invoices).pack(side='left', padx=5, pady=5)
    ttk.Radiobutton(view_label_frame, text="Paid", 
                   variable=self.invoice_view_var, value="paid",
                   command=self.refresh_billed_invoices).pack(side='left', padx=5, pady=5)
    ttk.Radiobutton(view_label_frame, text="All", 
                   variable=self.invoice_view_var, value="all",
                   command=self.refresh_billed_invoices).pack(side='left', padx=5, pady=5)
    
    ttk.Button(control_frame, text="Refresh", 
              command=self.refresh_billed_invoices).pack(side='right', padx=5)
    
    # Invoice list
    list_frame = ttk.LabelFrame(billed_frame, text="Invoices")
    list_frame.pack(fill='both', expand=True, padx=10, pady=10)
    
    tree_frame = ttk.Frame(list_frame)
    tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
    
    self.billed_invoices_tree = ttk.Treeview(tree_frame, 
        columns=('Invoice', 'Client', 'Date', 'Amount', 'Status', 'Paid Date'),
        show='headings', selectmode='extended')
    
    self.billed_invoices_tree.heading('Invoice', text='Invoice #')
    self.billed_invoices_tree.heading('Client', text='Client')
    self.billed_invoices_tree.heading('Date', text='Invoice Date')
    self.billed_invoices_tree.heading('Amount', text='Amount')
    self.billed_invoices_tree.heading('Status', text='Status')
    self.billed_invoices_tree.heading('Paid Date', text='Date Paid')
    
    self.billed_invoices_tree.column('Invoice', width=150)
    self.billed_invoices_tree.column('Client', width=150)
    self.billed_invoices_tree.column('Date', width=100)
    self.billed_invoices_tree.column('Amount', width=100)
    self.billed_invoices_tree.column('Status', width=80)
    self.billed_invoices_tree.column('Paid Date', width=100)
    
    vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.billed_invoices_tree.yview)
    self.billed_invoices_tree.configure(yscrollcommand=vsb.set)
    self.billed_invoices_tree.pack(side='left', fill='both', expand=True)
    vsb.pack(side='right', fill='y')
    
    # Action buttons
    action_frame = ttk.Frame(billed_frame)
    action_frame.pack(fill='x', padx=10, pady=10)
    
    ttk.Button(action_frame, text="Mark as PAID", 
              command=self.mark_invoices_paid_dialog).pack(side='left', padx=5)
    ttk.Button(action_frame, text="Mark as UNPAID", 
              command=self.mark_invoices_unpaid).pack(side='left', padx=5)
    
    self.billed_summary_label = ttk.Label(action_frame, text="")
    self.billed_summary_label.pack(side='right', padx=10)
