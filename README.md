# 🎭 Multi-Agent Conversation System

> Ein rundenbasiertes Gesprächssystem mit mehreren KI-Agenten, die unterschiedliche Persönlichkeiten haben und aufeinander reagieren.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Rich](https://img.shields.io/badge/Rich-000000?style=flat)](https://github.com/Textualize/rich)

## 🎬 Demo

Drei Agenten unterhalten sich über ein gemeinsames Thema:

```
╭────────────────────────── Isabella ──────────────────────────╮
│ Hallo, ich bin Isabella! Wollt ihr noch was trinken?       │
│ Habt ihr schon die Wale in Samaná gesehen?                 │
╰────────────────────────────────────────────────────────────╯
╭─────────────────────────── Klaus ────────────────────────────╮
│ Isabella, bring mir ein Bier und lass das Paradies-Gerede. │
│ Die Wale interessieren mich erst, wenn die Boote gewartet  │
│ sind. Heute wird nicht gefaulenzt.                          │
╰──────────────────────────────────────────────────────────────╯
╭─────────────────────────── Maria ────────────────────────────╮
│ Klaus, lass die Technik doch ruhen und komm mit uns die      │
│ tanzenden Wale bestaunen, die wie ein lebendiges Gemälde   │
│ wirken. Es ist schöner, die Natur zu genießen.              │
╰──────────────────────────────────────────────────────────────╯
```

## 👥 Die Agenten

| Agent | Persönlichkeit | Markenzeichen | Modell |
|-------|----------------|---------------|--------|
| **Isabella** | 🍹 Quirlige Kellnerin | *"Wollt ihr noch was trinken?"* — bringt ständig neue Themen rein | gemini-3-flash |
| **Klaus** | 🔧 Techniker aus Lahr | Pragmatisch, nörgelt gerne über Technik, will Dinge reparieren | kimi-k2.5 |
| **Maria** | 🎨 Entspannte Künstlerin | Sieht Poesie in allem — *"wie ein lebendiges Gemälde"* | gemini-3-flash |

## 🚀 Installation

### Voraussetzungen

- Python >= 3.10
- Git

### Setup

```bash
# Repository klonen
git clone https://github.com/aklaus69/LenaSims.git
cd LenaSims

# Virtuelle Umgebung erstellen
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder: venv\Scripts\activate  # Windows

# Abhängigkeiten installieren
pip install -e ".[dev]"
```

## 💻 Usage

### CLI (Terminal)

```bash
# Mit den Beispiel-Agenten starten
multi-agent-chat --topic "Urlaub in der DomRep" --rounds 5

# Eigene Agenten verwenden
multi-agent-chat --agents ./my_agents --topic "Künstliche Intelligenz" --rounds 3

# Mit Ausgabedatei
multi-agent-chat --output gespraech.json
```

### Web-Interface

```bash
# Server starten
python -m uvicorn multi_agent_chat.web.app:app --reload --host 0.0.0.0 --port 8000

# Browser öffnen
open http://localhost:8000
```

## 🏗️ Projektstruktur

```
LenaSims/
├── src/multi_agent_chat/
│   ├── models.py        # Pydantic Models
│   ├── ollama_client.py  # Async HTTP-Client
│   ├── engine.py        # Gesprächslogik
│   ├── storage.py       # JSON Speicherung
│   ├── loader.py        # Agenten-Loader
│   ├── cli.py           # Rich CLI
│   └── web/
│       └── app.py       # FastAPI Web-Interface
├── examples/
│   └── agents/          # Klaus, Maria, Isabella
├── tests/               # 73 Unit-Tests
├── pyproject.toml       # Projekt-Konfiguration
└── README.md           # Diese Datei
```

## ⚙️ Agenten konfigurieren

```json
{
    "name": "Klaus",
    "role": "Technikexperte aus Lahr",
    "instructions": "Du bist Klaus. Antworte immer mit maximal 3 Sätzen.",
    "model": "kimi-k2.5:cloud",
    "temperature": 0.6
}
```

## ✨ Features

- ✅ Rundenbasierte Gespräche
- ✅ Agenten reagieren namentlich aufeinander
- ✅ Themen-Steuerung
- ✅ Kontext-Speicherung
- ✅ CLI + Web Interface
- ✅ 73 Unit-Tests

## 🧪 Tests

```bash
pytest tests/ -v  # 73 Tests passing
```

## 📄 Lizenz

MIT License

---

<p align="center"><i>Erstellt mit ❤️ für KI-gestützte Unterhaltungen</i></p>
