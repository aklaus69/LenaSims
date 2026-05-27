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

from ..loader import load_all_agents
from ..engine import ConversationEngine
from ..models import AgentConfig, Conversation, Message
from ..model_selector import AVAILABLE_MODELS
from ..agent_configurator import PREDEFINED_PERSONALITIES
from ..human_agent import HumanAgent

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


class ChatMessage(BaseModel):
    """A chat message."""
    agent: str
    content: str
    timestamp: str
    is_human: bool = False


# Connection manager for WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.conversations: dict = {}
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
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
        "index.html",
        context={"request": request, "title": "Multi-Agent Chat"},
    )


@app.get("/api/models")
async def get_available_models():
    """Get list of available Ollama models."""
    models = []
    for key, (model_name, desc, emoji) in AVAILABLE_MODELS.items():
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
    for key, (name, desc, temp) in PREDEFINED_PERSONALITIES.items():
        personalities.append({
            "id": key,
            "name": name,
            "description": desc[:100] + "..." if desc and len(desc) > 100 else desc,
            "temperature": temp
        })
    return {"personalities": personalities}


@app.get("/api/temperatures")
async def get_temperature_options():
    """Get temperature options."""
    return {
        "options": [
            {"value": 0.3, "label": "Präzise (0.3)", "desc": "Fakten, Logik"},
            {"value": 0.6, "label": "Ausgewogen (0.6)", "desc": "Empfohlen"},
            {"value": 0.8, "label": "Kreativ (0.8)", "desc": "Experimentell"},
            {"value": 1.0, "label": "Chaos (1.0)", "desc": "Sehr zufällig"},
        ]
    }


@app.get("/api/default-agents")
async def get_default_agents():
    """Get default agent configurations."""
    try:
        agents_dir = project_dir / "examples" / "agents"
        agents = load_all_agents(agents_dir)
        
        return {
            "agents": [
                {
                    "name": agent.name,
                    "role": agent.role,
                    "instructions": agent.instructions,
                    "model": agent.model,
                    "temperature": agent.temperature
                }
                for agent in agents
            ]
        }
    except Exception as e:
        # Return hardcoded defaults if files not found
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
        # Convert request agents to AgentConfig
        agent_configs = []
        for agent_req in request.agents:
            config = AgentConfig(
                name=agent_req.name,
                role=agent_req.role,
                instructions=agent_req.instructions,
                model=agent_req.model,
                temperature=agent_req.temperature
            )
            agent_configs.append(config)
        
        # Add human agent if requested
        if request.include_human:
            human_config = AgentConfig(
                name="Du (Mensch)",
                role="Menschlicher Teilnehmer",
                instructions="Ein realer Mensch im Gespräch.",
                model="human",
                temperature=0.0
            )
            agent_configs.append(human_config)
        
        # Create conversation
        conversation_id = f"web_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return {
            "status": "ok",
            "conversation_id": conversation_id,
            "agents": [a.name for a in agent_configs],
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
            # Receive message (could be config or human input)
            data = await websocket.receive_json()
            
            if data.get("type") == "start":
                # Start conversation
                await handle_conversation_start(websocket, data)
            elif data.get("type") == "human_response":
                # Human sent a message
                await handle_human_response(websocket, data)
            elif data.get("type") == "stop":
                # Stop conversation
                break
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
        manager.disconnect(websocket)


async def handle_conversation_start(websocket: WebSocket, data: dict):
    """Handle conversation start via WebSocket."""
    try:
        # Parse agents from config
        agents = []
        for agent_data in data.get("agents", []):
            config = AgentConfig(
                name=agent_data["name"],
                role=agent_data["role"],
                instructions=agent_data["instructions"],
                model=agent_data["model"],
                temperature=agent_data["temperature"]
            )
            agents.append(config)
        
        topic = data.get("topic", "")
        rounds = data.get("rounds", 3)
        include_human = data.get("include_human", False)
        
        # Create conversation
        conversation = Conversation(
            id=f"ws_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            topic=topic
        )
        
        # Send start message
        await websocket.send_json({
            "type": "system",
            "content": f"Gespräch gestartet: {topic}" if topic else "Gespräch gestartet",
            "rounds": rounds,
            "agents": [a.name for a in agents]
        })
        
        # Run conversation
        await run_websocket_conversation(websocket, conversation, agents, rounds, include_human)
        
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })


async def run_websocket_conversation(
    websocket: WebSocket,
    conversation: Conversation,
    agents: List[AgentConfig],
    rounds: int,
    include_human: bool
):
    """Run conversation and stream via WebSocket."""
    human_agents = {a.name: HumanAgent(a) for a in agents if a.model == "human"}
    
    async with ConversationEngine(conversation, agents) as engine:
        for round_num in range(rounds):
            await websocket.send_json({
                "type": "round_start",
                "round": round_num + 1,
                "total_rounds": rounds
            })
            
            for agent in agents:
                if agent.model == "human":
                    # Wait for human input
                    await websocket.send_json({
                        "type": "human_turn",
                        "agent": agent.name,
                        "message": "Du bist dran!"
                    })
                    
                    # Wait for response (handled in main loop)
                    # For now, continue to next agent
                    continue
                
                try:
                    message = await engine.run_round(current_agent=agent)
                    await websocket.send_json({
                        "type": "message",
                        "agent": message.agent_id,
                        "content": message.content,
                        "is_human": False,
                        "round": round_num + 1
                    })
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "agent": agent.name,
                        "message": str(e)
                    })
        
        await websocket.send_json({
            "type": "complete",
            "total_messages": len(conversation.messages),
            "participants": conversation.participants
        })


async def handle_human_response(websocket: WebSocket, data: dict):
    """Handle response from human user."""
    # This would need storage of conversation state
    # Simplified version - just echo back
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
