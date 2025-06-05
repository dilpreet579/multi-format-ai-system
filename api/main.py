import os
import json
from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from agents.classifier_agent import ClassifierAgent
from agents.email_agent import EmailAgent
from agents.json_agent import JSONAgent
from agents.pdf_agent import PDFAgent
from memory.memory_store import MemoryStore
from router.action_router import ActionRouter

app = FastAPI(
    title="Multi-Format Autonomous AI System",
    description="A system that processes inputs from Email, JSON, and PDF, classifies format and business intent, routes to specialized agents, and dynamically chains follow-up actions.",
    version="1.0.0"
)

templates = Jinja2Templates(directory="templates")

# Mount static files if directory exists
if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
else:
    print("Static directory not found. UI features will be limited.")

classifier = ClassifierAgent()
email_agent = EmailAgent()
json_agent = JSONAgent()
pdf_agent = PDFAgent()
memory = MemoryStore()
action_router = ActionRouter()

def error_response(message: str, status_code: int = 400):
    return JSONResponse({"error": message}, status_code=status_code)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        return error_response(f"Failed to serve UI: {str(e)}", status_code=500)

@app.post('/upload')
async def upload(request: Request, file: UploadFile = File(None), json_data: str = Form(None)):
    try:
        source = 'upload'
        filename = file.filename if file else None
        content = None
        if file:
            raw = await file.read()
            try:
                content = raw.decode('utf-8')
            except Exception:
                content = raw
        elif json_data:
            content = json.loads(json_data)
        else:
            return error_response('No input provided', status_code=400)
        classification = classifier.classify(content, filename)
        fmt = classification['format']
        intent = classification['intent']
        agent_result = {}
        action = None
        if fmt == 'Email':
            agent_result = email_agent.process(content)
            action = agent_result['action']
        elif fmt == 'JSON':
            if isinstance(content, str):
                content = json.loads(content)
            agent_result = json_agent.process(content)
            action = agent_result['action']
        elif fmt == 'PDF':
            pdf_bytes = content if isinstance(content, bytes) else content.encode('utf-8')
            agent_result = pdf_agent.process(pdf_bytes)
            action = agent_result['action']
        else:
            return error_response('Unsupported file format', status_code=400)
        router_result = action_router.trigger_action(action)
        trace = {
            'classification': classification,
            'agent_result': agent_result,
            'router_result': router_result
        }
        memory.log_entry(source, fmt, intent, classification, agent_result.get('fields', {}), action, trace)
        return trace
    except Exception as e:
        return error_response(str(e), status_code=500)

@app.post('/crm/escalate')
async def crm_escalate(payload: dict):
    return {'status': 'CRM escalation simulated', 'payload': payload}

@app.post('/risk_alert')
async def risk_alert(payload: dict):
    return {'status': 'Risk alert simulated', 'payload': payload}

@app.post('/log_alert')
async def log_alert(payload: dict):
    return {'status': 'Alert logged', 'payload': payload}

@app.post('/log_and_close')
async def log_and_close(payload: dict):
    return {'status': 'Logged and closed', 'payload': payload}

@app.get('/logs')
async def get_logs():
    logs = memory.get_logs()
    return {'logs': logs} 