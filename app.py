from flask import Flask, render_template_string, request, redirect
import requests, threading, time
from bs4 import BeautifulSoup

app = Flask(__name__)
jobs = []
last_update = "Jamais"

LISTE = """
<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>FasoJob - Emploi Burkina</title>
<style>body{font-family:Arial;margin:0;background:#f4f4f4}header{background:#008751;color:white;padding:20px;text-align:center}.container{max-width:800px;margin:20px auto;padding:0 15px}.card{background:white;padding:15px;border-radius:10px;margin-bottom:12px}.btn{background:#008751;color:white;padding:10px 15px;border:none;border-radius:5px}input,textarea{width:100%;padding:10px;margin:5px 0;border:1px solid #ddd;border-radius:5px;box-sizing:border-box}.badge{background:#ffcc00;padding:3px 8px;border-radius:10px;font-size:12px}.robot{background:#e6ffe6;border:1px solid green}.voir{background:#008751;color:white;padding:12px;display:block;text-align:center;text-decoration:none;border-radius:8px;font-weight:bold;margin-top:10px}</style>
</head><body><header><h1>🇧🇫 FasoJob</h1><p>Les offres d'emploi au Burkina</p></header>
<div class="container">
<div class="card robot">🤖 Robot actif - {{ last_update }} - {{ jobs|length }} offres</div>
<div class="card"><h3>Publier une offre</h3><form method="post" action="/add"><input name="titre" placeholder="Titre" required><input name="entreprise" placeholder="Entreprise" required><input name="lieu" placeholder="Lieu" required><textarea name="desc" placeholder="Description complète..."></textarea><button class="btn" type="submit">Publier</button></form></div>
<h2>Offres du jour</h2>
{% for j in jobs %}
<div class="card"><span class="badge">{{ j.source }}</span> <b>{{ j.titre }}</b><br>{{ j.entreprise }} - {{ j.lieu }}<br>{{ j.desc[:120] }}...
<a class="voir" href="/offre/{{ loop.index0 }}">👁️ Voir l'offre</a></div>
{% endfor %}
</div></body></html>
"""

DETAIL = """
<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ j.titre }} - FasoJob</title>
<style>body{font-family:Arial;margin:0;background:#f4f4f4}header{background:#008751;color:white;padding:20px;text-align:center}.container{max-width:800px;margin:20px auto;padding:0 15px}.card{background:white;padding:20px;border-radius:10px}.back{color:#008751;text-decoration:none;font-weight:bold}.badge{background:#ffcc00;padding:5px 10px;border-radius:10px}.info{background:#f9f9f9;padding:15px;border-radius:8px;margin:15px 0}.btn{display:block;background:#008751;color:white;padding:15px;text-align:center;text-decoration:none;border-radius:8px;font-weight:bold;margin-top:15px}</style>
</head><body><header><h1>🇧🇫 FasoJob</h1></header>
<div class="container"><a class="back" href="/">← Retour aux offres</a><br><br>
<div class="card">
<span class="badge">{{ j.source }}</span>
<h1>{{ j.titre }}</h1>
<div class="info">
<b>🏢 Entreprise :</b> {{ j.entreprise }}<br><br>
<b>📍 Lieu :</b> {{ j.lieu }}<br><br>
<b>📅 Publié :</b> Aujourd'hui<br><br>
<b>📝 Type :</b> Temps plein
</div>
<h3>Description complète</h3>
<p style="line-height:1.7;font-size:16px">{{ j.desc }}</p>
<h3>Profil recherché</h3>
<p style="line-height:1.7">Motivé(e), sérieux(se), disponible rapidement. Expérience bienvenue mais débutant accepté selon le poste.</p>
<h3>Comment postuler ?</h3>
<p>Contacte directement l'entreprise en mentionnant <b>FasoJob</b> et le titre du poste.</p>
{% if j.link %}<a class="btn" href="{{ j.link }}" target="_blank">🔗 Voir l'offre originale sur le site source</a>{% endif %}
<a class="btn" style="background:#333" href="/">← Voir les autres offres</a>
</div></div></body></html>
"""

def scrape():
    global jobs, last_update
    found=[]
    try:
        r=requests.get("https://www.emploi.bf",timeout=15,headers={"User-Agent":"Mozilla/5.0"})
        soup=BeautifulSoup(r.text,"html.parser")
        for a in soup.find_all("a",href=True)[:30]:
            t=a.get_text(strip=True)
            if len(t)>15 and any(k in t.lower() for k in ["chauffeur","comptable","commercial","secretaire","technicien","agent","vendeur","caissier","informaticien","gestion"]):
                link=a["href"]
                if not link.startswith("http"): link="https://www.emploi.bf"+link
                found.append({"titre":t,"entreprise":"Voir offre","lieu":"Burkina Faso","desc":"Offre trouvée par le robot FasoJob sur Emploi.bf. Clique sur 'Voir l'offre originale' en bas pour voir tous les détails, le salaire et comment postuler sur le site officiel.","source":"Emploi.bf","link":link})
    except Exception as e: print(e)
    if found:
        jobs=found[:25]; last_update=time.strftime("%d/%m %H:%M")
    if not jobs:
        jobs=[
            {"titre":"Chauffeur Livraison","entreprise":"Burkina Logistics","lieu":"Ouagadougou","desc":"Nous recherchons un chauffeur livraison sérieux. Permis B/C obligatoire. Expérience de 2 ans souhaitée. Mission : livrer les colis à Ouagadougou et environs. Salaire à discuter selon expérience. Disponible immédiatement.","source":"FasoJob","link":""},
            {"titre":"Agent Commercial","entreprise":"Orange Burkina","lieu":"Bobo-Dioulasso","desc":"Nous recherchons un agent commercial dynamique pour la vente de nos produits. Prospection terrain, accueil clients, suivi des ventes. Profil : bon relationnel, aime le terrain, débutant accepté.","source":"FasoJob","link":""},
            {"titre":"Secrétaire Comptable","entreprise":"ONG Sahel","lieu":"Ouagadougou","desc":"Secrétaire comptable pour ONG. Saisie comptable, classement, accueil, gestion courrier. Profil : Bac+2 en comptabilité ou secrétariat, maîtrise Word/Excel.","source":"FasoJob","link":""},
        ]
        last_update=time.strftime("%d/%m %H:%M")+" (secours)"

def loop():
    while True:
        scrape(); time.sleep(3600)
threading.Thread(target=loop,daemon=True).start()
scrape()

@app.route("/")
def home(): return render_template_string(LISTE,jobs=jobs,last_update=last_update)
@app.route("/offre/<int:id>")
def offre(id):
    if id < 0 or id >= len(jobs): return redirect("/")
    return render_template_string(DETAIL,j=jobs[id])
@app.route("/add",methods=["POST"])
def add():
    jobs.insert(0,{"titre":request.form.get("titre"),"entreprise":request.form.get("entreprise"),"lieu":request.form.get("lieu"),"desc":request.form.get("desc"),"source":"Manuel","link":""})
    return redirect("/")
@app.route("/health")
def health(): return "OK"
if __name__=="__main__":
    import os; app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))