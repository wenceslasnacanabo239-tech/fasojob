from flask import Flask, request, redirect, render_template_string, session
import json, os
app = Flask(__name__)
app.secret_key = "fasojob-2026"

def load(n,d):
 try:
  if os.path.exists(n):
   with open(n,"r",encoding="utf-8") as f: return json.load(f)
 except: pass
 return d
def save(n,d):
 try:
  with open(n,"w",encoding="utf-8") as f: json.dump(d,f,ensure_ascii=False)
 except: pass

jobs = load("jobs.json",[])
produits = load("produits.json",[])
users = load("users.json",[])

STYLE="<meta name='viewport' content='width=device-width, initial-scale=1'><style>body{font-family:Arial;background:#FFF8E7;margin:0} .h{background:#008751;color:white;text-align:center;padding:15px} .h a{color:white;margin:0 5px;text-decoration:none;font-weight:bold} .c{background:white;margin:10px;padding:12px;border-radius:10px} .b{background:#008751;color:white;padding:8px 12px;text-decoration:none;border-radius:5px;display:inline-block} .v{background:#FF5722;color:white;padding:14px 20px;text-decoration:none;border-radius:8px;font-weight:bold;display:inline-block} .o{background:#F7941D;color:white;padding:12px 20px;text-decoration:none;border-radius:5px;font-weight:bold;display:inline-block} .ct{text-align:center;margin:15px} input,select,textarea{width:100%;padding:12px;margin:8px 0;border:1px solid #ccc;border-radius:5px;box-sizing:border-box} button{background:#008751;color:white;padding:14px;width:100%;border:none;border-radius:5px} .alert{background:#FFF3CD;border:2px solid #F7941D;padding:10px;border-radius:8px;margin:10px;text-align:center}</style>"

@app.route("/")
def home():
 u=session.get("user","")
 h=STYLE+f"<body><div class='h'><h1>FASOJOB</h1><a href='/'>Accueil</a><a href='/boutique'>MARKET</a>"
 if u: h+=f"<span>👋 {u}</span> <a href='/deconnexion'>Quitter</a>"
 else: h+="<a href='/inscription'>S'inscrire</a>"
 h+="</div><div class='ct'>"
 if not u: h+="<div class='alert'>👀 REGARDER = LIBRE sans compte<br>🔒 VENDRE + POSTULER = COMPTE OBLIGATOIRE</div>"
 else: h+=f"<p>✅ Connecté : <b>{u}</b></p>"
 h+="<br><a class='o' href='/boutique'>🛍️ REGARDER MARKET</a><br><br><a class='v' href='/vendre'>💰 VENDRE</a><br><br><a class='o' href='/publier'>+ PUBLIER EMPLOI</a></div><h3 style='text-align:center'>Produits</h3>"
 for i,p in enumerate(reversed(produits)):
  h+=f"<div class='c'><b>{p.get('nom','')}</b> - {p.get('prix','')} FCFA<br>{p.get('ville','')}<br><a class='b' href='/commander/{len(produits)-1-i}'>Commander</a></div>"
 h+="<h3 style='text-align:center'>Emplois</h3>"
 for i,j in enumerate(reversed(jobs)):
  idx=len(jobs)-1-i
  h+=f"<div class='c'><b>{j.get('titre','')}</b> - {j.get('ville','')}<br>{j.get('salaire','')}<br><a class='b' href='/postuler/{idx}'>💼 POSTULER</a></div>"
 return h+"</body>"

@app.route("/boutique")
def boutique():
 u=session.get("user","")
 h=STYLE+"<body><div class='h'><h1>🛍️ FASOJOB MARKET</h1><a href='/'>Accueil</a></div><div class='ct'><div class='alert'>👀 REGARDER = Libre<br>🔒 VENDRE = Compte obligatoire</div><a class='v' href='/vendre'>💰 VENDRE</a></div>"
 for i,p in enumerate(reversed(produits)):
  idx=len(produits)-1-i
  h+=f"<div class='c'><b>{p.get('nom','')}</b> - {p.get('prix','')} FCFA<br>{p.get('ville','')} | {p.get('cat','')}<br><a class='b' href='/commander/{idx}'>Commander</a></div>"
 return h+"</body>"

