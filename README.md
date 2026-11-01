# NeuroForge

Local-first AI knowledge engine with a mobile-friendly browser dashboard and adaptive terminal UI for **Android Termux, Windows CMD / PowerShell, Linux and macOS**.

> **MVP limitation:** NeuroForge currently stores and retrieves taught Q&A/rules using lexical matching. It is **not yet** a pretrained or self-trained LLM. The Gemini and Ollama adapters and neural training are planned, not implemented.

## Requirements

- Python 3.10 or newer
- No third-party Python dependencies for the TUI and built-in web server; no external AI API keys
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
python server.py
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
python server.py
```

Open **http://127.0.0.1:8000**. For optional FastAPI docs on desktop, install `requirements-web.txt` and start `python -m uvicorn main:app --host 127.0.0.1 --port 8000` instead.

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

Run the stdlib core tests using `python -m unittest discover -s checks -v`. Optional FastAPI tests require `python -m pip install -r requirements-web.txt`.

## Security

**Do not expose this version publicly.** It has no user authentication or access control. Bind to `127.0.0.1`, do not forward the port, and do not put API keys or secrets into knowledge records. Add auth and secure secrets storage before remote deployments. The database file is git-ignored.

## Roadmap

1. Provider adapters: optional local Ollama and Gemini API
2. Local semantic embeddings and relevance scoring
3. Provenance, contradictions, evaluations, stronger feedback loop
4. Small PyTorch neural experiments, controlled training
5. Sandboxed code agent and permissions, authentication for remote web use

## Termux Python 3.13 fix (pydantic-core build failed)

The default `python tui.py` and `python server.py` use only Python's standard library. You do **not** need Rust, maturin, FastAPI or Pydantic. Update your clone using `git pull --ff-only` then launch either command. The optional FastAPI stack is isolated in `requirements-web.txt` for environments where Pydantic wheels are available.

For Termux, keep the repository in Termux home (`~/NeuroForge`) where possible; Android shared storage can have executable/symlink limitations.
