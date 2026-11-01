"""NeuroForge adaptive terminal UI: Termux, CMD, PowerShell, Linux."""
import os
import shutil
import sys
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

def main():
    with db(): pass
    while True:
        header("Local AI")
        print("1  AI ilə söhbət\n2  Bilik öyrət\n3  Bilikləri göstər\n4  Bilik dəyiş / sil\n5  Geribildirim\n0  Çıxış")
        print("─"*width())
        choice=ask("Seçimin")
        if choice=="1": talk()
        elif choice=="2": teach()
        elif choice=="3": browse()
        elif choice=="4": manage()
        elif choice=="5": feedback()
        elif choice=="0": break
        else: print("Yanlış seçim");pause()

if __name__=="__main__": main()
