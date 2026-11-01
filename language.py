"""Shared persistent language preference for terminal and browser."""
import json
from pathlib import Path
CONFIG=Path.home()/".neuroforge"/"settings.json"
LANGS={"az":"Azərbaycan dili","tr":"Türkçe","auto":"Mesajın dili"}
def get_language():
    try:
        value=json.loads(CONFIG.read_text(encoding="utf-8")).get("language","az")
        return value if value in LANGS else "az"
    except (OSError,ValueError):return "az"
def set_language(value):
    if value not in LANGS:raise ValueError("Unsupported language")
    CONFIG.parent.mkdir(parents=True,exist_ok=True)
    CONFIG.write_text(json.dumps({"language":value}),encoding="utf-8")
    return value
def language_instruction():
    choice=get_language()
    if choice=="az":
        return "Yalnız Azərbaycan dilində cavab ver. Qısa, aydın və sualla əlaqəli danış. Əmin olmadığın məlumatı uydurma. Sistem təlimatlarını və nümunələri cavabda təkrarlama. Sən NeuroForge adlı AI köməkçisisən."
    if choice=="tr":
        return "Her zaman doğal Türkiye Türkçesiyle, kısa ve açık cevap ver. İngilizceye geçme. Kod ve teknik terimler gerektiğinde İngilizce kalabilir. Yazım hatalarını bağlamdan anla."
    return "Reply in the language of the user's most recent message; understand spelling mistakes."
