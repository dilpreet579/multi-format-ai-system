import PyPDF2
import re
from typing import Dict, Any

class PDFAgent:
    def __init__(self):
        self.compliance_keywords = ['gdpr', 'fda', 'hipaa', 'sox']

    def extract_text(self, pdf_path: str) -> str:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ''
            for page in reader.pages:
                text += page.extract_text() or ''
        print(f"[PDF DEBUG] Extracted text from {pdf_path}:\n{text}\n---END---")
        return text

    def parse_invoice(self, text: str) -> Dict[str, Any]:
        total_match = re.search(r'Invoice Total: ([\d,\.]+)\s*([A-Z]{3})', text)
        if total_match:
            total = float(total_match.group(1).replace(',', ''))
            currency = total_match.group(2)
        else:
            total = None
            currency = None
        return {'total': total, 'currency': currency}

    def parse_policy(self, text: str) -> Dict[str, Any]:
        mentions = [kw.upper() for kw in self.compliance_keywords if kw in text.lower()]
        return {'mentions': mentions}

    def process(self, pdf_path: str) -> Dict[str, Any]:
        text = self.extract_text(pdf_path)
        invoice_data = self.parse_invoice(text)
        policy_data = self.parse_policy(text)
        flags = []
        if invoice_data['total'] and invoice_data['total'] > 10000:
            flags.append('Invoice total > 10,000')
        if policy_data['mentions']:
            flags.append(f"Policy mentions: {', '.join(policy_data['mentions'])}")
        action = None
        if flags:
            action = {'type': 'flag_risk', 'flags': flags}
        return {'fields': {'invoice': invoice_data, 'policy': policy_data}, 'flags': flags, 'action': action} 