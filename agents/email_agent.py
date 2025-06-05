import os

from openai import OpenAI
from pydantic import BaseModel

from typing import Dict, Any
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class Email(BaseModel):
    sender: str
    subject: str
    body: str
    urgency: str
    issue: str
    tone: str

class EmailAgent:
    def __init__(self):
        pass

    def extract_fields(self, email_content: str) -> Dict[str, Any]:
        prompt = (
            "You are an email parsing assistant. Extract the following fields from the email content: sender, subject, body, urgency (high or routine), issue (short summary of the main issue), and the tone of the email(polite, angry, threatening, escalation, or neutral). "
            "The email content is: " + email_content
        )
        try:
            completion1 = client.beta.chat.completions.parse(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an email parsing assistant.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format=Email,
            )
            event = completion1.choices[0].message.parsed

            return event.model_dump()
        except Exception as e:
            print(f"[EMAIL_AGENT DEBUG] OpenAI API error: {e}")
            return {"sender": None, "subject": None, "body": email_content, "urgency": "routine", "issue": email_content[:100], "tone": "neutral"}
        

    def trigger_action(self, tone: str, urgency: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        if tone in ['angry', 'escalation', 'threatening'] or urgency == 'high':
            action = {'type': 'escalate', 'target': 'crm', 'fields': fields}
        else:
            action = {'type': 'log_and_close', 'fields': fields}
        return action

    def process(self, email_content: str) -> Dict[str, Any]:
        fields = self.extract_fields(email_content)
        tone = fields['tone']
        action = self.trigger_action(tone, fields['urgency'], fields)
        return {'fields': fields, 'tone': tone, 'action': action} 