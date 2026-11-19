from flask import Flask, request, redirect, render_template_string, jsonify, Response, session
import json, os, io
from PIL import Image, ImageDraw, ImageFont
app = Flask(__name__)
app.secret_key = "fasojob-secret-2026"

def charger(nom, defaut):
 if os.path.exists(nom):
  try:
   with open(nom,"r",encoding="utf-8") as f: return json.load(f)
  except: pass
 return defaut
def sauver(nom, data):
 with open(nom,"w",encoding="utf-8") as f: json.dump(data,f,ensure_ascii=False)

jobs = charger("jobs.json",[{"titre":"Vendeuse","ville":"Ouaga 2000","salaire":"75 000 FCFA","whatsapp":"","desc":""}])
produits = charger("produits.json",[{"nom":"Chaussures Nike Air","prix":"15000","cat":"Chaussures","ville":"Tampouy","whatsapp":"","img":"https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500"}])
users = charger("users.json",[])
visites = charger("visites.json",{"total":0})

STYLE="<meta name='viewport' content='width=device-width, initial-scale=1'><link rel='manifest' href='/manifest.json'><meta name='theme-color' content='#008751'><style>body{font-family:Arial;background:#FFF8E7;margin:0} .h{background:#008751;color:white;text-align:center;padding:15px} .h a{color:white;text-decoration:none;margin:0 6px;font-weight:bold;font-size:14px} .c{background:white;margin:10px;padding:12px;border-radius:10px;box-shadow:0 1px 5px #ccc} .b{background:#008751;color:white;padding:8px 12px;text-decoration:none;display:inline-block;border-radius:5px} .o{background:#F7941D;color:white;padding:12px 20px;text-decoration:none;display:inline-block;border-radius:5px;font-weight:bold} .v{background:#FF5722;color:white;padding:15px 25px;text-decoration:none;display:inline-block;border-radius:8px;font-weight:bold;font-size:18px} .ct{text-align:center;margin:15px} .s{width:80%;padding:12px;border-radius:5px;border:1px solid #ccc} input,select,textarea{width:100%;padding:12px;margin:8px 0;border:1px solid #ccc;border-radius:5px;box-sizing:border-box} button{background:#008751;color:white;padding:14px;width:100%;border:none;border-radius:5px;font-size:16px} .grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:10px} .card{background:white;border-radius:10px;overflow:hidden;box-shadow:0 1px 5px #ccc} .card img{width:100%;height:140px;object-fit:cover} .card div{padding:8px} .prix{color:#FF5722;font-weight:bold;font-size:16px} .catbtn{background:white;border:1px solid #008751;color:#008751;padding:6px 10px;border-radius:20px;text-decoration:none;font-size:13px;margin:3px;display:inline-block} .stat{background:white;margin:10px;padding:20px;border-radius:10px;text-align:center;box-shadow:0 1px 5px #ccc} .stat b{font-size:35px;color:#008751} .alert{background:#FFF3CD;border:2px solid #F7941D;padding:12px;border-radius:8px;margin:10px;text-align:center}</style>"

ACCUEIL = STYLE + """
<body><div class="h"><h1 style="margin:0">FASOJOB</h1><p style="margin:5px">Emplois & FASOJOB MARKET - Burkina</p><a href="/">🏠 Accueil</a><a href="/boutique">🛍️ MARKET</a>{% if user %}<span>👋 {{user}}</span> <a href="/deconnexion">Quitter</a>{% else %}<a href="/inscription">👤 S'inscrire</a>{% endif %}</div>
<div class="ct"><p>👥 <b>{{nb_users}} inscrits</b> | 👀 {{visites}} visites</p>
{% if not user %}<div class="alert">👀 <b>REGARDER = LIBRE, sans compte</b><br>🔒 <b>VENDRE + POSTULER = COMPTE OBLIGATOIRE</b></div>{% else %}<p>✅ Connecté : <b>{{user}}</b> - Tu peux VENDRE et POSTULER</p>{% endif %}
<br><a class="o" href="/boutique">🛍️ REGARDER LE MARKET</a><br><br>
<a class="v" href="/vendre">💰 VENDRE MON PRODUIT</a><br><small>🔒 Compte obligatoire</small><br><br>
<a class="o" style="background:#008751" href="/publier">+ PUBLIER UN EMPLOI</a></div>
<h3 style="text-align:center">🔥 Produits - Regarder libre</h3><div class="grid">
{% for idx,p in produits[:4] %}<div class="card"><img src="{{p.img}}"><div><b>{{p.nom}}</b><br><span class="prix">{{p.prix}} FCFA</span><br><small>{{p.ville}} - {{p.cat}}</small><br><a class="b" href="/commander/{{p.orig_idx}}">🛒 Commander</a></div></div>{% endfor %}</div>
<h3 style="text-align:center">🔥 Emplois - Regarder libre, Postuler = Compte</h3>
{% for idx,j in jobs %}<div class="c"><b>{{j.titre}} - {{j.ville}}</b><br>{{j.salaire}}<br>{% if j.desc %}<p>{{j.desc}}</p>{% endif %}<a class="b" href="/postuler/{{j.orig_idx}}">💼 POSTULER {% if not user %}🔒{% endif %}</a></div>{% endfor %}
</body></html>
"""

