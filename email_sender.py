"""
Email Sender Module for Time Tracker Pro
Handles SMTP email sending with attachments and templates
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import formataddr
import os
from datetime import datetime


class EmailSender:
    """Handles sending emails via SMTP with attachments and templates"""
    
    def __init__(self, smtp_server, smtp_port, email_address, email_password):
        """Initialize email sender with SMTP settings
        
        Args:
            smtp_server (str): SMTP server address (e.g., smtp.gmail.com)
            smtp_port (int): SMTP port (usually 587 for TLS)
            email_address (str): Your email address
            email_password (str): App password or email password
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email_address = email_address
        self.email_password = email_password
    
    def test_connection(self):
        """Test SMTP connection and authentication
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_address, self.email_password)
            server.quit()
            return (True, "Connection successful! ✅")
        except smtplib.SMTPAuthenticationError:
            return (False, "Authentication failed. Check your email and password.\n\n"
                          "For Gmail, you need an 'App Password':\n"
                          "1. Go to myaccount.google.com/security\n"
                          "2. Enable 2-Step Verification\n"
                          "3. Create App Password for 'Mail'")
        except smtplib.SMTPException as e:
            return (False, f"SMTP error: {str(e)}")
        except Exception as e:
            return (False, f"Connection error: {str(e)}\n\n"
                          "Check your SMTP server and port settings.")
    
    def send_email(self, to_address, subject, body_html, attachment_path=None, 
                   cc_addresses=None, bcc_addresses=None, from_name=None):
        """Send an email with optional attachment
        
        Args:
            to_address (str): Recipient email address
            subject (str): Email subject line
            body_html (str): Email body (HTML format)
            attachment_path (str, optional): Path to file to attach
            cc_addresses (list, optional): List of CC email addresses
            bcc_addresses (list, optional): List of BCC email addresses
            from_name (str, optional): Display name for sender
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = formataddr((from_name or self.email_address, self.email_address))
            msg['To'] = to_address
            msg['Subject'] = subject
            msg['Date'] = formataddr((None, datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')))
            
            # Add CC if provided
            if cc_addresses:
                msg['Cc'] = ', '.join(cc_addresses)
            
            # Attach HTML body
            msg.attach(MIMEText(body_html, 'html'))
            
            # Attach file if provided
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, 'rb') as f:
                    attachment = MIMEApplication(f.read(), _subtype='pdf')
                    attachment.add_header('Content-Disposition', 'attachment', 
                                        filename=os.path.basename(attachment_path))
                    msg.attach(attachment)
            
            # Connect and send
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_address, self.email_password)
            
            # Build recipient list (to + cc + bcc)
            recipients = [to_address]
            if cc_addresses:
                recipients.extend(cc_addresses)
            if bcc_addresses:
                recipients.extend(bcc_addresses)
            
            server.sendmail(self.email_address, recipients, msg.as_string())
            server.quit()
            
            return (True, f"Email sent successfully to {to_address}! ✅")
            
        except smtplib.SMTPAuthenticationError:
            return (False, "Authentication failed. Check your email settings.")
        except smtplib.SMTPException as e:
            return (False, f"Failed to send email: {str(e)}")
        except Exception as e:
            return (False, f"Error sending email: {str(e)}")
    
    def send_test_email(self, test_data=None):
        """Send a test email to yourself with sample data
        
        Args:
            test_data (dict, optional): Sample data for template testing
            
        Returns:
            tuple: (success: bool, message: str)
        """
        if test_data is None:
            test_data = {
                'client_name': 'John Smith',
                'invoice_number': 'INV-20260129-123456',
                'invoice_total': '$1,234.56',
                'company_name': 'Your Company'
            }
        
        subject = f"TEST: Invoice {test_data['invoice_number']}"
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <p><strong>This is a TEST email</strong></p>
            <p>Dear {test_data['client_name']},</p>
            <p>This is a test of your email invoice system.</p>
            <p>Invoice: <strong>{test_data['invoice_number']}</strong><br>
               Total: <strong>{test_data['invoice_total']}</strong></p>
            <p>If you're seeing this, your email settings are working correctly! ✅</p>
            <p>Best regards,<br>{test_data['company_name']}</p>
        </body>
        </html>
        """
        
        return self.send_email(
            to_address=self.email_address,
            subject=subject,
            body_html=body,
            from_name=test_data['company_name']
        )


class EmailTemplate:
    """Email template with variable substitution"""
    
    # Default templates
    TEMPLATES = {
        'Professional': {
            'subject': 'Invoice {{invoice_number}} from {{company_name}}',
            'body': '''<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <p>Dear {{client_name}},</p>
    
    <p>Please find attached invoice <strong>{{invoice_number}}</strong> for services rendered during {{date_range}}.</p>
    
    <p style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #2563eb;">
        <strong>Invoice Total:</strong> {{invoice_total}}<br>
        <strong>Payment Terms:</strong> {{payment_terms}}
    </p>
    
    <p>If you have any questions, please don't hesitate to contact me.</p>
    
    <p>Thank you for your business!</p>
    
    <p>Best regards,<br>
    {{company_name}}<br>
    {{company_email}}<br>
    {{company_phone}}</p>
</body>
</html>'''
        },
        
        'Friendly': {
            'subject': 'Your invoice is ready! 🎉',
            'body': '''<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <p>Hi {{client_name}}! 👋</p>
    
    <p>Hope you're doing well! Attached is invoice <strong>{{invoice_number}}</strong> for the great work we did together.</p>
    
    <p style="font-size: 18px;">
        💰 <strong>Total:</strong> {{invoice_total}}<br>
        📅 <strong>Due:</strong> {{due_date}}
    </p>
    
    <p>Let me know if you have any questions!</p>
    
    <p>Cheers,<br>
    {{company_name}} 😊</p>
</body>
</html>'''
        },
        
        'Formal': {
            'subject': 'Invoice {{invoice_number}} - {{company_name}}',
            'body': '''<html>
<body style="font-family: 'Times New Roman', serif; line-height: 1.8; color: #000;">
    <p>Dear {{client_name}},</p>
    
    <p>This email serves as formal notice that invoice <strong>{{invoice_number}}</strong>, dated {{invoice_date}}, has been issued for services rendered.</p>
    
    <table style="border-collapse: collapse; margin: 20px 0;">
        <tr>
            <td style="padding: 5px; border-bottom: 1px solid #ccc;"><strong>Amount Due:</strong></td>
            <td style="padding: 5px; border-bottom: 1px solid #ccc;">{{invoice_total}}</td>
        </tr>
        <tr>
            <td style="padding: 5px;"><strong>Payment Terms:</strong></td>
            <td style="padding: 5px;">{{payment_terms}}</td>
        </tr>
    </table>
    
    <p>Please remit payment to the address indicated on the attached invoice.</p>
    
    <p>Respectfully,<br>
    {{company_name}}</p>
</body>
</html>'''
        },
        
        'Reminder': {
            'subject': 'Payment Reminder - Invoice {{invoice_number}}',
            'body': '''<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <p>Dear {{client_name}},</p>
    
    <p>This is a friendly reminder that invoice <strong>{{invoice_number}}</strong> ({{invoice_total}}) is now past due.</p>
    
    <p style="background-color: #fff3cd; padding: 10px; border-left: 4px solid #ffc107;">
        ⚠️ <strong>Original Due Date:</strong> {{due_date}}
    </p>
    
    <p>Please submit payment at your earliest convenience. If payment has already been sent, please disregard this notice.</p>
    
    <p>Thank you,<br>
    {{company_name}}<br>
    {{company_email}}</p>
</body>
</html>'''
        },
        
        'Thank You': {
            'subject': 'Thank you for your payment! 💙',
            'body': '''<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <p>Dear {{client_name}},</p>
    
    <p style="font-size: 18px;">🎉 Thank you so much for your prompt payment of <strong>{{invoice_total}}</strong> for invoice {{invoice_number}}!</p>
    
    <p>It's always a pleasure working with you, and I look forward to our continued partnership!</p>
    
    <p>Warm regards,<br>
    {{company_name}} 💙</p>
</body>
</html>'''
        }
    }
    
    @staticmethod
    def get_template_names():
        """Get list of available template names"""
        return list(EmailTemplate.TEMPLATES.keys())
    
    @staticmethod
    def get_template(template_name):
        """Get template by name
        
        Returns:
            dict: {'subject': str, 'body': str} or None if not found
        """
        return EmailTemplate.TEMPLATES.get(template_name)
    
    @staticmethod
    def render_template(template_text, variables):
        """Replace template variables with actual values
        
        Args:
            template_text (str): Template with {{variable}} placeholders
            variables (dict): Dictionary of variable names and values
            
        Returns:
            str: Rendered template
        """
        result = template_text
        for key, value in variables.items():
            placeholder = '{{' + key + '}}'
            result = result.replace(placeholder, str(value))
        return result
    
    @staticmethod
    def get_available_variables():
        """Get list of all available template variables"""
        return [
            '{{client_name}}',
            '{{client_company}}',
            '{{client_email}}',
            '{{invoice_number}}',
            '{{invoice_date}}',
            '{{invoice_total}}',
            '{{payment_terms}}',
            '{{due_date}}',
            '{{date_range}}',
            '{{company_name}}',
            '{{company_email}}',
            '{{company_phone}}',
            '{{company_website}}'
        ]
