# Multi-Agent Chat

Modulares System für Gespräche zwischen mehreren KI-Agenten, implementiert in Python mit Unterstützung für CLI und Web-Interface.

## Features

- **Rundenbasierte Konversationen**: Agenten sprechen nacheinander in definierter Reihenfolge
- **CLI-Interface**: Schönes Terminal-Interface mit Rich Formatierung
- **Web-Interface**: FastAPI-basierte Webanwendung
- **Flexible Agenten-Konfiguration**: JSON-basierte Agentendefinition
- **Ollama-Integration**: Lokale LLM-Ausführung über Ollama
- **Gesprächsspeicherung**: Persistente Speicherung als JSON
- **Erweiterbar**: Modulare Architektur für einfache Erweiterungen

## Installation

### Voraussetzungen

- Python >= 3.10
- Ollama (für lokale LLM-Ausführung)

### Installation aus Quellen

```bash
# Repository klonen
git clone <repository-url>
cd multi_agent_chat

# Virtuelle Umgebung erstellen (empfohlen)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder: venv\Scripts\activate  # Windows

# Paket installieren
pip install -e .

# Oder mit Entwicklungsabhängigkeiten
pip install -e ".[dev]"
```

## Quickstart

### Beispiel-Agenten verwenden

```bash
# Mit den mitgelieferten Beispiel-Agenten starten
multi-agent-chat --agents ./examples/agents --topic "Künstliche Intelligenz" --rounds 3
```

### Web-Interface starten

```bash
python -m multi_agent_chat.web.app
# Oder
uvicorn multi_agent_chat.web.app:app --reload
```

Dann im Browser öffnen: http://localhost:8000

## Nutzung

### CLI

Die CLI unterstützt folgende Optionen:

```bash
multi-agent-chat [OPTIONS]

Optionen:
  --agents, -a PATH     Verzeichnis mit Agenten-JSON-Dateien [default: ./examples/agents]
  --topic, -t TEXT      Gesprächsthema
  --rounds, -r INTEGER  Anzahl der Gesprächsrunden [default: 3]
  --output, -o PATH     Ausgabedatei für Gesprächs-JSON
  --version, -v         Versionsnummer anzeigen
  --help               Hilfe anzeigen

Beispiele:
  # Basisnutzung
  multi-agent-chat

  # Mit eigenem Thema
  multi-agent-chat --topic "Klimawandel und Technologie" --rounds 5

  # Mit Ausgabedatei
  multi-agent-chat --agents ./my_agents --output ./conversation.json
```

### Web Interface

Das Web-Interface bietet eine browserbasierte Oberfläche:

```bash
# Starten
uvicorn multi_agent_chat.web.app:app --host 0.0.0.0 --port 8000

# Endpunkte:
# GET  /       - Hauptseite (Chat-Interface)
# POST /start  - Neue Konversation starten
# GET  /health - Health-Check
```

### Agenten erstellen

Agenten werden als JSON-Dateien definiert:

```bash
# Beispiel: my_agent.json
{
  "name": "MeinAgent",
  "role": "Experte für X",
  "instructions": "Du bist ein Experte...",
  "model": "llama3.2",
  "temperature": 0.7,
  "max_tokens": 300
}
```

## Projektstruktur

```
multi_agent_chat/
├── src/multi_agent_chat/
│   ├── __init__.py          # Paket-Initialisierung
│   ├── models.py            # Pydantic Modelle (Message, AgentConfig, Conversation)
│   ├── ollama_client.py     # Ollama API Client
│   ├── engine.py             # Konversations-Engine
│   ├── storage.py            # JSON-Speicherung
│   ├── loader.py             # Agenten-Loader
│   ├── cli.py                # Rich-basierte CLI
│   └── web/
│       ├── __init__.py
│       ├── app.py            # FastAPI Anwendung
│       ├── templates/        # Jinja2 Templates
│       └── static/           # CSS/JS Dateien
├── examples/
│   └── agents/               # Beispiel-Agenten
│       ├── klaus.json
│       ├── isabella.json
│       └── maria.json
├── tests/                    # Unit- und Integrationstests
├── docs/                     # Dokumentation
├── pyproject.toml           # Projekt-Konfiguration
└── README.md                # Diese Datei
```

## Agenten-Format

Agenten werden als JSON-Dateien definiert mit folgendem Schema:

```json
{
  "name": "string",           // Erforderlich: Name des Agenten
  "role": "string",           // Erforderlich: Rolle/Persönlichkeit
  "instructions": "string",   // Erforderlich: System-Prompt
  "model": "string",          // Optional: LLM-Modell (default: "gpt-4o")
  "temperature": 0.7,         // Optional: 0.0-2.0 (default: 0.7)
  "max_tokens": 300           // Optional: Maximale Token-Anzahl
}
```

### Beispiel-Agenten

**Klaus (Technikexperte)**:
```json
{
  "name": "Klaus",
  "role": "Technikexperte und pragmatischer Entwickler",
  "instructions": "Du bist Klaus, ein erfahrener Softwareentwickler...",
  "model": "llama3.2",
  "temperature": 0.6,
  "max_tokens": 300
}
```

**Isabella (Kreative)**:
```json
{
  "name": "Isabella",
  "role": "Kreative Designerin",
  "instructions": "Du bist Isabella, eine kreative Designerin...",
  "model": "llama3.2",
  "temperature": 0.8,
  "max_tokens": 300
}
```

**Maria (Analytikerin)**:
```json
{
  "name": "Maria",
  "role": "Datenanalytikerin",
  "instructions": "Du bist Maria, eine Analystin mit Blick auf Daten...",
  "model": "llama3.2",
  "temperature": 0.5,
  "max_tokens": 300
}
```

## Entwicklung

### Tests ausführen

```bash
pytest

# Mit Coverage
pytest --cov=multi_agent_chat

# Spezifische Testdatei
pytest tests/test_engine.py
```

### Linting

```bash
ruff check src/
ruff format src/
```

## Ollama-Integration

Das System verwendet Ollama für lokale LLM-Ausführung:

```bash
# Ollama installieren
# Siehe: https://ollama.ai

# Modell herunterladen
ollama pull llama3.2

# Ollama Server starten (im Hintergrund)
ollama serve
```

## API-Referenz

### Core Models

**Message**: Einzelne Nachricht im Gespräch
- `role`: "user", "assistant", oder "system"
- `content`: Nachrichtentext
- `timestamp`: Erstellungszeit
- `agent_id`: Optionaler Agenten-Bezug

**AgentConfig**: Agenten-Konfiguration
- `name`, `role`, `instructions`: Basis-Attribute
- `model`, `temperature`, `max_tokens`: LLM-Parameter

**Conversation**: Gesamtes Gespräch
- `id`, `topic`: Identifikation
- `participants`: Liste der Agenten-Namen
- `messages`: Liste der Message-Objekte
- `started_at`, `ended_at`: Zeitstempel

### Storage

```python
from multi_agent_chat.storage import ConversationStorage

storage = ConversationStorage("./conversations")
storage.save(conversation, "my_chat.json")
loaded = storage.load("my_chat.json")
```

## Lizenz

MIT License - Siehe pyproject.toml

## Autoren

Multi-Agent Chat Team