BOUTIQUE = STYLE + """
<body><div class="h"><h1 style="margin:0">🛍️ FASOJOB MARKET</h1><a href="/">🏠 Accueil</a><a href="/boutique">🛍️ MARKET</a></div>
<div class="ct"><div class="alert">👀 REGARDER = Sans compte<br>🔒 VENDRE = Compte obligatoire</div>
<a class="v" href="/vendre">💰 VENDRE - COMPTE OBLIGATOIRE</a><br><br>
<form method="GET"><input class="s" name="q" value="{{q}}" placeholder="Rechercher..."><br><br><button class="b" type="submit">Rechercher</button></form><br>
<a class="catbtn" href="/boutique">Tous</a><a class="catbtn" href="/boutique?cat=Vetements">👕 Vêtements</a><a class="catbtn" href="/boutique?cat=Chaussures">👟 Chaussures</a><a class="catbtn" href="/boutique?cat=Telephones">📱 Téléphones</a><a class="catbtn" href="/boutique?cat=Beaute">💄 Beauté</a><a class="catbtn" href="/boutique?cat=Maison">🏠 Maison</a></div>
<div class="grid">{% for idx,p in produits %}<div class="card"><img src="{{p.img}}"><div><b>{{p.nom}}</b><br><span class="prix">{{p.prix}} FCFA</span><br><small>{{p.ville}} | {{p.cat}}</small><br><a class="b" href="/commander/{{p.orig_idx}}">🛒 Commander</a></div></div>{% endfor %}</div>
</body></html>
"""

INSCRIPTION = STYLE + """<body><div class="h"><h2>🔒 COMPTE OBLIGATOIRE</h2><a href="/">Accueil</a></div><div style="padding:15px"><div class="alert">👀 Regarder = Sans compte<br>🔒 <b>VENDRE ou POSTULER = Tu dois créer un compte</b><br>C'est GRATUIT, juste Nom + WhatsApp</div><form method="POST"><input name="nom" placeholder="Ton Nom : Ex: Wenceslas" required><input name="whatsapp" placeholder="Ton WhatsApp : 22670000000" required><select name="type"><option>Vendeur</option><option>Acheteur / Cherche Emploi</option><option>Recruteur</option></select><button>CRÉER MON COMPTE GRATUIT</button></form><p style="text-align:center">Déjà inscrit ? <a href="/connexion">Connecte-toi ici</a></p></div></body></html>"""

CONNEXION = STYLE + """<body><div class="h"><h2>👋 Bon retour !</h2><a href="/">Accueil</a></div><div style="padding:15px"><form method="POST"><input name="whatsapp" placeholder="Ton WhatsApp : 22670000000" required><button>SE CONNECTER</button></form><p style="text-align:center">Pas encore de compte ? <a href="/inscription">Inscris-toi</a></p></div></body></html>"""

