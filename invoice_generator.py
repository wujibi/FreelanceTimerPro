from dataclasses import dataclass

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import os


@dataclass(frozen=True)
class PdfLayout:
    margin: float
    logo_size: float
    company_font: int
    company_name_font: int
    header_spacer: float
    title_font: int
    title_space_after: int
    title_spacer: float
    meta_font: int
    meta_spacer: float
    period_spacer: float
    bill_to_font: int
    client_font: int
    client_indent: int
    bill_to_spacer: float
    table_header_font: int
    table_header_pad: int
    table_body_font: int
    table_row_pad: int
    total_font: int
    total_pad: int
    footer_spacer: float
    footer_font: int


STANDARD_LAYOUT = PdfLayout(
    margin=0.75,
    logo_size=1.5,
    company_font=10,
    company_name_font=12,
    header_spacer=0.3,
    title_font=28,
    title_space_after=20,
    title_spacer=0.1,
    meta_font=10,
    meta_spacer=0.05,
    period_spacer=0.4,
    bill_to_font=12,
    client_font=10,
    client_indent=10,
    bill_to_spacer=0.4,
    table_header_font=11,
    table_header_pad=10,
    table_body_font=10,
    table_row_pad=8,
    total_font=12,
    total_pad=10,
    footer_spacer=0.5,
    footer_font=11,
)

COMPACT_LAYOUT = PdfLayout(
    margin=0.5,
    logo_size=0.85,
    company_font=9,
    company_name_font=10,
    header_spacer=0.15,
    title_font=20,
    title_space_after=10,
    title_spacer=0.05,
    meta_font=9,
    meta_spacer=0.03,
    period_spacer=0.2,
    bill_to_font=10,
    client_font=9,
    client_indent=6,
    bill_to_spacer=0.2,
    table_header_font=9,
    table_header_pad=5,
    table_body_font=8,
    table_row_pad=4,
    total_font=10,
    total_pad=6,
    footer_spacer=0.25,
    footer_font=9,
)


