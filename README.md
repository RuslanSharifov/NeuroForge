# NeuroForge

Local-first AI knowledge engine with a mobile-friendly browser dashboard and adaptive terminal UI for **Android Termux, Windows CMD / PowerShell, Linux and macOS**.

> **Important:** The default Q&A mode still uses lexical matching. The new **optional local LLM chat** uses an externally installed Ollama-compatible local model to understand natural language, typos and code questions. It preserves conversation history and incorporates approved knowledge. It does **not** train neural weights autonomously. The Gemini adapter, automatic self-training and repository code-editing agent are not implemented.

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

## Conversational AI + local model (optional)

The new terminal menu item **6 — Lokal LLM söhbəti** and web chat path `/agent/chat` use an Ollama-compatible local server. You must install/run a compatible model separately. This feature has **no paid API requirement**, but models consume storage and RAM. Running a local LLM directly on Android Termux depends on device hardware and availability of a compatible runtime; don't assume desktop Ollama instructions work unmodified on Android.

Desktop example, after installing Ollama:
```bash
ollama pull qwen2.5-coder:1.5b
ollama serve
```
In a second terminal:
```bash
python tui.py
# or
python server.py
```

Model selection by environment variable:
```bash
export NEUROFORGE_MODEL=qwen2.5-coder:1.5b
export NEUROFORGE_LLM_URL=http://127.0.0.1:11434/api/chat
```

For Android Termux, use a working **local Ollama-compatible inference server** (if your device supports it) and point `NEUROFORGE_LLM_URL` to it. If no model server is running, legacy knowledge CRUD still works; conversational mode shows a connection error. Never expose the unauthenticated app to the internet.

## GitHub skill reading (not executable plugins)

Menu item **7 — GitHub skill-lər** and web Skill panel accept **direct GitHub markdown file links**, e.g. `https://github.com/owner/repo/blob/main/skills/example/SKILL.md`. Each import is initially **disabled** and must be enabled manually. Imported text supplies extra context for the local LLM. It cannot automatically install packages, run arbitrary scripts, edit repository files, or make model weights learn. Review imported content; treat it as untrusted.

## Roadmap to genuine autonomous improvement

- Retrieval and inference: local LLM + semantic memory
- Code tools: read workspace files, inspect DOM/HTML, generate patches, run sandboxed tests, seek approval before commits
- Learning pipeline: log outcomes, propose distilled lessons, validate with tests and human approval
- Optional periodic LoRA fine-tuning when hardware permits, with evaluation and rollback
- Trust controls for skills: source review, explicit permissions, tool sandbox and secrets isolation

## v0.4 natural-language coding agent (experimental)

The chat now calls a local model with tools. You can say things like: "login səhifəsini tap, div əvəzinə header istifadə etmək üçün dəyişiklik təklif et". The model can **list files, search text, read workspace files and propose a full-file patch**. Changes are **never applied automatically**: confirm the diff in TUI or Web. The agent can still have ordinary conversations and retain recent history. This is not autonomous model-weight training.

Set a project as the workspace BEFORE launching NeuroForge:
```bash
export NEUROFORGE_WORKSPACE="$HOME/my-project"
python tui.py
```
On Windows CMD:
```bat
set NEUROFORGE_WORKSPACE=C:\\Users\\YourUser\\Projects\\my-project
python tui.py
```
Or launch `python server.py` for a browser UI. The LLM must be running at `NEUROFORGE_LLM_URL` (defaults to an Ollama-compatible endpoint at 127.0.0.1:11434) with `NEUROFORGE_MODEL` installed. Desktop example: `ollama pull qwen2.5-coder:1.5b`. On Android, set up an Android-compatible local inference server separately; there is no bundled Android model.

The agent cannot run shell commands, automatically install packages, discover arbitrary private GitHub repositories or edit outside the configured workspace. GitHub SKILL.md imports are **reference documents**, not executable code. Advanced long-term learning, safe command execution, and autonomous model training remain future work.

**SECURITY:** Browser app is not authenticated; keep it bound to 127.0.0.1, never expose it on a public address. Do not use the workspace containing secrets. Review each proposed edit carefully; model suggestions can be incorrect. The built-in edit endpoint is not safe for untrusted network clients.

## Public-user guided installation (v0.5)

The TUI and the standard-library web server still have **no pip dependencies**. Termux users can run:

```bash
git clone https://github.com/RuslanSharifov/NeuroForge.git
cd NeuroForge
python setup.py
python doctor.py --check-updates
python tui.py
```

- `python setup.py`: checks Python, `llama-server`, and the GGUF model, asks permission separately before installing packages and downloading the model. It does not automatically execute commands without consent, and doesn't reinstall items that are detected.
- `python doctor.py`: inspection only, no changes.
- `python doctor.py --install`: offers to repair missing Termux dependencies / model.
- TUI menu **8 — Versiya və qurulum**: checks status, compares published project version, offers missing components. Updates are *suggested*, not silently installed.
- `python server.py`: starts the local browser UI.

Run the local inference server in a separate terminal after setup:

```bash
llama-server -m "$HOME/models/qwen-coder.gguf" --alias qwen2.5-coder:1.5b --host 127.0.0.1 --port 8080 -c 2048 -np 1 -t 4
```

The default agent endpoint is `http://127.0.0.1:8080/v1/chat/completions`. If you use Ollama instead, configure `NEUROFORGE_LLM_URL` and `NEUROFORGE_MODEL` to match its server and model.

Windows/Linux/macOS users must install a compatible local inference server separately. The guided installer does not silently use a third-party desktop package manager. No OS-level visibility changes are made to repositories. If distributing this project publicly, enable GitHub repository visibility manually and review LICENSE, credentials, test results and open-network security first.

## v0.5.1: automatic local inference server startup

After `python setup.py` has installed `llama-server` and a GGUF file, starting terminal menu **6 — AI Agent**, or sending a request to the web `/agent/run` endpoint, automatically starts the local llama.cpp server on `127.0.0.1:8080` if it is not already listening. Startup can take several seconds. Errors and logs: `~/models/neuroforge-llama.log`. Model download / package installation never occurs through this action without asking first via `setup.py`. When a custom endpoint is configured, start your own server. For Termux, Android may stop the model server under memory pressure.

## Language and response speed

Terminal menu **9 — Cavab dili** chooses Azerbaijani (default), Turkish or automatic language detection. Preference persists in `~/.neuroforge/settings.json` and applies to both TUI and browser chats. It is a language instruction, not a guarantee: very small code-focused models may still answer in English or misunderstand Azerbaijani.

Simple conversations now omit the workspace tool schema to reduce processing latency. Code/repository requests still use tool calling. The model server remains CPU-bound on Termux and may answer slowly; response length is limited to reduce delay. Empty Enter in agent conversation is ignored.
