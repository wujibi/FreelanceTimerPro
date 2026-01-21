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
        """Generate a professional invoice PDF with logo support"""
        # Create the PDF document
        doc = SimpleDocTemplate(filename, pagesize=letter, 
                               topMargin=0.75 * inch,
                               bottomMargin=0.75 * inch,
                               leftMargin=0.75 * inch,
                               rightMargin=0.75 * inch)
        story = []

        # Get styles
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=28,
            spaceAfter=20,
            textColor=colors.HexColor('#1a5490'),
            alignment=0  # LEFT aligned
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=10,
            textColor=colors.HexColor('#1a5490'),
            fontName='Helvetica-Bold'
        )

        # Get company and client info
        company = self.get_company_info()
        client = self.get_client_info(invoice_data['client_id'])

        # Header - Company Info LEFT, Logo RIGHT
        if company:
            # Check if logo exists
            logo_path = company[5] if len(company) > 5 else None
            
            if logo_path and os.path.exists(logo_path):
                # Create table with company info on LEFT, logo on RIGHT
                try:
                    logo = Image(logo_path, width=1.5*inch, height=1.5*inch, kind='proportional')
                    company_info_text = self.format_company_info_html(company)
                    company_para = Paragraph(company_info_text, ParagraphStyle(
                        'CompanyStyle',
                        parent=styles['Normal'],
                        fontSize=10,
                        alignment=0,  # LEFT align
                        textColor=colors.HexColor('#333333')
                    ))
                    
                    # Create header table: LEFT=company info, RIGHT=logo
                    header_data = [[company_para, logo]]
                    header_table = Table(header_data, colWidths=[4.7*inch, 1.8*inch])
                    header_table.setStyle(TableStyle([
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('ALIGN', (0, 0), (0, 0), 'LEFT'),   # Company info LEFT
                        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),  # Logo RIGHT
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ]))
                    story.append(header_table)
                except Exception as e:
                    print(f"[WARNING] Could not add logo: {e}")
                    # Fallback to text only
                    company_info = self.format_company_info_html(company)
                    company_para = Paragraph(company_info, ParagraphStyle(
                        'CompanyStyle',
                        parent=styles['Normal'],
                        fontSize=10,
                        alignment=0,  # LEFT align
                        textColor=colors.HexColor('#333333')
                    ))
                    story.append(company_para)
            else:
                # No logo, just company info on LEFT
                company_info = self.format_company_info_html(company)
                company_para = Paragraph(company_info, ParagraphStyle(
                    'CompanyStyle',
                    parent=styles['Normal'],
                    fontSize=10,
                    alignment=0,  # LEFT align
                    textColor=colors.HexColor('#333333')
                ))
                story.append(company_para)
            
            story.append(Spacer(1, 0.3 * inch))

        # Invoice Title on its own line (LEFT aligned)
        story.append(Paragraph("INVOICE", title_style))
        story.append(Spacer(1, 0.1 * inch))

        # Invoice Number (LEFT) and Date (RIGHT) on same line
        invoice_date = datetime.now().strftime("%B %d, %Y")
        
        invoice_header_data = [[
            Paragraph(f"<b>Invoice Number:</b> {invoice_number}", ParagraphStyle(
                'InvoiceNum',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#333333')
            )),
            Paragraph(f"<b>Invoice Date:</b> {invoice_date}", ParagraphStyle(
                'InvoiceDate',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#333333'),
                alignment=2  # RIGHT align
            ))
        ]]
        
        invoice_header_table = Table(invoice_header_data, colWidths=[3.25*inch, 3.25*inch])
        invoice_header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(invoice_header_table)
        story.append(Spacer(1, 0.05 * inch))

        # Period (LEFT) and Payment Terms (RIGHT) on same line
        period_text = f"<b>Invoice Period:</b> {invoice_data['start_date'].strftime('%m/%d/%Y')} - {invoice_data['end_date'].strftime('%m/%d/%Y')}"
        
        # Get payment terms from company info or use default
        payment_terms = "Payment is due within 30 days"
        if company and len(company) > 7 and company[7]:
            payment_terms = company[7]
        
        period_data = [[
            Paragraph(period_text, ParagraphStyle(
                'Period',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#333333')
            )),
            Paragraph(f"<b>Payment Terms:</b> {payment_terms}", ParagraphStyle(
                'Terms',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#333333'),
                alignment=2  # RIGHT align
            ))
        ]]
        
        period_table = Table(period_data, colWidths=[3.25*inch, 3.25*inch])
        period_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(period_table)
        story.append(Spacer(1, 0.4 * inch))

        # Bill To Section
        story.append(Paragraph("BILL TO:", heading_style))
        if client:
            client_info = self.format_client_info_html(client)
            client_para = Paragraph(client_info, ParagraphStyle(
                'ClientStyle',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#333333'),
                leftIndent=10
            ))
            story.append(client_para)
        story.append(Spacer(1, 0.4 * inch))

        # Invoice Items Table
        table_data = [['Description', 'Quantity', 'Rate', 'Amount']]

        for item in invoice_data['items']:
            if item.get('is_header'):
                # Project header - bold, no values
                table_data.append([
                    Paragraph(f"<b>{item['description'].replace('**', '')}</b>", styles['Normal']),
                    '', '', ''
                ])
            elif item.get('is_subtotal'):
                # Project subtotal - bold, right-aligned amount
                table_data.append([
                    Paragraph(f"<b>{item['description']}</b>", styles['Normal']),
                    '', '',
                    f"${item['amount']:.2f}"
                ])
            else:
                # Regular task row
                amount_display = f"${item['amount']:.2f}" if isinstance(item['amount'], (int, float)) else ''
                table_data.append([
                    item['description'],
                    item['quantity'],
                    item['rate'],
                    amount_display
                ])

        # Add subtotal and total rows
        table_data.append(['', '', '', ''])  # Blank row
        table_data.append(['', '', 'TOTAL:', f"${invoice_data['total']:.2f}"])

        # Create table with better styling
        items_table = Table(table_data, colWidths=[3.8*inch, 1.2*inch, 1.2*inch, 1.2*inch])
        items_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -3), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -3), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -3), 8),
            ('TOPPADDING', (0, 1), (-1, -3), 8),
            ('TEXTCOLOR', (0, 1), (-1, -3), colors.HexColor('#333333')),
            
            # Total row
            ('FONTNAME', (2, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (2, -1), (-1, -1), 12),
            ('BACKGROUND', (2, -1), (-1, -1), colors.HexColor('#e8f4f8')),
            ('TEXTCOLOR', (2, -1), (-1, -1), colors.HexColor('#1a5490')),
            ('TOPPADDING', (2, -1), (-1, -1), 10),
            ('BOTTOMPADDING', (2, -1), (-1, -1), 10),
            
            # Borders
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#1a5490')),
            ('LINEABOVE', (2, -1), (-1, -1), 1.5, colors.HexColor('#1a5490')),
            ('BOX', (0, 0), (-1, -3), 1, colors.HexColor('#cccccc')),
            ('INNERGRID', (0, 1), (-1, -3), 0.5, colors.HexColor('#eeeeee')),
        ]))

        story.append(items_table)
        story.append(Spacer(1, 0.5 * inch))

        # Footer - Thank You Message (center)
        thank_you_message = "Thank you for your business!"
        if company and len(company) > 8 and company[8]:
            thank_you_message = company[8]
        
        footer_text = f"<b>{thank_you_message}</b>"
        footer_para = Paragraph(footer_text, ParagraphStyle(
            'FooterStyle',
            parent=styles['Normal'],
            fontSize=11,
            alignment=1,  # Center
            textColor=colors.HexColor('#666666')
        ))
        story.append(footer_para)

        # Build PDF
        doc.build(story)
        print(f"[PDF] Invoice generated successfully: {filename}")

    def get_company_info(self):
        """Get company information from database"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM company_info WHERE id = 1')
                return cursor.fetchone()
        except Exception as e:
            print(f"[WARNING] Could not get company info: {e}")
            return None

    def get_client_info(self, client_id):
        """Get client information from database"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM clients WHERE id = ?', (client_id,))
                return cursor.fetchone()
        except Exception as e:
            print(f"[WARNING] Could not get client info: {e}")
            return None

    def format_company_info_html(self, company):
        """Format company info as HTML for PDF"""
        if not company:
            return "<b>Your Company Name</b><br/>Your Address<br/>Your Phone<br/>Your Email"

        info_parts = []
        
        # Company name (bold and larger)
        if len(company) > 1 and company[1]:
            info_parts.append(f"<b><font size=12>{company[1]}</font></b>")
        
        # Address
        if len(company) > 2 and company[2]:
            address_formatted = company[2].replace('\n', '<br/>')
            info_parts.append(address_formatted)
        
        # Phone
        if len(company) > 3 and company[3]:
            info_parts.append(f"Phone: {company[3]}")
        
        # Email
        if len(company) > 4 and company[4]:
            info_parts.append(f"Email: {company[4]}")
        
        # Website (if exists)
        if len(company) > 6 and company[6]:
            info_parts.append(f"Web: {company[6]}")

        return '<br/>'.join(info_parts)

    def format_client_info_html(self, client):
        """Format client info as HTML for PDF"""
        if not client:
            return "<i>Client information not available</i>"

        info_parts = []
        
        # Name (bold)
        if len(client) > 1 and client[1]:
            info_parts.append(f"<b>{client[1]}</b>")
        
        # Company
        if len(client) > 2 and client[2]:
            info_parts.append(client[2])
        
        # Address
        if len(client) > 5 and client[5]:
            address_formatted = client[5].replace('\n', '<br/>')
            info_parts.append(address_formatted)
        
        # Phone
        if len(client) > 4 and client[4]:
            info_parts.append(f"Phone: {client[4]}")
        
        # Email
        if len(client) > 3 and client[3]:
            info_parts.append(f"Email: {client[3]}")

        return '<br/>'.join(info_parts)
