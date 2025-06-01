import re
import json
from typing import Dict, Any

class ClassifierAgent:
    def __init__(self):
        self.intent_keywords = {
            'RFQ': ['request for quote', 'rfq', 'quotation'],
            'Complaint': ['complaint', 'dissatisfied', 'unacceptable', 'angry'],
            'Invoice': ['invoice', 'total', 'amount due'],
            'Regulation': ['regulation', 'policy', 'compliance', 'gdpr', 'fda'],
            'Fraud Risk': ['fraud', 'risk', 'anomaly', 'suspicious']
        }

    def detect_format(self, content: Any, filename: str = None) -> str:
        if filename and filename.lower().endswith('.pdf'):
            return 'PDF'
        if filename and filename.lower().endswith('.json'):
            return 'JSON'
        if isinstance(content, dict):
            return 'JSON'
        if isinstance(content, bytes) and filename and filename.lower().endswith('.eml'):
            return 'Email'
        if isinstance(content, str):
            if re.search(r'From: .*@.*', content) and re.search(r'Subject:', content):
                return 'Email'
            try:
                json.loads(content)
                return 'JSON'
            except Exception:
                pass
            if '%PDF' in content[:20]:
                return 'PDF'
        return 'Unknown'

    def detect_intent(self, content: str) -> str:
        text = content.lower() if isinstance(content, str) else str(content).lower()
        print(f"[CLASSIFIER DEBUG] Text for intent detection: {text}")
        for intent, keywords in self.intent_keywords.items():
            for kw in keywords:
                print(f"[CLASSIFIER DEBUG] Checking keyword: {kw}")
                if re.search(rf'{re.escape(kw)}(\W|$)', text):
                    print(f"[CLASSIFIER DEBUG] Matched intent: {intent}")
                    return intent
        print("[CLASSIFIER DEBUG] No intent matched.")
        return 'Unknown'

    def extract_pdf_text(self, pdf_bytes: bytes) -> str:
        import PyPDF2
        from io import BytesIO
        text = ''
        try:
            reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
            for page in reader.pages:
                text += page.extract_text() or ''
        except Exception as e:
            print(f"[CLASSIFIER DEBUG] PDF text extraction error: {e}")
        print(f"[CLASSIFIER DEBUG] PDF extracted text: {text}")
        return text

    def classify(self, content: Any, filename: str = None) -> Dict[str, Any]:
        fmt = self.detect_format(content, filename)
        intent = 'Unknown'
        if fmt == 'PDF':
            # If content is bytes, extract text
            if isinstance(content, bytes):
                pdf_text = self.extract_pdf_text(content)
                intent = self.detect_intent(pdf_text)
            elif isinstance(content, str):
                # fallback: try intent detection on string
                intent = self.detect_intent(content)
        else:
            intent = self.detect_intent(content)
        routing_metadata = {'format': fmt, 'intent': intent}
        return routing_metadata 