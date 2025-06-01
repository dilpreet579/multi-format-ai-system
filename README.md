# Multi-Format Autonomous AI System with Contextual Decisioning & Chained Actions

## Overview
A multi-agent system that processes Email, JSON, and PDF inputs, classifies format and business intent, routes to specialized agents, and dynamically chains follow-up actions based on extracted data.

## Architecture
![Architecture Diagram](./diagram.png)

## Features
- Format and intent classification
- Specialized agents for Email, JSON, PDF
- Shared memory store (SQLite)
- Action router for follow-up actions
- REST API (FastAPI)
- (Bonus) Simple UI

## Setup

### 1. Clone the Repository
```bash
git clone https://github.com/dilpreet579/multi-format-ai.git
```

### 2. Create and Activate a Virtual Environment
```bash
python -m venv multiai
# On Windows:
.\multiai\Scripts\activate
# On macOS/Linux:
source multiai/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Usage
Run the API server:
```bash
uvicorn api.main:app --reload
```

## Sample Inputs
See `samples/` directory.

## Output Logs
See `/logs` endpoint or memory store.

## Git Repository Best Practices
- Commit changes with clear messages.
- Use branches for new features or experiments.
- Pull latest changes before starting new work.
- Keep sensitive data (API keys, .env) out of the repo (add to `.gitignore`).

## Screenshots
(Include after running demo) 