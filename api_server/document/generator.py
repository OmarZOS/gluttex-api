from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML
import os
from pathlib import Path
from document.invoice_data import InvoiceGenerator, Invoice, Receipt, Cart, ReceiptData
import base64
from datetime import datetime
import json

class CompactInvoiceRenderer:
    def __init__(self, template_dir: str = "document/templates", static_dir: str = "static"):
        self.template_dir = template_dir
        self.static_dir = static_dir
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters
        def format_currency(value, symbol="DZD"):
            if value is None:
                return f"0.00{symbol}"
            try:
                return f"{float(value):,.2f}{symbol}"
            except:
                return f"0.00{symbol}"
        
        self.env.filters['format_currency'] = format_currency
        self.env.filters['format_date'] = lambda x: datetime.strptime(x, "%Y-%m-%d").strftime("%b %d, %Y") if "-" in x else x
        
        # Create directories if they don't exist
        Path(self.static_dir).mkdir(exist_ok=True)
        Path(self.template_dir).mkdir(exist_ok=True)
        
        # Create CSS directory and file
        css_dir = Path(self.static_dir) / "css"
        css_dir.mkdir(exist_ok=True)
        
        # Write CSS if it doesn't exist
        css_path = css_dir / "invoice.css"
        if not css_path.exists():
            self._create_default_css(css_path)
    
    def _create_default_css(self, css_path: Path):
        """Create default CSS for invoices"""
        css_content = """
        /* Default invoice CSS */
        body {
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 20px;
        }
        
        .invoice-container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }
        
        .company-info h1 {
            margin: 0;
            color: #2c3e50;
        }
        
        .invoice-info {
            text-align: right;
        }
        
        .invoice-number {
            font-size: 24px;
            font-weight: bold;
            color: #3498db;
        }
        
        .client-info, .company-details {
            margin-bottom: 20px;
        }
        
        .items-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        
        .items-table th {
            background-color: #f8f9fa;
            text-align: left;
            padding: 12px;
            border-bottom: 2px solid #dee2e6;
        }
        
        .items-table td {
            padding: 10px;
            border-bottom: 1px solid #dee2e6;
        }
        
        .totals {
            text-align: right;
            margin-top: 30px;
        }
        
        .total-row {
            display: flex;
            justify-content: flex-end;
            margin-bottom: 5px;
        }
        
        .total-label {
            width: 150px;
            text-align: right;
            padding-right: 10px;
        }
        
        .total-amount {
            width: 150px;
            text-align: right;
            font-weight: bold;
        }
        
        .grand-total {
            font-size: 18px;
            color: #27ae60;
            border-top: 2px solid #e0e0e0;
            padding-top: 10px;
            margin-top: 10px;
        }
        
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e0e0e0;
            font-size: 12px;
            color: #7f8c8d;
        }
        
        .qr-code {
            text-align: center;
            margin: 20px 0;
        }
        
        .qr-code img {
            max-width: 150px;
            height: auto;
        }
        """
        
        with open(css_path, 'w') as f:
            f.write(css_content)
    
    def render_compact_invoice(self, invoice: Invoice) -> str:
        """Render compact invoice as HTML string"""
        template = self.env.get_template("invoice.html")
        context = invoice.to_dict()
        # Add generated date
        context['generated_date'] = datetime.now().strftime("%B %d, %Y %H:%M")
        return template.render(**context)
    
    def render_compact_receipt(self, receipt: Receipt) -> str:
        """Render compact receipt as HTML string"""
        template = self.env.get_template("receipt.html")
        context = receipt.to_dict()
        return template.render(**context)
    
    def generate_invoice_from_json(self, json_data: dict) -> Invoice:
        """Generate invoice from JSON data"""
        return InvoiceGenerator.from_json(json_data)
    
    def generate_compact_invoice_pdf(self, invoice: Invoice, output_path: str = None) -> bytes:
        """Generate PDF from compact invoice"""
        html_content = self.render_compact_invoice(invoice)
        
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        html = HTML(string=html_content, base_url=os.path.abspath(self.static_dir))
        pdf_bytes = html.write_pdf()
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes)
        
        return pdf_bytes
    
    def generate_compact_receipt_pdf(self, receipt: Receipt, output_path: str = None) -> bytes:
        """Generate PDF from compact receipt"""
        html_content = self.render_compact_receipt(receipt)
        
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        html = HTML(string=html_content, base_url=os.path.abspath(self.static_dir))
        pdf_bytes = html.write_pdf()
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes)
        
        return pdf_bytes
    
    def generate_compact_invoice_html(self, invoice: Invoice, output_path: str = None):
        """Save compact invoice as HTML file"""
        html_content = self.render_compact_invoice(invoice)
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
        return html_content
    
    def generate_compact_receipt_html(self, receipt: Receipt, output_path: str):
        """Save compact receipt as HTML file"""
        html_content = self.render_compact_receipt(receipt)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def preview_compact_invoice(self, invoice: Invoice, output_dir: str = "output"):
        """Preview compact invoice"""
        Path(output_dir).mkdir(exist_ok=True)
        
        html_path = Path(output_dir) / f"invoice-{invoice.invoice_number.replace('/', '-')}.html"
        pdf_path = Path(output_dir) / f"invoice-{invoice.invoice_number.replace('/', '-')}.pdf"
        
        print(f"Generating compact invoice HTML: {html_path}")
        self.generate_compact_invoice_html(invoice, str(html_path))
        
        print(f"Generating compact invoice PDF: {pdf_path}")
        self.generate_compact_invoice_pdf(invoice, str(pdf_path))
        
        return {
            "html": str(html_path),
            "pdf": str(pdf_path)
        }
    
    def preview_compact_receipt(self, receipt: Receipt, output_dir: str = "output"):
        """Preview compact receipt"""
        Path(output_dir).mkdir(exist_ok=True)
        
        html_path = Path(output_dir) / f"receipt_{receipt.receipt_number.replace('/', '-')}.html"
        pdf_path = Path(output_dir) / f"receipt_{receipt.receipt_number.replace('/', '-')}.pdf"
        
        print(f"Generating compact receipt HTML: {html_path}")
        self.generate_compact_receipt_html(receipt, str(html_path))
        
        print(f"Generating compact receipt PDF: {pdf_path}")
        self.generate_compact_receipt_pdf(receipt, str(pdf_path))
        
        return {
            "html": str(html_path),
            "pdf": str(pdf_path)
        }

