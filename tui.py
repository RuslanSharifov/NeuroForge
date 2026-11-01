"""NeuroForge adaptive terminal UI: Termux, CMD, PowerShell, Linux."""
import os
import shutil
import sys
from providers import menu as provider_menu, provider
from models import menu as models_menu
from language import get_language,set_language,LANGS
from model_server import ensure_local_llm
from doctor import describe, check_update, install_server, download_model, VERSION
from agent_runtime import agent_run, pending_edits, decide_edit
from agent import respond, import_github_skill, import_github_repo, skills, set_skill_active
from core import db, chat, list_knowledge, create_knowledge, patch_knowledge, delete_knowledge, list_feedback, create_feedback, approve_feedback, KnowledgeIn, KnowledgePatch, ChatIn, FeedbackIn

def width():
    return max(32, min(shutil.get_terminal_size(fallback=(76,24)).columns, 96))

def crop(value, limit):
    value = str(value).replace("\n", " ")
    return value if len(value)<=limit else value[:max(0,limit-1)]+"…"

def header(name):
    if sys.stdout.isatty():
        os.system("cls" if os.name=="nt" else "clear")
    print(" NEUROFORGE / "+name)
    print("─"*width())

def ask(label, optional=False):
    while True:
        try: value=input(label+" > ").strip()
        except (EOFError,KeyboardInterrupt): raise SystemExit(0)
        if value or optional: return value
        print("Bu sahə boş ola bilməz.")

def pause():
    ask("Davam üçün Enter", True)

def talk():
    header("Söhbət")
    print("Geri dönmək üçün /exit yazın.")
    while True:
        message=ask("Sən")
        if message.lower() in ("/exit","geri","/quit"): return
        result=chat(ChatIn(message=message))
        print("AI:",result["answer"])
        print("Mənbə:",result["source_id"],"| Uyğunluq:",result["confidence"])

def teach():
    header("Bilik öyrət")
    question=ask("Sual")
    answer=ask("Cavab")
    category=ask("Kateqoriya (boş=general)",True) or "general"
    item=create_knowledge(KnowledgeIn(question=question,answer=answer,category=category))
    print("Yadda saxlandı: #"+str(item["id"]))
    pause()

def browse():
    header("Bilik siyahısı")
    rows=list_knowledge()
    compact=width()<58
    for row in rows:
        if compact:
            print(f'#{row["id"]} [{"ON" if row["enabled"] else "OFF"}] {crop(row["question"],width()-14)}')
            print("  "+crop(row["answer"],width()-4))
        else:
            print(f'#{row["id"]:<4} {crop(row["category"],12):<12} {crop(row["question"],width()-24)}')
            print("   "+crop(row["answer"],width()-5))
    if not rows: print("Hələ bilik yoxdur.")
    pause()

def manage():
    header("Bilik redaktəsi")
    try: ident=int(ask("Bilik ID"))
    except ValueError: print("Yanlış ID"); pause(); return
    row=next((x for x in list_knowledge() if x["id"]==ident),None)
    if not row: print("Bilik tapılmadı");pause();return
    print(crop(row["question"],width()-2))
    print("1 Yenilə  2 Aktiv/deaktiv  3 Sil  0 Geri")
    choice=ask("Seçim")
    if choice=="1":
        q=ask("Yeni sual (boş=saxla)",True)
        a=ask("Yeni cavab (boş=saxla)",True)
        changes={}
        if q: changes["question"]=q
        if a: changes["answer"]=a
        patch_knowledge(ident, KnowledgePatch(**changes))
        print("Yeniləndi")
    elif choice=="2":
        patch_knowledge(ident,KnowledgePatch(enabled=not bool(row["enabled"])))
        print("Status dəyişdi")
    elif choice=="3" and ask("Silmək üçün DELETE yaz")=="DELETE":
        delete_knowledge(ident)
        print("Silindi")
    pause()

