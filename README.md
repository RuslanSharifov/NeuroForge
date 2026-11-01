# NeuroForge

Local-first AI knowledge engine with a mobile-friendly browser dashboard and adaptive terminal UI for **Android Termux, Windows CMD / PowerShell, Linux and macOS**.

> **MVP limitation:** NeuroForge currently stores and retrieves taught Q&A/rules using lexical matching. It is **not yet** a pretrained or self-trained LLM. The Gemini and Ollama adapters and neural training are planned, not implemented.

## Requirements

- Python 3.10 or newer
- No external AI API keys
- SQLite (bundled with Python)

## Android Termux

Install Termux from F-Droid, then:

```bash
pkg update
pkg install python git -y
git clone https://github.com/RuslanSharifov/NeuroForge.git
cd NeuroForge
python -m pip install -r requirements.txt
python tui.py
```

To launch the web panel instead:

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000** in your Android browser.

## Windows CMD

```bat
git clone https://github.com/RuslanSharifov/NeuroForge.git
cd NeuroForge
py -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python tui.py
```

For PowerShell, activate with `.venv\Scripts\Activate.ps1` (subject to local execution policy).

Start the web panel in place of the terminal UI with:

```bat
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000**. API docs: **http://127.0.0.1:8000/docs**.

## Linux / macOS

```bash
git clone https://github.com/RuslanSharifov/NeuroForge.git
cd NeuroForge
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python tui.py
```

## Features

- Q&A/rules knowledge creation, reading, editing and deletion
- Enable/disable knowledge entries
- Change history
- Lexical retrieval chat with source ID and confidence
- Feedback proposals and manual approval to become knowledge
- Adaptive text menus that fit narrow Termux displays
- Responsive browser interface working against the same SQLite file

## API

| Method | Route | Purpose |
|---|---|---|
| GET | `/health` | Health |
| GET, POST | `/knowledge` | List/create knowledge |
| GET, PATCH, DELETE | `/knowledge/{id}` | Manage knowledge |
| GET | `/knowledge/{id}/history` | Edit history |
| POST | `/chat` | Ask knowledge engine |
| GET, POST | `/feedback` | Feedback |
| POST | `/feedback/{id}/approve` | Approve learning |

Run tests with `python -m pytest -q`.

## Security

**Do not expose this version publicly.** It has no user authentication or access control. Bind to `127.0.0.1`, do not forward the port, and do not put API keys or secrets into knowledge records. Add auth and secure secrets storage before remote deployments. The database file is git-ignored.

## Roadmap

1. Provider adapters: optional local Ollama and Gemini API
2. Local semantic embeddings and relevance scoring
3. Provenance, contradictions, evaluations, stronger feedback loop
4. Small PyTorch neural experiments, controlled training
5. Sandboxed code agent and permissions, authentication for remote web use
