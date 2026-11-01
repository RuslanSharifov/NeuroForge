"""User-approved GGUF download; no automatic installs without confirmation."""
import urllib.request
from pathlib import Path
from model_catalog import model_info, choose, catalog

def download(key):
    info=model_info(key)
    if info["installed"]:
        print("Model artıq mövcuddur:",info["title"])
        return True
    print("Model:",info["title"],"\nSource:",info["url"],"\nDestination:",info["path"])
    try:
        permission=input("Modeli yükləməyə icazə verirsən? [y/N]: ").strip().lower()
    except (EOFError,KeyboardInterrupt):return False
    if permission not in ("y","yes","b","bəli"):return False
    dest=Path(info["path"])
    dest.parent.mkdir(parents=True,exist_ok=True)
    partial=dest.with_suffix(".gguf.part")
    try:
        req=urllib.request.Request(info["url"],headers={"User-Agent":"NeuroForge/0.6"})
        with urllib.request.urlopen(req,timeout=45) as response,partial.open("wb") as output:
            total=0
            while True:
                chunk=response.read(262144)
                if not chunk:break
                output.write(chunk)
                total+=len(chunk)
                if total//10485760 != (total-len(chunk))//10485760:
                    print(f"Yükləndi: {total//1048576} MiB",flush=True)
        with partial.open("rb") as fp:valid=fp.read(4)==b"GGUF"
        if not valid or partial.stat().st_size<info["min_bytes"]:
            raise ValueError("GGUF faylı etibarlı deyil və ya natamamdır")
        partial.replace(dest)
        print("Model hazırdır:",dest)
        return True
    except Exception as exc:
        print("Yükləmə alınmadı:",exc)
        print("Yarımçıq fayl:",partial)
        return False

def menu():
    print("\nNeuroForge Model Manager")
    for info in catalog():
        print(f'{info["key"]}: {info["title"]} - {"READY" if info["installed"] else "MISSING"}')
    print("Model dəyişmək üçün adını yaz (chat/coder), çıxmaq üçün Enter.")
    key=input("Seçim > ").strip()
    if not key:return
    if key not in ("chat","coder"):print("Yanlış seçim");return
    info=model_info(key)
    if not info["installed"] and not download(key):return
    choose(key)
    print("Model seçildi:",info["title"])
    print("Vacib: köhnə llama-server hələ işləyirsə, onu dayandırıb TUI-ni yenidən aç.")

if __name__=="__main__":menu()
