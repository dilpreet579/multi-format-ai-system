import requests
import time
import os
from enum import Enum
from typing import Optional

class ActionType(Enum):
    ESCALATE = 'escalate'
    FLAG_RISK = 'flag_risk'
    LOG_ALERT = 'log_alert'
    LOG_AND_CLOSE = 'log_and_close'

ACTION_ENDPOINTS = {
    ActionType.ESCALATE.value: '/crm/escalate',
    ActionType.FLAG_RISK.value: '/risk_alert',
    ActionType.LOG_ALERT.value: '/log_alert',
    ActionType.LOG_AND_CLOSE.value: '/log_and_close',
}

class ActionRouter:
    def __init__(self, base_url='http://localhost:8000', in_process: bool = True, retries: int = 3, timeout: int = 2):
        self.base_url = base_url
        self.in_process = in_process
        self.retries = retries
        self.timeout = timeout
        try:
            from fastapi.testclient import TestClient
            from api.main import app
            self.client = TestClient(app)
        except Exception:
            self.client = None
            self.in_process = False

    def trigger_action(self, action: Optional[dict]) -> dict:
        """
        Route the action to the appropriate endpoint, either in-process or via HTTP.
        """
        if not action:
            return {'status': 'no_action'}
        endpoint = ACTION_ENDPOINTS.get(action.get('type'))
        if not endpoint:
            return {'status': 'unknown_action'}
        if self.in_process and self.client:
            resp = self.client.post(endpoint, json=action)
            if resp.status_code == 200:
                return {'status': 'success', 'response': resp.json()}
            else:
                return {'status': 'failed', 'error': resp.text}
        url = self.base_url + endpoint
        for attempt in range(self.retries):
            try:
                resp = requests.post(url, json=action, timeout=self.timeout)
                if resp.status_code == 200:
                    return {'status': 'success', 'response': resp.json()}
            except Exception as e:
                print(f"[ActionRouter] Attempt {attempt+1} failed: {e}")
                time.sleep(1)
        return {'status': 'failed', 'error': str(action)} 