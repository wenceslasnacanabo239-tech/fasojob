from flask import Flask, request, redirect, render_template_string
app = Flask(__name__)
jobs = [
 {"titre":"Vendeuse","ville":"Ouaga 2000","salaire":"75 000 FCFA","whatsapp":"","desc":""},
 {"titre":"Chauffeur","ville":"Tampouy","salaire":"90 000 FCFA","whatsapp":"","desc":""},
 {"titre":"Secretaire","ville":"Koulouba","salaire":"120 000 FCFA","whatsapp":"","desc":""},
]
ACCUEIL = """
<html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<style>body{font-family:Arial;background:#FFF8E7;margin:0} .h{background:#008751;color:white;text-align:center;padding:20px} .c{background:white;margin:10px;padding:12px;border-left:5px solid #F7941D} .b{background:#008751;color:white;padding:8px 12px;text-decoration:none;display:inline-block;border-radius:5px} .o{background:#F7941D;color:white;padding:12px 20px;text-decoration:none;display:inline-block;border-radius:5px;font-weight:bold} .ct{text-align:center;margin:20px}</style></head>
<body><div class="h"><h1>FASOJOB</h1><p>Emplois au Burkina Faso</p></div>
<div class="ct"><a class="o" href="/publier">+ PUBLIER UNE OFFRE GRATUIT</a></div>
{% for j in jobs %}<div class="c"><b>{{j.titre}} - {{j.ville}}</b><br>{{j.salaire}}<br>{% if j.desc %}<p>{{j.desc}}</p>{% endif %}
{% if j.whatsapp %}<a class="b" href="https://wa.me/{{j.whatsapp}}">Postuler sur WhatsApp</a>{% else %}<a class="b" href="#">Postuler</a>{% endif %}</div>{% endfor %}
<div class="ct"><a class="o" href="/publier">S'INSCRIRE GRATUIT</a></div></body></html>
"""
PUBLIER = """
<html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<style>body{font-family:Arial;background:#FFF8E7;padding:15px} input,textarea{width:100%;padding:12px;margin:8px 0;border:1px solid #ccc;border-radius:5px} button{background:#008751;color:white;padding:14px;width:100%;border:none;border-radius:5px;font-size:16px}</style></head>
<body><h2 style="text-align:center;color:#008751">Publier une offre - Gratuit</h2>
<form method="POST">
<input name="titre" placeholder="Titre : Ex: Vendeuse" required>
<input name="ville" placeholder="Ville / Quartier : Ex: Ouaga 2000" required>
<input name="salaire" placeholder="Salaire : Ex: 75 000 FCFA" required>
<input name="whatsapp" placeholder="WhatsApp : Ex: 22670000000" required>
<textarea name="desc" placeholder="Description du poste..."></textarea>
<button type="submit">PUBLIER MON OFFRE</button></form>
<p style="text-align:center"><a href="/">Retour a l'accueil</a></p></body></html>
"""
@app.route("/")
def home():
 return render_template_string(ACCUEIL, jobs=reversed(jobs))
@app.route("/publier", methods=["GET","POST"])
def publier():
 if request.method=="POST":
  jobs.append({"titre":request.form["titre"],"ville":request.form["ville"],"salaire":request.form["salaire"],"whatsapp":request.form["whatsapp"].replace(" ","").replace("+",""),"desc":request.form["desc"]})
  return redirect("/")
 return render_template_string(PUBLIER)
if __name__=="__main__":
 app.run(host="0.0.0.0", port=10000)