ADMIN = STYLE + """<body><div class="h"><h2>📊 TABLEAU DE BORD</h2><a href="/">Voir le site</a></div>
<div class="stat"><b>{{visites}}</b><br>👀 Visites</div><div class="stat"><b>{{nb_users}}</b><br>👥 Inscrits</div><div class="stat"><b>{{nb_produits}}</b><br>🛍️ Produits</div><div class="stat"><b>{{nb_jobs}}</b><br>💼 Emplois</div>
{% for u in users %}<div class="c"><b>{{u.nom}}</b> - {{u.type}}<br>📱 <a href="https://wa.me/{{u.whatsapp}}">{{u.whatsapp}}</a></div>{% endfor %}</body></html>"""

PUBLIER = STYLE + """<body><div class="h"><h2>Publier une offre - {{user}}</h2><a href="/">Accueil</a></div><div style="padding:15px"><form method="POST"><input name="titre" placeholder="Titre : Vendeuse" required><input name="ville" placeholder="Ville : Ouaga 2000" required><input name="salaire" placeholder="Salaire : 75 000 FCFA" required><input name="whatsapp" placeholder="WhatsApp : 22670000000" required><textarea name="desc" placeholder="Description..."></textarea><button>PUBLIER MON OFFRE</button></form></div></body></html>"""

VENDRE = STYLE + """<body><div class="h"><h2>💰 VENDRE - {{user}}</h2><a href="/">Accueil</a> <a href="/boutique">Market</a></div><div style="padding:15px"><p style="text-align:center">✅ Tu es inscrit, tu peux vendre maintenant !</p><form method="POST"><input name="nom" placeholder="Nom du produit" required><input name="prix" placeholder="Prix : Ex: 15000" required><select name="cat"><option>Vetements</option><option>Chaussures</option><option>Telephones</option><option>Beaute</option><option>Maison</option><option>Autre</option></select><input name="ville" placeholder="Quartier : Tampouy" required><input name="whatsapp" placeholder="WhatsApp : 22670000000" required><input name="img" placeholder="Lien photo - Sinon laisse vide"><button>💰 VENDRE MON PRODUIT GRATUIT</button></form></div></body></html>"""

@app.route("/")
def home():
 visites["total"]=visites.get("total",0)+1; sauver("visites.json",visites)
 jobs_list=[{"orig_idx":i,"titre":j["titre"],"ville":j["ville"],"salaire":j["salaire"],"desc":j.get("desc",""),"whatsapp":j.get("whatsapp","")} for i,j in enumerate(jobs)]
 prod_list=[{"orig_idx":i,"nom":p["nom"],"prix":p["prix"],"ville":p["ville"],"cat":p["cat"],"img":p["img"],"whatsapp":p.get("whatsapp","")} for i,p in enumerate(produits)]
 return render_template_string(ACCUEIL, jobs=list(reversed(jobs_list)), produits=list(reversed(prod_list)), nb_users=len(users), visites=visites["total"], user=session.get("user"))

@app.route("/boutique")
def boutique():
 q=request.args.get("q","").lower(); cat=request.args.get("cat","")
 liste=[{"orig_idx":i,"nom":p["nom"],"prix":p["prix"],"ville":p["ville"],"cat":p["cat"],"img":p["img"],"whatsapp":p.get("whatsapp","")} for i,p in enumerate(produits)]
 liste=list(reversed(liste))
 if cat: liste=[p for p in liste if p["cat"]==cat]
 if q: liste=[p for p in liste if q in p["nom"].lower() or q in p["ville"].lower()]
 return render_template_string(BOUTIQUE, produits=liste, q=request.args.get("q",""))

@app.route("/postuler/<int:id>")
def postuler(id):
 # REGLE : Regarder libre, Postuler = Compte obligatoire
 if "user" not in session:
  return redirect(f"/inscription?next=/postuler/{id}")
 if 0 <= id < len(jobs):
  j=jobs[id]
  wa=j.get("whatsapp","")
  return redirect(f"https://wa.me/{wa}?text=Bonjour je suis {session.get('user')} je veux postuler pour {j['titre']} sur FASOJOB")
 return redirect("/")

@app.route("/commander/<int:id>")
def commander(id):
 # Commander = Regarder + Acheter libre, on ne bloque pas, mais si pas inscrit on propose de s'inscrire apres
 if 0 <= id < len(produits):
  p=produits[id]
  return redirect(f"https://wa.me/{p.get('whatsapp','')}?text=Bonjour je veux acheter {p['nom']} a {p['prix']} FCFA sur FASOJOB")
 return redirect("/boutique")

