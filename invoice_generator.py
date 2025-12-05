from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import os


class InvoiceGenerator:
    def __init__(self, db_manager):
        self.db = db_manager

    def generate_pdf(self, invoice_data, filename, invoice_number):
        # Create the PDF document
        doc = SimpleDocTemplate(filename, pagesize=letter, topMargin=0.5 * inch)
        story = []

        # Get styles
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.darkblue
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue
        )

        # Get company info
        company = self.get_company_info()
        client = self.get_client_info(invoice_data['client_id'])

        # Header section with company info
        if company:
            company_info = self.format_company_info(company)
            # Check if logo exists
            if len(company) > 5 and company[5] and os.path.exists(company[5]):
                try:
                    logo = Image(company[5], width=2 * inch, height=1 * inch)
                    header_data = [[logo, Paragraph(company_info, styles['Normal'])]]
                    header_table = Table(header_data, colWidths=[2.5 * inch, 4 * inch])
                    header_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ]))
                    story.append(header_table)
                except Exception:
                    # If logo fails to load, just use text
                    story.append(Paragraph(company_info, styles['Normal']))
            else:
                story.append(Paragraph(company_info, styles['Normal']))

            story.append(Spacer(1, 0.3 * inch))

        # Invoice title
        story.append(Paragraph("INVOICE", title_style))

        # Invoice details
        invoice_date = datetime.now().strftime("%B %d, %Y")
        invoice_details = [
            ['Invoice Number:', invoice_number],
            ['Invoice Date:', invoice_date],
            ['Period:',
             f"{invoice_data['start_date'].strftime('%m/%d/%Y')} - {invoice_data['end_date'].strftime('%m/%d/%Y')}"]
        ]

        details_table = Table(invoice_details, colWidths=[2 * inch, 2 * inch])
        details_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        story.append(details_table)
        story.append(Spacer(1, 0.3 * inch))

        # Bill to section
        story.append(Paragraph("Bill To:", heading_style))
        if client:
            client_info = self.format_client_info(client)
            story.append(Paragraph(client_info, styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))

        # Invoice items table
        table_data = [['Description', 'Quantity', 'Rate', 'Amount']]

        for item in invoice_data['items']:
            table_data.append([
                item['description'],
                item['quantity'],
                item['rate'],
                f"${item['amount']:.2f}"
            ])

        # Add total row
        table_data.append(['', '', 'Total:', f"${invoice_data['total']:.2f}"])

        # Create table
        items_table = Table(table_data, colWidths=[3.5 * inch, 1 * inch, 1.5 * inch, 1 * inch])
        items_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            # Data rows
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 10),
            ('ALIGN', (0, 1), (0, -2), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            # Total row
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            # Borders
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.darkblue),
        ]))

        story.append(items_table)
        story.append(Spacer(1, 0.5 * inch))

        # Footer
        footer_text = "Thank you for your business!"
        story.append(Paragraph(footer_text, styles['Normal']))

        # Build PDF - this was missing!
        doc.build(story)

    def get_company_info(self):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM company_info WHERE id = 1')
            return cursor.fetchone()

    def get_client_info(self, client_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM clients WHERE id = ?', (client_id,))
            return cursor.fetchone()

    def format_company_info(self, company):
        if not company:
            return "Your Company Name<br/>Your Address<br/>Your Phone<br/>Your Email"

        info_parts = [company[1]]  # Company name
        if len(company) > 2 and company[2]:  # Address
            address_formatted = company[2].replace('\n', '<br/>')
            info_parts.append(address_formatted)
        if len(company) > 3 and company[3]:  # Phone
            info_parts.append(company[3])
        if len(company) > 4 and company[4]:  # Email
            info_parts.append(company[4])

        return '<br/>'.join(info_parts)

    def format_client_info(self, client):
        if not client:
            return "Client information not available"

        info_parts = []
        if len(client) > 1 and client[1]:  # Name
            info_parts.append(client[1])
        if len(client) > 2 and client[2]:  # Company
            info_parts.append(client[2])
        if len(client) > 5 and client[5]:  # Address
            address_formatted = client[5].replace('\n', '<br/>')
            info_parts.append(address_formatted)
        if len(client) > 4 and client[4]:  # Phone
            info_parts.append(f"Phone: {client[4]}")
        if len(client) > 3 and client[3]:  # Email
            info_parts.append(f"Email: {client[3]}")

        return '<br/>'.join(info_parts)
