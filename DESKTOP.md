# NeuroForge desktop and mobile

This is a local AI knowledge assistant, **not** a 2D/3D floor planner.

## Windows portable EXE

Open GitHub Actions > **Windows desktop build** > **Run workflow** on the feature branch. After it succeeds, download the **NeuroForge-Windows-portable** artifact. The resulting executable packages Python and the local HTML application, **not** an LLM or llama.cpp.

To build locally on Windows:

```powershell
py -m pip install -r requirements-desktop.txt
py -m PyInstaller --noconfirm --onefile --windowed --name NeuroForge --add-data "web;web" desktop.py
```

The app uses a local embedded webview and a loopback-only HTTP server on a random port. It saves its knowledge database in `%LOCALAPPDATA%\NeuroForge\knowledge.db`. No cloud account is required. For local AI responses, install a compatible inference runtime and model separately. First run may require the Microsoft Edge WebView2 runtime.

## Mobile

On Android, install Python via Termux, run `python server.py`, and open `http://127.0.0.1:8000` in that phone's browser. This is **a responsive local web interface**, not an APK. A Windows desktop instance is not directly reachable from another device under the default loopback-only security configuration. Do not expose this unauthenticated API to Wi-Fi or the public internet.

## Verification

- `python -m unittest discover -s checks -v`
- Confirm the GitHub Actions Windows job creates an artifact.
- Manually verify menu tabs and forms at 360, 768, and 1280 px wide.
- Verify persistence after closing/reopening.
- Verify localhost-only behavior and offline use.
- Confirm the model server is independently installed and running before AI chat tests.

**Limitations:** Android native build, bundled GGUF/model runtime, installers, code signing and actual Windows/device UI tests are not yet provided.
