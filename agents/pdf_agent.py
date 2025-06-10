import os

from openai import OpenAI
from pydantic import BaseModel

import PyPDF2
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class LineItem(BaseModel):
    description: str
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    total: Optional[float] = None

class PDFExtraction(BaseModel):
    # Invoice fields
    total: Optional[float] = None
    currency: Optional[str] = None
    line_items: Optional[List[LineItem]] = None
    # Policy fields
    policy_mentions: Optional[List[str]] = None
    # Document type
    doc_type: Optional[str] = None  # 'invoice', 'policy', or 'unknown'

class PDFAgent:
    def __init__(self):
        pass

    def extract_pdf_text(self, pdf_bytes: bytes) -> str:
        from io import BytesIO
        text = ''
        try:
            reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
            for page in reader.pages:
                text += page.extract_text() or ''
        except Exception as e:
            print(f"[PDF_AGENT DEBUG] PDF text extraction error: {e}")
        return text
    

    def parse_pdf(self, text: str) -> dict:
        prompt = (
            "You are a document parsing assistant. The document may be an invoice or a policy document. "
            "If it is an invoice, extract: total, currency, and all line items (each with description, quantity, unit_price, total). "
            "If it is a policy document, extract a list of compliance mentions (GDPR, FDA, HIPAA, SOX, etc). "
            "Also, return a field 'doc_type' as either 'invoice', 'policy', or 'unknown'. "
            "Return your answer as a JSON object with keys: total, currency, line_items, policy_mentions, doc_type. "
            f"Document text: {text}"
        )
        try:
            completion = client.beta.chat.completions.parse(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a document parsing assistant."},
                    {"role": "user", "content": prompt}
                ],
                response_format=PDFExtraction,
            )
            event = completion.choices[0].message.parsed
            return event.model_dump()
        except Exception as e:
            print(f"[PDF_AGENT DEBUG] OpenAI PDF extraction error: {e}")
            return {
                "total": None,
                "currency": None,
                "line_items": [],
                "policy_mentions": [],
                "doc_type": "unknown"
            }

    def process(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Process a PDF from bytes, extract text, parse invoice fields, and policy mentions."""
        text = self.extract_pdf_text(pdf_bytes)
        extraction = self.parse_pdf(text)
        flags = []
        if extraction.get('total') and extraction['total'] > 10000:
            flags.append('Invoice total > 10,000')
        if extraction.get('policy_mentions'):
            flags.append(f"Policy mentions: {', '.join(extraction['policy_mentions'])}")
        action = None
        if flags:
            action = {'type': 'flag_risk', 'flags': flags}
        else:
            action = {'type': 'log_and_close', 'fields': extraction}
        return {
            'fields': extraction,
            'flags': flags,
            'action': action
        } 