class InvoiceGenerator:
    def __init__(self, db_manager):
        self.db = db_manager

    def generate_pdf(self, invoice_data, filename, invoice_number, *, compact: bool = False):
        """Generate a professional invoice PDF with logo support."""
        layout = COMPACT_LAYOUT if compact else STANDARD_LAYOUT
        margin = layout.margin * inch
        doc = SimpleDocTemplate(
            filename,
            pagesize=letter,
            topMargin=margin,
            bottomMargin=margin,
            leftMargin=margin,
            rightMargin=margin,
        )
        story = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=layout.title_font,
            spaceAfter=layout.title_space_after,
            textColor=colors.HexColor('#1a5490'),
            alignment=0,
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=layout.bill_to_font,
            spaceAfter=6 if compact else 10,
            textColor=colors.HexColor('#1a5490'),
            fontName='Helvetica-Bold',
        )

        company = self.get_company_info()
        client = self.get_client_info(invoice_data['client_id'])

        if company:
            logo_path = company[5] if len(company) > 5 else None
            company_style = ParagraphStyle(
                'CompanyStyle',
                parent=styles['Normal'],
                fontSize=layout.company_font,
                alignment=0,
                textColor=colors.HexColor('#333333'),
            )

            if logo_path and os.path.exists(logo_path):
                try:
                    logo = Image(
                        logo_path,
                        width=layout.logo_size * inch,
                        height=layout.logo_size * inch,
                        kind='proportional',
                    )
                    company_info_text = self.format_company_info_html(company, layout=layout)
                    company_para = Paragraph(company_info_text, company_style)
                    header_data = [[company_para, logo]]
                    header_table = Table(header_data, colWidths=[4.7 * inch, 1.8 * inch])
                    header_table.setStyle(TableStyle([
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ]))
                    story.append(header_table)
                except Exception as e:
                    print(f"[WARNING] Could not add logo: {e}")
                    company_para = Paragraph(
                        self.format_company_info_html(company, layout=layout),
                        company_style,
                    )
                    story.append(company_para)
            else:
                company_para = Paragraph(
                    self.format_company_info_html(company, layout=layout),
                    company_style,
                )
                story.append(company_para)

            story.append(Spacer(1, layout.header_spacer * inch))

        story.append(Paragraph("INVOICE", title_style))
        story.append(Spacer(1, layout.title_spacer * inch))

        invoice_date = datetime.now().strftime("%B %d, %Y")
        meta_style = ParagraphStyle(
            'Meta',
            parent=styles['Normal'],
            fontSize=layout.meta_font,
            textColor=colors.HexColor('#333333'),
        )
        meta_right_style = ParagraphStyle(
            'MetaRight',
            parent=meta_style,
            alignment=2,
        )

        invoice_header_data = [[
            Paragraph(f"<b>Invoice Number:</b> {invoice_number}", meta_style),
            Paragraph(f"<b>Invoice Date:</b> {invoice_date}", meta_right_style),
        ]]
        invoice_header_table = Table(invoice_header_data, colWidths=[3.25 * inch, 3.25 * inch])
        invoice_header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(invoice_header_table)
        story.append(Spacer(1, layout.meta_spacer * inch))

        period_text = (
            f"<b>Invoice Period:</b> "
            f"{invoice_data['start_date'].strftime('%m/%d/%Y')} - "
            f"{invoice_data['end_date'].strftime('%m/%d/%Y')}"
        )
        payment_terms = "Payment is due within 30 days"
        if company and len(company) > 7 and company[7]:
            payment_terms = company[7]

        period_data = [[
            Paragraph(period_text, meta_style),
            Paragraph(f"<b>Payment Terms:</b> {payment_terms}", meta_right_style),
        ]]
        period_table = Table(period_data, colWidths=[3.25 * inch, 3.25 * inch])
        period_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(period_table)
        story.append(Spacer(1, layout.period_spacer * inch))

        story.append(Paragraph("BILL TO:", heading_style))
        if client:
            client_para = Paragraph(
                self.format_client_info_html(client),
                ParagraphStyle(
                    'ClientStyle',
                    parent=styles['Normal'],
                    fontSize=layout.client_font,
                    textColor=colors.HexColor('#333333'),
                    leftIndent=layout.client_indent,
                ),
            )
            story.append(client_para)
        story.append(Spacer(1, layout.bill_to_spacer * inch))

        table_data = [['Description', 'Quantity', 'Rate', 'Amount']]
        for item in invoice_data['items']:
            if item.get('is_header'):
                table_data.append([
                    Paragraph(f"<b>{item['description'].replace('**', '')}</b>", styles['Normal']),
                    '', '', '',
                ])
            elif item.get('is_subtotal'):
                table_data.append([
                    Paragraph(f"<b>{item['description']}</b>", styles['Normal']),
                    '', '',
                    f"${item['amount']:.2f}",
                ])
            else:
                amount_display = f"${item['amount']:.2f}" if isinstance(item['amount'], (int, float)) else ''
                table_data.append([
                    item['description'],
                    item['quantity'],
                    item['rate'],
                    amount_display,
                ])

        table_data.append(['', '', '', ''])
        table_data.append(['', '', 'TOTAL:', f"${invoice_data['total']:.2f}"])

        items_table = Table(table_data, colWidths=[3.8 * inch, 1.2 * inch, 1.2 * inch, 1.2 * inch])
        pad = layout.table_row_pad
        header_pad = layout.table_header_pad
        total_pad = layout.total_pad
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), layout.table_header_font),
            ('BOTTOMPADDING', (0, 0), (-1, 0), header_pad),
            ('TOPPADDING', (0, 0), (-1, 0), header_pad),
            ('FONTNAME', (0, 1), (-1, -3), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -3), layout.table_body_font),
            ('BOTTOMPADDING', (0, 1), (-1, -3), pad),
            ('TOPPADDING', (0, 1), (-1, -3), pad),
            ('TEXTCOLOR', (0, 1), (-1, -3), colors.HexColor('#333333')),
            ('FONTNAME', (2, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (2, -1), (-1, -1), layout.total_font),
            ('BACKGROUND', (2, -1), (-1, -1), colors.HexColor('#e8f4f8')),
            ('TEXTCOLOR', (2, -1), (-1, -1), colors.HexColor('#1a5490')),
            ('TOPPADDING', (2, -1), (-1, -1), total_pad),
            ('BOTTOMPADDING', (2, -1), (-1, -1), total_pad),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#1a5490')),
            ('LINEABOVE', (2, -1), (-1, -1), 1.5, colors.HexColor('#1a5490')),
            ('BOX', (0, 0), (-1, -3), 1, colors.HexColor('#cccccc')),
            ('INNERGRID', (0, 1), (-1, -3), 0.5, colors.HexColor('#eeeeee')),
        ]))

        story.append(items_table)
        story.append(Spacer(1, layout.footer_spacer * inch))

        thank_you_message = "Thank you for your business!"
        if company and len(company) > 8 and company[8]:
            thank_you_message = company[8]

        story.append(Paragraph(
            f"<b>{thank_you_message}</b>",
            ParagraphStyle(
                'FooterStyle',
                parent=styles['Normal'],
                fontSize=layout.footer_font,
                alignment=1,
                textColor=colors.HexColor('#666666'),
            ),
        ))

        doc.build(story)
        mode = "compact" if compact else "standard"
        print(f"[PDF] Invoice generated successfully ({mode}): {filename}")

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

    def format_company_info_html(self, company, *, layout: PdfLayout = STANDARD_LAYOUT):
        """Format company info as HTML for PDF"""
        if not company:
            return "<b>Your Company Name</b><br/>Your Address<br/>Your Phone<br/>Your Email"

        info_parts = []
        if len(company) > 1 and company[1]:
            info_parts.append(
                f"<b><font size={layout.company_name_font}>{company[1]}</font></b>"
            )
        if len(company) > 2 and company[2]:
            info_parts.append(company[2].replace('\n', '<br/>'))
        if len(company) > 3 and company[3]:
            info_parts.append(f"Phone: {company[3]}")
        if len(company) > 4 and company[4]:
            info_parts.append(f"Email: {company[4]}")
        if len(company) > 6 and company[6]:
            info_parts.append(f"Web: {company[6]}")

        return '<br/>'.join(info_parts)

    def format_client_info_html(self, client):
        """Format client info as HTML for PDF"""
        if not client:
            return "<i>Client information not available</i>"

        info_parts = []
        if len(client) > 1 and client[1]:
            info_parts.append(f"<b>{client[1]}</b>")
        if len(client) > 2 and client[2]:
            info_parts.append(client[2])
        if len(client) > 5 and client[5]:
            info_parts.append(client[5].replace('\n', '<br/>'))
        if len(client) > 4 and client[4]:
            info_parts.append(f"Phone: {client[4]}")
        if len(client) > 3 and client[3]:
            info_parts.append(f"Email: {client[3]}")

        return '<br/>'.join(info_parts)