def feedback():
    header("Geribildirim")
    print("1 Düzəliş təklif et  2 Təsdiqlə")
    choice=ask("Seçim")
    if choice=="1":
        result=create_feedback(FeedbackIn(prompt=ask("Sual"),suggested_answer=ask("Düzgün cavab")))
        print("Gözləyən düzəliş:",result["feedback_id"])
    elif choice=="2":
        rows=[r for r in list_feedback() if not r["approved"]]
        for row in rows: print(f'#{row["id"]}: {crop(row["prompt"],22)} -> {crop(row["suggested_answer"],22)}')
        if rows:
            try:
                ident=int(ask("Təsdiq ID (0=geri)"))
                if ident in [r["id"] for r in rows]: approve_feedback(ident);print("Təsdiqləndi")
            except ValueError: print("Yanlış ID")
        else: print("Gözləyən düzəliş yoxdur")
    pause()

def agent_talk():
    header("Lokal LLM söhbəti")
    status=ensure_local_llm() if provider()=="local" else {"ready":True}
    if not status["ready"]:
        print(status.get("error","Model server hazır deyil"))
        pause()
        return
    print("Geri dönmək üçün /exit yaz.")
    while True:
        message=ask("Sən",True)
        if not message:continue
        if message.lower() in ("/exit","/quit"): return
        try:
            result=agent_run(message)
            print("AI:",result["answer"])
        except Exception as exc:
            print("LLM xətası:",exc)

def skill_menu():
    header("GitHub bacarıqları")
    print("1 Markdown skill URL import et  2 Skill-lərə bax/aktivləşdir")
    ch=ask("Seçim")
    if ch=="1":
        try:
            url=ask("GitHub repo və ya SKILL.md URL")
            print(import_github_skill(url) if "/blob/" in url else import_github_repo(url))
            print("Yeni skill deaktivdir; yoxladıqdan sonra aktivləşdir.")
        except Exception as exc:print("Import xətası:",exc)
    elif ch=="2":
        rows=skills()
        for r in rows:print(f'#{r["id"]} [{"ON" if r["active"] else "OFF"}] {crop(r["name"],25)}')
        if rows:
            try:
                ident=int(ask("Skill ID (0=geri)"))
                if ident in [r["id"] for r in rows]:
                    active=ask("Aktivləşsin? (h/y)").lower()=="h"
                    print(set_skill_active(ident,active))
            except (ValueError,TypeError) as exc:print(exc)
    pause()

def maintenance():
    header("Version / Setup")
    info=describe()
    print("Version:",VERSION)
    print("llama-server:", "OK" if info["llama_server"] else "NOT INSTALLED")
    print("Model:", "OK" if info["model_ready"] else "MISSING")
    print("Python:",info["python"])
    print("1  Check GitHub version")
    print("2  Offer to install missing components")
    choice=ask("Seçim")
    if choice=="1":
        print(check_update())
        print("To review changes, run git fetch origin main and git log HEAD..origin/main")
        print("After reviewing, update with git pull --ff-only origin main")
    elif choice=="2":
        if not info["llama_server"]:install_server()
        if not info["model_ready"]:download_model()
    pause()

def language_menu():
    header("Cavab dili")
    print("Hazırda:",LANGS[get_language()])
    print("1 Azərbaycan dili  2 Türkçe  3 Avtomatik")
    choice=ask("Seçim")
    choice={"1":"az","2":"tr","3":"auto"}.get(choice)
    if choice: print("Seçildi:",LANGS[set_language(choice)])
    pause()

def main():
    with db(): pass
    while True:
        header("Local AI")
        print("1  AI ilə söhbət\n2  Bilik öyrət\n3  Bilikləri göstər\n4  Bilik dəyiş / sil\n5  Geribildirim\n6  AI Agent (söhbət + kod alətləri)\n7  GitHub skill-lər\n8  Versiya və qurulum\n9  Cavab dili\n10 Model meneceri\n11 AI provayderi / Gemini\n0  Çıxış")
        print("─"*width())
        choice=ask("Seçimin")
        if choice=="1": talk()
        elif choice=="2": teach()
        elif choice=="3": browse()
        elif choice=="4": manage()
        elif choice=="5": feedback()
        elif choice=="6": agent_talk()
        elif choice=="7": skill_menu()
        elif choice=="8": maintenance()
        elif choice=="9": language_menu()
        elif choice=="10": models_menu()
        elif choice=="11": provider_menu()
        elif choice=="0": break
        else: print("Yanlış seçim");pause()

if __name__=="__main__": main()
