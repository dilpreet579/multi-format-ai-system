import requests
import time
import os

class ActionRouter:
    def __init__(self, base_url='http://localhost:8000', in_process: bool = True):
        self.base_url = base_url
        self.in_process = in_process
        try:
            from fastapi.testclient import TestClient
            from api.main import app
            self.client = TestClient(app)
        except Exception:
            self.client = None
            self.in_process = False

    def trigger_action(self, action: dict) -> dict:
        if not action:
            return {'status': 'no_action'}
        endpoint = None
        if action['type'] == 'escalate':
            endpoint = '/crm/escalate'
        elif action['type'] == 'flag_risk':
            endpoint = '/risk_alert'
        elif action['type'] == 'log_alert':
            endpoint = '/log_alert'
        elif action['type'] == 'log_and_close':
            endpoint = '/log_and_close'
        if not endpoint:
            return {'status': 'unknown_action'}
        if self.in_process and self.client:
            resp = self.client.post(endpoint, json=action)
            if resp.status_code == 200:
                return {'status': 'success', 'response': resp.json()}
            else:
                return {'status': 'failed', 'error': resp.text}
        url = self.base_url + endpoint
        for attempt in range(3):
            try:
                resp = requests.post(url, json=action, timeout=2)
                if resp.status_code == 200:
                    return {'status': 'success', 'response': resp.json()}
            except Exception as e:
                time.sleep(1)
        return {'status': 'failed', 'error': str(action)} 