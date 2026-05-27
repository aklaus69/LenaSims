# 🎭 Multi-Agent Conversation System

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Rich](https://img.shields.io/badge/Rich-000000?style=flat)](https://github.com/Textualize/rich)

> Ein rundenbasiertes Gesprächssystem mit mehreren KI-Agenten, die unterschiedliche Persönlichkeiten haben und aufeinander reagieren – **jetzt auch mit menschlichen Teilnehmern!**

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

### 🧑‍💻 Mit menschlichem Teilnehmer:

```
╭────────────────────────── Isabella ──────────────────────────╮
│ Wollt ihr noch was trinken? Heute gibt's frischen Kaffee!  │
╰────────────────────────────────────────────────────────────╯
╭────────────────────── 🧑‍💻 Klaus (Du) ────────────────────────╮
│ Ich nehme einen Espresso. Und erzählt mal, was gibt's Neues?│
╰──────────────────────────────────────────────────────────────╯
╭─────────────────────────── Maria ────────────────────────────╮
│ Ooh, Espresso! Der ist wie dunkle Musik in einer Tasse...   │
╰──────────────────────────────────────────────────────────────╯
```

## ✨ Features

- ✅ **Rundenbasiert** — Agenten sprechen nacheinander
- ✅ **Interaktiv** — Agenten reagieren namentlich aufeinander
- ✅ **🧑‍💻 Menschlicher Teilnehmer** — Du kannst mit den Agenten chatten!
- ✅ **🎨 Vollständige Konfiguration** — Namen, Persönlichkeiten, Temperaturen, Modelle
- ✅ **🤖 Modell-Auswahl** — Pro-Agent Modell wählen (Kimi, Gemini, Llama, etc.)
- ✅ **Themen-Steuerung** — Gespräch über definiertes Topic
- ✅ **Kontext** — Gesprächsverlauf bleibt erhalten
- ✅ **CLI + Web** — Terminal-Interface und Browser-App
- ✅ **73 Unit-Tests** — Vollständig getestet

## 👥 Die Agenten

| Agent | Persönlichkeit | Markenzeichen | Standard-Modell |
|-------|----------------|---------------|-----------------|
| **Isabella** | 🍹 Quirlige Kellnerin | *"Wollt ihr noch was trinken?"* — bringt ständig neue Themen rein | gemini-3-flash |
| **Klaus** | 🔧 Techniker aus Lahr | Pragmatisch, nörgelt gerne über Technik | kimi-k2.5 |
| **Maria** | 🎨 Entspannte Künstlerin | Sieht Poesie in allem — *"wie ein lebendiges Gemälde"* | gemini-3-flash |
| **🧑‍💻 Du** | Menschlicher Teilnehmer | Beeinflusse das Gespräch! | — |

## 🚀 Installation

### Voraussetzungen

- Python >= 3.10
- Git
- Ollama (für lokale Modelle)

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

### Grundlegende Nutzung

```bash
# Mit den Beispiel-Agenten starten
multi-agent-chat --topic "Urlaub in der DomRep" --rounds 5

# Mit Ausgabedatei
multi-agent-chat --output gespraech.json
```

### 🧑‍💻 Mit menschlichem Teilnehmer

```bash
# Du selbst nimmst am Gespräch teil!
multi-agent-chat --human --topic "Kaffeeklatsch" --rounds 3

# Kurzform
multi-agent-chat -H -t "Technik-Talk" -r 2
```

**Während des Gesprächs:**
- Tippe deine Nachricht und drücke ENTER
- LEER (ENTER) = überspringen
- `exit` = Gespräch beenden

### 🎨 Vollständige Konfiguration (-c)

Ändere **alles** interaktiv: Namen, Persönlichkeiten, Temperaturen, Modelle

```bash
multi-agent-chat -c --topic "Neues Thema"
```

**Vorgefertigte Persönlichkeiten:**

| # | Persönlichkeit | Temp | Stil |
|---|----------------|------|------|
| `[1]` | Klaus (Techniker) | 0.6 | 🔧 Pragmatisch, nörgelt |
| `[2]` | Maria (Künstlerin) | 0.8 | 🎨 Poetisch, entspannt |
| `[3]` | Isabella (Kellnerin) | 0.9 | ☕ Quirlig, enthusiastisch |
| `[4]` | Oskar (Pessimist) | 0.7 | 😒 Chronisch negativ |
| `[5]` | Sophie (Optimistin) | 0.85 | 🌈 Unerschütterlich positiv |
| `[6]` | Professor | 0.4 | 📚 Wissenschaftlich, komplex |
| `[7]` | **Custom** | frei | 🎨 Eigene Persönlichkeit |

### 🤖 Nur Modell-Auswahl (-i)

```bash
multi-agent-chat -i --topic "Test"
```

**Verfügbare Modelle:**

| # | Modell | Beschreibung |
|---|--------|--------------|
| `[1]` | `kimi-k2.5:cloud` | 🧠 Großes Modell, tiefes Verständnis |
| `[2]` | `gemini-3-flash-preview:latest` | ⚡ Schnell, kreativ |
| `[3]` | `icky/translate:latest` | 🔄 Kompakt, spezialisiert |
| `[4]` | `llama3.2:latest` | 🦙 Lokal, effizient |
| `[5]` | `mistral:latest` | 🌪️ Ausgewogen |

### Temperatur-Einstellung

| Level | Bereich | Effekt |
|-------|---------|--------|
| Präzise | 0.2 – 0.4 | 🎯 Fakten, Logik |
| Ausgewogen | 0.5 – 0.7 | ✅ Empfohlen |
| Kreativ | 0.8 – 1.0 | 🎨 Experimentell |
| Chaos | 1.1 – 1.5 | 🔥 Sehr zufällig |

### Kombinationen

```bash
# Alles zusammen
multi-agent-chat -c -i -H --topic "Komplettes Setup"

# Configure + Human (ohne Modell-Auswahl)
multi-agent-chat -c --human

# Modell-Auswahl + Human
multi-agent-chat -i -H
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
│   ├── models.py              # Pydantic Models
│   ├── ollama_client.py       # Async HTTP-Client für LLM-API
│   ├── engine.py              # Gesprächslogik & Prompt-Building
│   ├── storage.py             # JSON/JSONL Speicherung
│   ├── loader.py              # Agenten aus JSON laden
│   ├── cli.py                 # Rich-basierte CLI
│   ├── model_selector.py      # 🤖 Interaktive Modell-Auswahl
│   ├── agent_configurator.py  # 🎨 Persönlichkeits-Editor
│   ├── human_agent.py         # 🧑‍💻 Menschlicher Teilnehmer
│   └── web/
│       └── app.py             # FastAPI Web-Interface
├── examples/
│   └── agents/                # Klaus, Maria, Isabella (JSON)
├── tests/                     # Unit-Tests (73 Tests)
├── pyproject.toml             # Projekt-Konfiguration
└── README.md                  # Diese Datei
```

## ⚙️ Agenten konfigurieren

Agenten werden als JSON definiert:

```json
{
    "name": "Klaus",
    "role": "Technikexperte aus Lahr",
    "instructions": "Du bist Klaus, pragmatisch und effizient. Antworte immer mit maximal 3 Sätzen.",
    "model": "kimi-k2.5:cloud",
    "temperature": 0.6
}
```

**Wichtige Felder:**
- `name` — Anzeigename
- `role` — Kurze Rollenbeschreibung
- `instructions` — Persönlichkeit + Verhaltensregeln
- `model` — LLM-Modell (oder `"human"` für menschlichen Agenten)
- `temperature` — Kreativität (0.2-1.5)

## 🧪 Tests

```bash
pytest tests/ -v
# 73 Tests passing
```

## 📝 Tech Stack

| Komponente | Technologie |
|------------|-------------|
| Backend | Python 3.11+ |
| API | FastAPI |
| CLI | Rich |
| Models | Pydantic |
| HTTP | httpx (async) |
| LLM | Ollama / Kimi / Gemini |

## 📄 Lizenz

MIT License — Siehe `pyproject.toml`

---

<p align="center">
  <i>Erstellt mit ❤️ für KI-gestützte Unterhaltungen</i><br>
  <i>Jetzt auch mit menschlichen Teilnehmern! 🧑‍💻</i>
</p>