@app.route("/inscription", methods=["GET","POST"])
def inscription():
 if request.method=="POST":
  nom=request.form["nom"]; wa=request.form["whatsapp"].replace(" ","").replace("+","")
  if not [u for u in users if u["whatsapp"]==wa]:
   users.append({"nom":nom,"whatsapp":wa,"type":request.form["type"]}); sauver("users.json",users)
  session["user"]=nom; session["whatsapp"]=wa
  return redirect(request.args.get("next","/vendre"))
 return render_template_string(INSCRIPTION)

@app.route("/connexion", methods=["GET","POST"])
def connexion():
 if request.method=="POST":
  wa=request.form["whatsapp"].replace(" ","").replace("+","")
  trouve=[u for u in users if u["whatsapp"]==wa]
  if trouve:
   session["user"]=trouve[0]["nom"]; session["whatsapp"]=wa; return redirect("/")
  return redirect("/inscription")
 return render_template_string(CONNEXION)

@app.route("/deconnexion")
def deconnexion():
 session.clear(); return redirect("/")

@app.route("/admin")
def admin():
 return render_template_string(ADMIN, visites=visites.get("total",0), nb_users=len(users), users=list(reversed(users)), nb_produits=len(produits), nb_jobs=len(jobs))

@app.route("/publier", methods=["GET","POST"])
def publier():
 if "user" not in session: return redirect("/inscription?next=/publier")
 if request.method=="POST":
  jobs.append({"titre":request.form["titre"],"ville":request.form["ville"],"salaire":request.form["salaire"],"whatsapp":request.form["whatsapp"].replace(" ","").replace("+",""),"desc":request.form["desc"],"auteur":session.get("user","")}); sauver("jobs.json",jobs); return redirect("/")
 return render_template_string(PUBLIER, user=session.get("user"))

@app.route("/vendre", methods=["GET","POST"])
def vendre():
 if "user" not in session: return redirect("/inscription?next=/vendre")
 if request.method=="POST":
  img=request.form["img"] or "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500"
  produits.append({"nom":request.form["nom"],"prix":request.form["prix"],"cat":request.form["cat"],"ville":request.form["ville"],"whatsapp":request.form["whatsapp"].replace(" ","").replace("+",""),"img":img,"auteur":session.get("user","")}); sauver("produits.json",produits); return redirect("/boutique")
 return render_template_string(VENDRE, user=session.get("user"))

@app.route("/publier-produit")
def old_vendre(): return redirect("/vendre")

@app.route("/manifest.json")
def manifest(): return jsonify({"name":"FASOJOB","short_name":"FASOJOB","start_url":"/","display":"standalone","background_color":"#FFF8E7","theme_color":"#008751","icons":[{"src":"/icon.png?v=2","sizes":"512x512","type":"image/png","purpose":"any"}]})
@app.route("/sw.js")
def sw(): return Response("self.addEventListener('fetch',e=>{e.respondWith(fetch(e.request).catch(()=>caches.match(e.request)))})", mimetype="application/javascript")
@app.route("/icon.png")
def icon():
 img=Image.new("RGB",(512,512),"#008751"); d=ImageDraw.Draw(img)
 try: f1=ImageFont.truetype("DejaVuSans-Bold.ttf",150); f2=ImageFont.truetype("DejaVuSans-Bold.ttf",62); f3=ImageFont.truetype("DejaVuSans-Bold.ttf",38)
 except: f1=ImageFont.load_default(); f2=f1; f3=f1
 d.rectangle([15,15,497,497],outline="#F7941D",width=12); d.text((256,180),"F",font=f1,fill="white",anchor="mm"); d.text((256,330),"FASOJOB",font=f2,fill="white",anchor="mm"); d.text((256,400),"BURKINA",font=f3,fill="#F7941D",anchor="mm")
 buf=io.BytesIO(); img.save(buf,format="PNG"); buf.seek(0); return Response(buf.getvalue(), mimetype="image/png")
if __name__=="__main__": app.run(host="0.0.0.0", port=10000)