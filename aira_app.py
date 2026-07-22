import os
import sqlite3
import datetime
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

# Pypdf modulunu hələlik deaktiv etdik ki, fayl yoxdursa çökməsin
# VERİLƏNLƏR BAZASI AYARLARI
db = sqlite3.connect("aira.db")
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS profile(key TEXT PRIMARY KEY, value TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS yaddaş(id INTEGER PRIMARY KEY AUTOINCREMENT, sual TEXT, cavab TEXT)")

cursor.execute("INSERT OR REPLACE INTO profile VALUES (?, ?)", ("Qurucu / Creator", "Sadiq"))
db.commit()

API_KEY = "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"
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=API_KEY)

def yadda_saxla(sual, cavab):
    cursor.execute("INSERT INTO yaddaş(sual, cavab) VALUES (?, ?)", (sual, cavab))
    db.commit()

def yadda_oxu():
    cursor.execute("SELECT sual, cavab FROM yaddaş ORDER BY id DESC LIMIT 5")
    return cursor.fetchall()

def profil_oxu():
    cursor.execute("SELECT key, value FROM profile")
    data = cursor.fetchall()
    if not data: return "İstifadəçi haqqında məlumat yoxdur."
    return "\n".join(f"{k}: {v}" for k, v in data)

def saat_yoxla(sual):
    s = sual.lower()
    if any(x in s for x in ["saat neçədir", "saat kaç", "what time is it"]):
        return datetime.datetime.now().strftime("%H:%M")
    if any(x in s for x in ["tarix neçədir", "tarih nedir", "what is the date"]):
        return datetime.datetime.now().strftime("%d.%m.%Y")
    return None

def internetde_axtar(sorgu):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        url = f"https://html.duckduckgo.com/html/?q={sorgu}"
        cavab = requests.get(url, headers=headers)
        if cavab.status_code != 200: return ""
        soup = BeautifulSoup(cavab.text, 'html.parser')
        neticeler = [n.text.strip() for n in soup.find_all('a', class_='result__snippet')[:2]]
        return "\n".join(neticeler)
    except:
        return ""

def aira_cavab_ver(sual):
    s = sual.lower()

    if any(x in s for x in ["mənim adım", "benim adım", "my name is"]):
        ad = sual.replace("Mənim adım", "").replace("mənim adım", "").replace("Benim adım", "").replace("benim adım", "").replace("My name is", "").replace("my name is", "").strip()
        cursor.execute("INSERT OR REPLACE INTO profile VALUES (?, ?)", ("Ad/Name", ad))
        db.commit()
        return "Adını yadda saxladım! 👍"

    vaxt = saat_yoxla(sual)
    if vaxt:
        return f"Saat/Tarix: {vaxt}"

    yaddaş_data = yadda_oxu()
    profil_data = profil_oxu()
    
    internet_data = ""
    if any(x in s for x in ["axtar", "google", "internet", "tap", "ara"]):
        təmiz_sorgu = sual.replace("axtar", "").replace("Google-da", "").replace("internetdə", "").replace("ara", "").strip()
        internet_data = internetde_axtar(təmiz_sorgu)

    try:
        cavab = client.chat.completions.create(
            model="google/gemini-2.5-flash",
            max_tokens=300,
            messages=[
                {
                    "role": "system",
                    "content": f"Sən Aira adlı AI köməkçisən. Azərbaycan, Türk və İngilis dillərində qısa cavab ver. Sənin qurucun Sadiqdir.\n\nİstifadəçi: {profil_data}\nYaddaş: {yaddaş_data}\nİnternet: {internet_data}"
                },
                {"role": "user", "content": sual}
            ]
        )
        netice = cavab.choices[0].message.content
        yadda_saxla(sual, netice)
        return netice
    except:
        return "Bağlantı xətası baş verdi."