@app.route("/inscription", methods=["GET","POST"])
def insc():
 if request.method=="POST":
  nom=request.form["nom"]; wa=request.form["whatsapp"].replace(" ","").replace("+","")
  if not any(isinstance(x,dict) and x.get("whatsapp")==wa for x in users):
   users.append({"nom":nom,"whatsapp":wa,"type":request.form["type"]}); save("users.json",users)
  session["user"]=nom; session["whatsapp"]=wa
  return redirect(request.args.get("next","/vendre"))
 return STYLE+"<body><div class='h'><h2>🔒 COMPTE OBLIGATOIRE</h2><a href='/'>Accueil</a></div><div style='padding:15px'><div class='alert'>👀 Regarder = Sans compte<br>🔒 VENDRE ou POSTULER = Crée un compte GRATUIT</div><form method='POST'><input name='nom' placeholder='Ton Nom' required><input name='whatsapp' placeholder='WhatsApp 22670000000' required><select name='type'><option>Vendeur</option><option>Cherche Emploi</option><option>Recruteur</option></select><button>CRÉER MON COMPTE GRATUIT</button></form></div></body>"

@app.route("/vendre", methods=["GET","POST"])
def vendre():
 if "user" not in session: return redirect("/inscription?next=/vendre")
 if request.method=="POST":
  produits.append({"nom":request.form["nom"],"prix":request.form["prix"],"cat":request.form["cat"],"ville":request.form["ville"],"whatsapp":request.form["whatsapp"].replace(" ","").replace("+",""),"img":"https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500"}); save("produits.json",produits); return redirect("/boutique")
 return STYLE+f"<body><div class='h'><h2>💰 VENDRE - {session.get('user')}</h2><a href='/'>Accueil</a></div><div style='padding:15px'><form method='POST'><input name='nom' placeholder='Nom produit' required><input name='prix' placeholder='Prix' required><select name='cat'><option>Vetements</option><option>Chaussures</option><option>Telephones</option><option>Beaute</option><option>Maison</option><option>Autre</option></select><input name='ville' placeholder='Quartier' required><input name='whatsapp' placeholder='WhatsApp' required><button>VENDRE GRATUIT</button></form></div></body>"

@app.route("/publier", methods=["GET","POST"])
def publier():
 if "user" not in session: return redirect("/inscription?next=/publier")
 if request.method=="POST":
  jobs.append({"titre":request.form["titre"],"ville":request.form["ville"],"salaire":request.form["salaire"],"whatsapp":request.form["whatsapp"].replace(" ","").replace("+",""),"desc":request.form["desc"]}); save("jobs.json",jobs); return redirect("/")
 return STYLE+"<body><div class='h'><h2>Publier Emploi</h2><a href='/'>Accueil</a></div><div style='padding:15px'><form method='POST'><input name='titre' placeholder='Titre' required><input name='ville' placeholder='Ville' required><input name='salaire' placeholder='Salaire' required><input name='whatsapp' placeholder='WhatsApp' required><textarea name='desc' placeholder='Description'></textarea><button>PUBLIER</button></form></div></body>"

@app.route("/postuler/<int:id>")
def postuler(id):
 if "user" not in session: return redirect(f"/inscription?next=/postuler/{id}")
 if 0 <= id < len(jobs):
  j=jobs[id]; return redirect(f"https://wa.me/{j.get('whatsapp','')}?text=Bonjour je suis {session.get('user')} je veux postuler pour {j.get('titre','')} sur FASOJOB")
 return redirect("/")

@app.route("/commander/<int:id>")
def commander(id):
 if 0 <= id < len(produits):
  p=produits[id]; return redirect(f"https://wa.me/{p.get('whatsapp','')}?text=Bonjour je veux acheter {p.get('nom','')} sur FASOJOB")
 return redirect("/boutique")

@app.route("/deconnexion")
def deco():
 session.clear(); return redirect("/")
@app.route("/admin")
def admin():
 return STYLE+f"<body><div class='h'><h2>📊 ADMIN</h2><a href='/'>Voir site</a></div><div class='c'>Inscrits : {len(users)}<br>Produits : {len(produits)}<br>Emplois : {len(jobs)}</div>"+"".join([f"<div class='c'>{u.get('nom','')} - {u.get('whatsapp','')}</div>" for u in users if isinstance(u,dict)])+"</body>"

@app.errorhandler(500)
def err500(e): return STYLE+"<body><div class='h'><h1>FASOJOB</h1></div><div class='c'><h2>Petit problème, on répare...</h2><p>Reviens dans 1 minute, <a href='/'>Clique ici</a></p></div></body>", 500

if __name__=="__main__": app.run(host="0.0.0.0", port=10000)