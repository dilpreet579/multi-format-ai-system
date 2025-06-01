from typing import Dict, Any, List

class JSONAgent:
    REQUIRED_FIELDS = {
        'event': str,
        'customer_id': int,
        'amount': float,
        'currency': str,
        'timestamp': str
    }

    def __init__(self):
        pass

    def validate_schema(self, data: Dict[str, Any]) -> List[str]:
        anomalies = []
        for field, ftype in self.REQUIRED_FIELDS.items():
            if field not in data:
                anomalies.append(f'Missing field: {field}')
            else:
                try:
                    if ftype == float:
                        float(data[field])
                    elif not isinstance(data[field], ftype):
                        anomalies.append(f'Field {field} type mismatch: expected {ftype.__name__}, got {type(data[field]).__name__}')
                except Exception:
                    anomalies.append(f'Field {field} type error: {data[field]}')
        return anomalies

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        anomalies = self.validate_schema(data)
        action = None
        if anomalies:
            action = {'type': 'log_alert', 'anomalies': anomalies}
        return {'fields': data, 'anomalies': anomalies, 'action': action} 