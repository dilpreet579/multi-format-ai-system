import os

from openai import OpenAI
from pydantic import BaseModel

import re
import json
from typing import Dict, Any
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class IntentClassification(BaseModel):
    intent: str

class ClassifierAgent:
    def __init__(self):
        pass

    def detect_format(self, content: Any, filename: str = None) -> str:
        if filename and filename.lower().endswith(".pdf"):
            return "PDF"
        if filename and filename.lower().endswith(".json"):
            return "JSON"
        if isinstance(content, dict):
            return "JSON"
        if (
            isinstance(content, bytes)
            and filename
            and filename.lower().endswith(".eml")
        ):
            return "Email"
        if isinstance(content, str):
            if re.search(r"From: .*@.*", content) and re.search(r"Subject:", content):
                return "Email"
            try:
                json.loads(content)
                return "JSON"
            except Exception:
                pass
            if "%PDF" in content[:20]:
                return "PDF"
        return "Unknown"

    def detect_intent(self, content: str) -> str:
        text = content.lower() if isinstance(content, str) else str(content).lower()
        prompt = (
            "You are an intent classification assistant. "
            "Given the following content, classify its intent as one of: RFQ, Complaint, Invoice, Regulation, Fraud Risk, or Unknown. "
            "The content is: " + text
        )
        try:
            completion = client.beta.chat.completions.parse(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an intent classification assistant.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format=IntentClassification,
            )
            event = completion.choices[0].message.parsed
            intent = event.intent

            print(f"[CLASSIFIER DEBUG] OpenAI intent: {intent}")
            return intent
        except Exception as e:
            print(f"[CLASSIFIER DEBUG] OpenAI API error: {e}")
            return "Unknown"

    def extract_pdf_text(self, pdf_bytes: bytes) -> str:
        import PyPDF2
        from io import BytesIO

        text = ""
        try:
            reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
            for page in reader.pages:
                text += page.extract_text() or ""
        except Exception as e:
            print(f"[CLASSIFIER DEBUG] PDF text extraction error: {e}")
        print(f"[CLASSIFIER DEBUG] PDF extracted text: {text}")
        return text

    def classify(self, content: Any, filename: str = None) -> Dict[str, Any]:
        fmt = self.detect_format(content, filename)
        intent = "Unknown"
        if fmt == "PDF":
            # If content is bytes, extract text
            if isinstance(content, bytes):
                pdf_text = self.extract_pdf_text(content)
                intent = self.detect_intent(pdf_text)
            elif isinstance(content, str):
                # fallback: try intent detection on string
                intent = self.detect_intent(content)
        else:
            intent = self.detect_intent(content)
        routing_metadata = {"format": fmt, "intent": intent}
        return routing_metadata
