from typing import Dict, Any, List, Optional
from pydantic import BaseModel, ValidationError

class JSONSchema(BaseModel):
    event: str
    customer_id: int
    amount: float
    currency: str
    timestamp: str

class JSONAgent:
    def __init__(self):
        pass

    def validate_schema(self, data: Dict[str, Any]) -> List[str]:
        anomalies = []
        try:
            JSONSchema(**data)
        except ValidationError as e:
            for err in e.errors():
                anomalies.append(f"{err['loc'][0]}: {err['msg']}")
        return anomalies

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        anomalies = self.validate_schema(data)
        action = None
        if anomalies:
            action = {'type': 'log_alert', 'anomalies': anomalies, 'fields': data}
        else:
            action = {'type': 'log_and_close', 'fields': data}
        return {'fields': data, 'anomalies': anomalies, 'action': action} 