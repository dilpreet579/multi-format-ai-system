import re
from textblob import TextBlob
from typing import Dict, Any

class EmailAgent:
    def __init__(self):
        pass

    def extract_fields(self, email_content: str) -> Dict[str, Any]:
        sender = re.search(r'From: (.*)', email_content)
        sender = sender.group(1).strip() if sender else None
        subject = re.search(r'Subject: (.*)', email_content)
        subject = subject.group(1).strip() if subject else None
        body = email_content.split('\n\n', 1)[-1]
        urgency = 'high' if re.search(r'urgent|immediate|asap|unacceptable', body, re.I) else 'routine'
        issue = subject if subject else body[:100]
        return {'sender': sender, 'subject': subject, 'urgency': urgency, 'issue': issue, 'body': body}

    def detect_tone(self, body: str) -> str:
        blob = TextBlob(body)
        polarity = blob.sentiment.polarity
        if polarity < -0.3:
            return 'angry'
        elif polarity > 0.3:
            return 'polite'
        elif re.search(r'threat|legal|lawsuit', body, re.I):
            return 'threatening'
        elif re.search(r'escalate|unacceptable', body, re.I):
            return 'escalation'
        return 'neutral'

    def trigger_action(self, tone: str, urgency: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        if tone in ['angry', 'escalation', 'threatening'] or urgency == 'high':
            action = {'type': 'escalate', 'target': 'crm', 'fields': fields}
        else:
            action = {'type': 'log_and_close', 'fields': fields}
        return action

    def process(self, email_content: str) -> Dict[str, Any]:
        fields = self.extract_fields(email_content)
        tone = self.detect_tone(fields['body'])
        action = self.trigger_action(tone, fields['urgency'], fields)
        return {'fields': fields, 'tone': tone, 'action': action} 