"""Local GGUF model catalog and user-approved model switching."""
import json
from pathlib import Path

CONFIG=Path.home()/".neuroforge"/"models.json"
MODELS={
 "coder":{"title":"Qwen2.5 Coder 1.5B Q4","filename":"qwen-coder.gguf","alias":"qwen2.5-coder:1.5b","url":"https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF/resolve/main/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf","min_bytes":500000000},
 "chat":{"title":"Qwen3 1.7B Q4_K_M","filename":"qwen3-chat.gguf","alias":"qwen3:1.7b","url":"https://huggingface.co/tensorblock/Qwen_Qwen3-1.7B-GGUF/resolve/main/Qwen3-1.7B-Q4_K_M.gguf","min_bytes":800000000}
}
def selected():
    try:
        value=json.loads(CONFIG.read_text(encoding="utf-8")).get("selected","coder")
        return value if value in MODELS else "coder"
    except (OSError, ValueError):
        return "coder"
def choose(value):
    if value not in MODELS:raise ValueError("Unknown model")
    CONFIG.parent.mkdir(parents=True,exist_ok=True)
    CONFIG.write_text(json.dumps({"selected":value}),encoding="utf-8")
    return value
def model_info(key=None):
    key=key or selected()
    data=dict(MODELS[key])
    data["key"]=key
    data["path"]=str(Path.home()/"models"/data["filename"])
    path=Path(data["path"])
    try:
        with path.open("rb") as fh:valid=fh.read(4)==b"GGUF" and path.stat().st_size>=data["min_bytes"]
    except OSError:valid=False
    data["installed"]=valid
    return data
def catalog():
    return [model_info(k) for k in MODELS]
