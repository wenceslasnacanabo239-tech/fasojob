from flask import Flask, render_template_string, request, redirect
import requests, threading, time
from bs4 import BeautifulSoup

app = Flask(__name__)
jobs = []
last_update = "Jamais"

HTML = """
<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>FasoJob - Robot Emploi Burkina</title>
<style>body{font-family:Arial;margin:0;background:#f4f4f4}header{background:#008751;color:white;padding:20px;text-align:center}.container{max-width:800px;margin:20px auto;padding:0 15px}.card{background:white;padding:15px;border-radius:10px;margin-bottom:12px}.btn{background:#008751;color:white;padding:10px 15px;border:none;border-radius:5px}input,textarea{width:100%;padding:10px;margin:5px 0;border:1px solid #ddd;border-radius:5px;box-sizing:border-box}.badge{background:#ffcc00;padding:3px 8px;border-radius:10px;font-size:12px}.robot{background:#e6ffe6;border:1px solid green}</style>
</head><body><header><h1>🇧🇫 FasoJob - Robot</h1><p>Offres réelles du Burkina, mises à jour auto</p></header>
<div class="container">
<div class="card robot">🤖 Robot actif - Dernière mise à jour : {{ last_update }} - {{ jobs|length }} offres trouvées</div>
<div class="card"><h3>Publier une offre</h3><form method="post" action="/add"><input name="titre" placeholder="Titre" required><input name="entreprise" placeholder="Entreprise" required><input name="lieu" placeholder="Lieu" required><textarea name="desc" placeholder="Description"></textarea><button class="btn" type="submit">Publier</button></form></div>
<h2>Offres du jour</h2>
{% for j in jobs %}<div class="card"><span class="badge">{{ j.source }}</span> <b>{{ j.titre }}</b><br>{{ j.entreprise }} - {{ j.lieu }}<br>{{ j.desc }}<br>{% if j.link %}<a href="{{ j.link }}" target="_blank">Voir l'offre →</a>{% endif %}</div>
{% else %}<div class="card">Robot en train de chercher... Actualise dans 1 min.</div>{% endfor %}
</div></body></html>
"""

def scrape():
    global jobs, last_update
    found = []
    # Site 1 : Emploi Burkina
    try:
        r = requests.get("https://www.emploi.bf", timeout=15, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True)[:30]:
            t = a.get_text(strip=True)
            if len(t) > 15 and any(k in t.lower() for k in ["chauffeur","comptable","commercial","secretaire","technicien","agent","vendeur","caissier","informaticien","gestion"]):
                link = a["href"]
                if not link.startswith("http"): link = "https://www.emploi.bf" + link
                found.append({"titre": t, "entreprise": "Voir offre", "lieu": "Burkina Faso", "desc": "Offre trouvée par le robot FasoJob", "source": "Emploi.bf", "link": link})
    except Exception as e:
        print("Erreur emploi.bf:", e)
    # Site 2 : JobaBurkina / FasoJobs - recherche générale
    try:
        r = requests.get("https://burkinafaso.jobinrwanda.com", timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True)[:20]:
            t = a.get_text(strip=True)
            if len(t) > 20:
                found.append({"titre": t[:80], "entreprise": "Offre Internationale", "lieu": "Burkina Faso", "desc": "Offre trouvée par le robot", "source": "Robot", "link": a["href"] if a["href"].startswith("http") else ""})
    except: pass
    if found:
        jobs = found[:25]
        last_update = time.strftime("%d/%m %H:%M")
    if not jobs:
        jobs = [
            {"titre":"Chauffeur Livraison","entreprise":"Burkina Logistics","lieu":"Ouagadougou","desc":"Permis B/C requis","source":"FasoJob","link":""},
            {"titre":"Agent Commercial","entreprise":"Orange Burkina","lieu":"Bobo-Dioulasso","desc":"Vente et prospection","source":"FasoJob","link":""},
            {"titre":"Secrétaire Comptable","entreprise":"ONG Sahel","lieu":"Ouagadougou","desc":"Bac+2 requis","source":"FasoJob","link":""},
        ]
        last_update = time.strftime("%d/%m %H:%M") + " (secours)"

def robot_loop():
    while True:
        scrape()
        time.sleep(3600) # 1 heure

threading.Thread(target=robot_loop, daemon=True).start()
scrape()

@app.route("/")
def home(): return render_template_string(HTML, jobs=jobs, last_update=last_update)
@app.route("/add", methods=["POST"])
def add():
    jobs.insert(0, {"titre": request.form.get("titre"), "entreprise": request.form.get("entreprise"), "lieu": request.form.get("lieu"), "desc": request.form.get("desc"), "source":"Manuel", "link":""})
    return redirect("/")
@app.route("/health")
def health(): return "OK"

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))