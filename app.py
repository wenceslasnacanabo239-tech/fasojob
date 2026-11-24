from flask import Flask, request, redirect
import requests

app = Flask(__name__)

JOBS = []

HTML = """
<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>FasoJob - Emplois au Burkina</title>
<style>body{font-family:sans-serif;background:#f2f2f2;padding:15px} .card{background:white;padding:15px;border-radius:10px;margin:10px 0} .btn{background:#25D366;color:white;padding:10px 15px;border-radius:8px;text-decoration:none;display:inline-block} .top{background:#007bff;color:white;padding:20px;border-radius:10px;text-align:center}</style>
</head><body>
<div class="top"><h1>🇧🇫 FasoJob</h1><p>Emplois au Burkina Faso</p><a href="/ajouter" style="background:white;color:#007bff;padding:10px 15px;border-radius:8px;text-decoration:none">+ Ajouter une offre</a></div>
<p><b>{total} offres</b> | <a href="/robot">🔄 Actualiser avec le robot</a></p>
{jobs}
</body></html>
"""

@app.route("/")
def home():
    q = request.args.get("q","").lower()
    cards = ""
    for j in JOBS:
        if q and q not in (j.get("titre","") + j.get("ville","")).lower():
            continue
        wa = j.get("whatsapp","")
        btn = f'<a class="btn" href="https://wa.me/{wa}">Postuler WhatsApp</a>' if wa else f'<a class="btn" href="#">Voir annonce</a>'
        cards += f'<div class="card"><h3>{j.get("titre","")}</h3><p>📍 {j.get("ville","")} | 💰 {j.get("salaire","")}</p><p>{j.get("desc","")}</p><p><small>Source: {j.get("source","")}</small></p>{btn}</div>'
    if not cards:
        cards = "<div class='card'><p>Aucune offre pour le moment. Appuie sur Actualiser avec le robot.</p></div>"
    return HTML.format(total=len(JOBS), jobs=cards)

@app.route("/ajouter", methods=["GET","POST"])
def ajouter():
    if request.method == "POST":
        JOBS.append({
            "titre": request.form.get("titre",""),
            "ville": request.form.get("ville",""),
            "salaire": request.form.get("salaire",""),
            "whatsapp": request.form.get("whatsapp",""),
            "desc": request.form.get("desc",""),
            "source": "Manuel"
        })
        return redirect("/")
    return """
    <form method="post" style="font-family:sans-serif;padding:20px">
    <h2>Ajouter une offre</h2>
    Titre: <input name="titre" required><br><br>
    Ville: <input name="ville" required><br><br>
    Salaire: <input name="salaire"><br><br>
    WhatsApp: <input name="whatsapp" placeholder="226..."><br><br>
    Description:<br><textarea name="desc"></textarea><br><br>
    <button>Publier</button>
    </form>
    """

@app.route("/robot")
def robot():
    try:
        url = "https://api.reliefweb.int/v1/jobs?appname=fasojob&preset=latest&query[value]=Burkina Faso&limit=20&fields[include][]=title&fields[include][]=url&fields[include][]=location&fields[include][]=organization"
        r = requests.get(url, timeout=20)
        data = r.json()
        nouveaux = []
        for item in data.get("data", []):
            f = item.get("fields", {})
            titre = f.get("title", "Offre")
            ville = "Burkina Faso"
            loc = f.get("location", [])
            if loc:
                ville = loc[0].get("name", "Burkina Faso")
            lien = f.get("url", "")
            org = f.get("organization", [])
            org_nom = org[0].get("name", "") if org else ""
            nouveaux.append({
                "titre": titre,
                "ville": ville,
                "salaire": "Voir annonce",
                "whatsapp": "",
                "desc": (org_nom + " - Voir annonce : " + lien)[:500],
                "source": "ReliefWeb"
            })
    except Exception as e:
        nouveaux = []
    ajoutes = 0
    for job in nouveaux:
        existe = False
        for j in JOBS:
            if j.get("titre") == job.get("titre"):
                existe = True
                break
        if not existe:
            JOBS.append(job)
            ajoutes += 1
    if ajoutes == 0:
        return f"Aucune nouvelle vraie offre pour le moment. Total : {len(JOBS)} - <a href='/'>Retour</a>"
    return f"Robot OK ! {ajoutes} vraies offres ajoutees. Total : {len(JOBS)} - <a href='/'>Voir les offres</a>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)