# Example usage with actual JSON data
def main():
    # Initialize renderer
    renderer = CompactInvoiceRenderer()
    
    # Your actual JSON data
    json_data = {
        "cart_status": "open",
        "cart_total_amount": 250,
        "cart_client_user": None,
        "cart_notes": "Genetic counseling and testing consideration",
        "cart_created_at": "2025-12-23T10:59:45",
        "cart_updated_at": "2025-12-23T10:59:45",
        "cart_product_provider_id": 6,
        "cart_person_ref": 1,
        "cart_selling_user": 1,
        "cart_id": 37,
        "app_user": None,
        "person": {
            "id_person": 1,
            "person_details_id": 1,
            "person_blood_type_id": 1,
            "person_location_id": None,
            "person_details": {
                "person_last_name": "One",
                "id_person_details": 1,
                "person_birth_date": "2003-01-01",
                "person_first_name": "Some",
                "person_gender": "Male",
                "person_nationality": "Algerian"
            }
        },
        "cart_product_provider": {
            "product_provider_owner": None,
            "product_provider_location_id": None,
            "id_product_provider": 6,
            "product_provider_type_id": 2,
            "product_provider_details_id": 1,
            "product_provider_org_id": None,
            "product_provider_details": {
                "provider_name": "Magasin habibou sans gluten",
                "provider_contact_info": "Facebook: https://www.facebook.com/profile.php?id=100063549909208",
                "idprovider_details_id": 1
            },
            "product_provider_org": None,
            "product_provider_type": {
                "product_provider_type_desc": "Bakery",
                "product_provider_ref": null,
                "id_product_provider_type": 2
            }
        },
        "app_user_": {
            "app_user_person_id": 1,
            "id_app_user": 1,
            "app_user_type_id": 1,
            "app_user_password": "password",
            "app_user_preferences": None,
            "app_user_image_url": None,
            "app_user_last_active": None,
            "app_user_name": "SomeOne",
            "app_user_last_updated": None,
            "app_user_creation": None,
            "app_user_subscription_ref": None,
            "app_user_person": {
                "id_person": 1,
                "person_details_id": 1,
                "person_blood_type_id": 1,
                "person_location_id": None,
                "person_details": {
                    "person_last_name": "One",
                    "id_person_details": 1,
                    "person_birth_date": "2003-01-01",
                    "person_first_name": "Some",
                    "person_gender": "Male",
                    "person_nationality": "Algerian"
                }
            }
        },
        "invoice": [
            {
                "invoice_id": 37,
                "invoice_issue_date": "2024-02-21",
                "invoice_notes": "Prenatal care",
                "invoice_updated_at": "2025-12-23T10:59:45",
                "invoice_cart_id": 37,
                "invoice_number": "INV-2024-037",
                "invoice_total_amount": 280,
                "invoice_status": "paid",
                "invoice_due_date": "2024-03-21",
                "invoice_created_at": "2025-12-23T10:59:45",
                "payment": []
            }
        ],
        "ordered_service": [
            {
                "ordered_service_service_id": 7,
                "ordered_service_cart_id": 37,
                "ordered_service_quantity": 1,
                "ordered_service_total_price": 100,
                "ordered_service_scheduled_at": None,
                "ordered_service_updated_at": "2025-12-23T10:59:45",
                "ordered_service_id": 46,
                "ordered_service_unit_price": 100,
                "ordered_service_notes": "First trimester ultrasound",
                "ordered_service_created_at": "2025-12-23T10:59:45"
            }
        ],
        "receipt": [
            {
                "receipt_id": 56,
                "receipt_number": "RCPT-RECENT-056",
                "receipt_notes": "Fresh payment receipt",
                "receipt_cart_ref": 37,
                "receipt_amount": 9200,
                "receipt_payment_id": None,
                "receipt_created_at": "2024-03-06T09:10:00",
                "receipt_payment": None,
                "deposit": []
            }
        ],
        "deposit": [],
        "ordered_item": [
            {
                "id_ordered_item": 61,
                "ordered_quantity": 5,
                "applied_vat": 8,
                "ordered_product_id": 2,
                "order_ref": None,
                "unit_price": 8,
                "product_discount": 15,
                "ordered_product": {
                    "product_provider_id": 2,
                    "product_quantifier": None,
                    "product_owner": 2,
                    "product_brand": "LEGER",
                    "product_category_id": 1,
                    "product_barcode": "1234567890124",
                    "id_product": 2,
                    "last_updated": "2025-12-23T11:01:55",
                    "created": "2025-12-23T00:00:00",
                    "product_description": "Light and crispy gluten-free butter biscuits.",
                    "product_origin_id": None,
                    "product_name": "Butter Biscuits LEGER",
                    "product_price": 4.49,
                    "product_quantity": 147
                }
            }
        ]
    }
    
    print("Creating invoice from JSON data...")
    invoice = renderer.generate_invoice_from_json(json_data)
    
    # Preview compact invoice
    result = renderer.preview_compact_invoice(invoice)
    print(f"✓ Compact invoice generated:")
    print(f"  HTML: {result['html']}")
    print(f"  PDF: {result['pdf']}")
    
    # Generate receipt if available
    if json_data.get('receipt') and len(json_data['receipt']) > 0:
        print("\nCreating receipt from JSON data...")
        receipt_data = json_data['receipt'][0]
        
        # Create ReceiptData
        receipt_data_obj = ReceiptData(
            receipt_id=receipt_data['receipt_id'],
            receipt_number=receipt_data['receipt_number'],
            receipt_amount=receipt_data['receipt_amount'],
            receipt_notes=receipt_data.get('receipt_notes'),
            receipt_cart_ref=receipt_data.get('receipt_cart_ref'),
            receipt_payment_id=receipt_data.get('receipt_payment_id'),
            receipt_created_at=receipt_data['receipt_created_at'],
            receipt_payment=receipt_data.get('receipt_payment'),
            deposit=receipt_data.get('deposit', [])
        )
        
        # Create Receipt
        receipt = Receipt.from_receipt_data(invoice, receipt_data_obj)
        
        # Preview compact receipt
        result = renderer.preview_compact_receipt(receipt)
        print(f"✓ Compact receipt generated:")
        print(f"  HTML: {result['html']}")
        print(f"  PDF: {result['pdf']}")


renderer = CompactInvoiceRenderer()

if __name__ == "__main__":
    main()