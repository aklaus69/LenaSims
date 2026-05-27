"""
Web interface for Multi-Agent Chat with full configuration.
Supports agent config, model selection, human mode, and live chat.
"""

import asyncio
import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI(
    title="Multi-Agent Chat",
    description="A modular multi-agent conversation system with full web configuration",
    version="0.2.0",
)

# Get the web directory path
web_dir = Path(__file__).parent
project_dir = web_dir.parent.parent.parent

# Mount static files
app.mount("/static", StaticFiles(directory=web_dir / "static"), name="static")

# Setup templates
templates = Jinja2Templates(directory=web_dir / "templates")


# Available models data (copied to avoid import issues)
AVAILABLE_MODELS_DATA = {
    "1": ("kimi-k2.5:cloud", "Kimik2.5 Cloud - Großes Modell, tiefes Verständnis", "🧠"),
    "2": ("gemini-3-flash-preview:latest", "Gemini Flash - Schnell, kreativ", "⚡"),
    "3": ("icky/translate:latest", "Icky Translate - Kompakt, spezialisiert", "🔄"),
    "4": ("llama3.2:latest", "Llama 3.2 - Lokal, effizient", "🦙"),
    "5": ("mistral:latest", "Mistral - Ausgewogen", "🌪️"),
}

PREDEFINED_PERSONALITIES_DATA = {
    "1": ("Klaus (Techniker)", "Du bist Klaus, ein praktischer Techniker aus Lahr...", 0.6),
    "2": ("Maria (Künstlerin)", "Du bist Maria, eine entspannte Künstlerin...", 0.8),
    "3": ("Isabella (Kellnerin)", "Du bist Isabella, eine quirlige Kellnerin...", 0.9),
    "4": ("Oskar (Pessimist)", "Du bist Oskar, ein chronischer Pessimist...", 0.7),
    "5": ("Sophie (Optimistin)", "Du bist Sophie, eine unerschütterliche Optimistin...", 0.85),
    "6": ("Professor (Gelehrter)", "Du bist ein Professor...", 0.4),
}


class AgentConfigRequest(BaseModel):
    """Request for configuring an agent."""
    name: str
    role: str
    instructions: str
    model: str
    temperature: float


class StartConversationRequest(BaseModel):
    """Request to start a conversation."""
    topic: str = ""
    rounds: int = 3
    agents: List[AgentConfigRequest]
    include_human: bool = False


# Connection manager for WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.conversations: dict = {}
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the main configuration interface."""
    return templates.TemplateResponse(
        request,
        "index.html",
        {"title": "Multi-Agent Chat"},
    )


@app.get("/api/models")
async def get_available_models():
    """Get list of available Ollama models."""
    models = []
    for key, (model_name, desc, emoji) in AVAILABLE_MODELS_DATA.items():
        models.append({
            "id": key,
            "name": model_name,
            "description": desc,
            "emoji": emoji
        })
    return {"models": models}


@app.get("/api/personalities")
async def get_personalities():
    """Get predefined personality templates."""
    personalities = []
    for key, (name, desc, temp) in PREDEFINED_PERSONALITIES_DATA.items():
        personalities.append({
            "id": key,
            "name": name,
            "description": desc[:50] + "..." if desc else desc,
            "temperature": temp
        })
    return {"personalities": personalities}


@app.get("/api/default-agents")
async def get_default_agents():
    """Get default agent configurations."""
    return {
        "agents": [
            {
                "name": "Klaus",
                "role": "Techniker aus Lahr",
                "instructions": "Du bist Klaus, ein praktischer Techniker. Antworte kurz (1-2 Sätze).",
                "model": "gemini-3-flash-preview:latest",
                "temperature": 0.6
            },
            {
                "name": "Maria",
                "role": "Künstlerin",
                "instructions": "Du bist Maria, eine entspannte Künstlerin. Antworte kurz (1-2 Sätze).",
                "model": "gemini-3-flash-preview:latest",
                "temperature": 0.8
            },
            {
                "name": "Isabella",
                "role": "Kellnerin",
                "instructions": "Du bist Isabella, eine quirlige Kellnerin. Antworte kurz (1-2 Sätze).",
                "model": "gemini-3-flash-preview:latest",
                "temperature": 0.9
            }
        ]
    }


@app.post("/api/start")
async def start_conversation(request: StartConversationRequest):
    """Start a new conversation session."""
    try:
        return {
            "status": "ok",
            "message": "Ready for WebSocket connection",
            "agents": [a.name for a in request.agents],
            "topic": request.topic,
            "rounds": request.rounds,
            "include_human": request.include_human
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for live chat."""
    await manager.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "start":
                await handle_conversation_start(websocket, data)
            elif data.get("type") == "human_response":
                await handle_human_response(websocket, data)
            elif data.get("type") == "stop":
                break
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except:
            pass
        manager.disconnect(websocket)


async def handle_conversation_start(websocket: WebSocket, data: dict):
    """Handle conversation start via WebSocket."""
    try:
        topic = data.get("topic", "")
        rounds = data.get("rounds", 3)
        agents = data.get("agents", [])
        include_human = data.get("include_human", False)
        
        # Send start message
        await websocket.send_json({
            "type": "system",
            "content": f"Gespräch gestartet: {topic}" if topic else "Gespräch gestartet",
            "rounds": rounds,
            "agents": [a.get("name", "Agent") for a in agents]
        })
        
        # Mock conversation (simplified for web)
        await websocket.send_json({
            "type": "complete",
            "total_messages": 0,
            "participants": [a.get("name") for a in agents]
        })
        
    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})


async def handle_human_response(websocket: WebSocket, data: dict):
    """Handle response from human user."""
    await websocket.send_json({
        "type": "message",
        "agent": data.get("agent", "Human"),
        "content": data.get("content", ""),
        "is_human": True
    })


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.2.0"}
