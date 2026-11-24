from flask import Flask, request, redirect, render_template_string, session, send_from_directory
import json, os, uuid
from datetime import datetime
from werkzeug.utils import secure_filename
app = Flask(__name__)
app.secret_key = "fasojob-2026"
os.makedirs("static/uploads", exist_ok=True)

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

def today():
 # Date du jour au Burkina
 return datetime.now().strftime("%d/%m/%Y")

jobs = load("jobs.json",[])
produits = load("produits.json",[])
users = load("users.json",[])

STYLE="""
<meta name='viewport' content='width=device-width, initial-scale=1'>
<style>
body{font-family:Arial;background:#FFF8E7;margin:0;padding-bottom:20px}
.h{background:#008751;color:white;text-align:center;padding:12px 10px;position:sticky;top:0;z-index:10}
.h h1{margin:0;font-size:24px}
.h a{color:white;margin:0 6px;text-decoration:none;font-weight:bold;font-size:13px}
.topbtn{text-align:center;margin:12px 10px}
.btn-vert{background:#008751;color:white;padding:12px 20px;border-radius:6px;font-weight:bold;display:inline-block;text-decoration:none;font-size:15px}
.btn-orange{background:#F7941D;color:white;padding:14px 20px;border-radius:6px;font-weight:bold;display:inline-block;text-decoration:none;font-size:15px;width:85%;text-align:center}
h2.sec{text-align:center;margin:18px 0 10px;font-size:20px}
.card{background:white;margin:10px;padding:14px;border-radius:10px;box-shadow:0 1px 4px rgba(0,0,0,0.08)}
.card b{font-size:16px}
.card .salaire{font-size:15px;margin:2px 0}
.card .desc{font-size:14px;margin:8px 0}
.date{font-size:12px;color:#888;margin:4px 0}
.btn-post{background:#008751;color:white;padding:9px 14px;border-radius:5px;text-decoration:none;display:inline-block;font-size:14px}
.suppr{color:#E53935;font-size:13px;margin-left:10px;text-decoration:none;font-weight:bold}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:0 10px}
.pcard{background:white;border-radius:10px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,0.08);padding-bottom:10px;position:relative}
.pcard img{width:100%;height:150px;object-fit:cover}
.pcard .info{padding:8px 10px}
.pcard .nom{font-weight:bold;font-size:14px;line-height:1.2}
.pcard .prix{color:#E65100;font-weight:bold;font-size:15px;margin:3px 0}
.pcard .lieu{font-size:12px;color:#333}
.btn-cmd{background:#008751;color:white;padding:8px 12px;border-radius:5px;text-decoration:none;display:inline-block;font-size:14px;margin-top:6px}
.alert{background:#FFF3CD;border:2px solid #F7941D;padding:10px;border-radius:8px;margin:10px;text-align:center;font-size:14px}
input,select,textarea{width:100%;padding:12px;margin:8px 0;border:1px solid #ccc;border-radius:5px;box-sizing:border-box}
button{background:#008751;color:white;padding:14px;width:100%;border:none;border-radius:5px;font-weight:bold}
.photo-box{border:2px dashed #008751;padding:15px;text-align:center;border-radius:10px;background:#E8F5E9}
#preview{width:100%;max-height:220px;object-fit:cover;border-radius:8px;display:none;margin-top:10px}
.badge-new{background:#FF5722;color:white;font-size:11px;padding:2px 6px;border-radius:10px}
</style>
<script>function showPreview(e){var f=e.files[0]; if(f){var r=new FileReader(); r.onload=function(ev){var img=document.getElementById('preview'); img.src=ev.target.result; img.style.display='block';}; r.readAsDataURL(f);}}
function confirmer(msg){return confirm(msg);}</script>
"""

def header():
 u=session.get("user","")
 h=f"<div class='h'><h1>FASOJOB</h1>"
 h+=f"<a href='/'>Accueil</a><a href='/boutique'>MARKET</a>"
 if u: h+=f"<span>👋 {u}</span> <a href='/deconnexion'>Quitter</a>"
 else: h+="<a href='/inscription'>S'inscrire</a>"
 return h+"</div>"

@app.route("/")
def home():
 h=STYLE+"<body>"+header()
 h+="<div class='topbtn'><a class='btn-vert' href='/vendre'>+ VENDRE UN PRODUIT</a></div>"
 if "user" not in session:
  h+="<div class='alert'>👀 Regarder = Sans compte<br>🔒 VENDRE ou POSTULER = Crée un compte GRATUIT</div>"
 else:
  h+=f"<p style='text-align:center'>✅ Connecté : <b>{session.get('user')}</b></p>"
 # EMPLOIS
 h+="<h2 class='sec'>🔥 Emplois Récents</h2>"
 if not jobs:
  h+="<div class='card' style='text-align:center'>Aucun emploi pour le moment.<br><br><a class='btn-orange' href='/publier'>+ Publier une offre</a></div>"
 for i,j in enumerate(reversed(jobs)):
  idx=len(jobs)-1-i
  date_txt=j.get('date', today())
  is_new=" <span class='badge-new'>NOUVEAU</span>" if date_txt==today() else ""
  h+=f"<div class='card'><b>{j.get('titre','')} - {j.get('ville','')}</b>{is_new}<div class='salaire'>{j.get('salaire','')}</div>"
  if j.get('desc'): h+=f"<div class='desc'>{j.get('desc')}</div>"
  h+=f"<div class='date'>📅 Publié le {date_txt}</div>"
  h+=f"<a class='btn-post' href='/postuler/{idx}'>Postuler WhatsApp</a> <a class='suppr' href='/supprimer_emploi/{idx}' onclick=\"return confirmer('Supprimer cette offre ? Elle n\\'existe plus ?')\">🗑️ Supprimer</a></div>"
 # PRODUITS
 h+="<h2 class='sec'>🔥 Produits Populaires</h2>"
 if not produits:
  h+="<div class='card' style='text-align:center'>Aucun produit pour le moment.<br>Sois le premier à vendre !</div>"
 else:
  h+="<div class='grid'>"
  for i,p in enumerate(reversed(produits)):
   idx=len(produits)-1-i
   img=p.get('img','https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500')
   date_txt=p.get('date', today())
   h+=f"<div class='pcard'><img src='{img}'><div class='info'><div class='nom'>{p.get('nom','')}</div><div class='prix'>{p.get('prix','')} FCFA</div><div class='lieu'>{p.get('ville','')} - {p.get('cat','')}</div><div class='date'>📅 {date_txt}</div><a class='btn-cmd' href='/commander/{idx}'>Commander</a><br><a class='suppr' href='/supprimer_produit/{idx}' onclick=\"return confirmer('Ce produit n\\'est plus en stock ? Supprimer ?')\">🗑️ Supprimer</a></div></div>"
  h+="</div>"
 h+="<div class='topbtn' style='margin-top:20px'><a class='btn-orange' href='/publier'>+ PUBLIER UNE OFFRE GRATUIT</a></div>"
 return h+"</body>"

@app.route("/boutique")
def boutique():
 h=STYLE+"<body>"+header()
 h+="<div class='topbtn'><a class='btn-vert' href='/vendre'>+ VENDRE UN PRODUIT</a></div>"
 h+="<h2 class='sec'>🔥 Produits Populaires</h2><div class='grid'>"
 for i,p in enumerate(reversed(produits)):
  idx=len(produits)-1-i
  h+=f"<div class='pcard'><img src='{p.get('img','')}'><div class='info'><div class='nom'>{p.get('nom','')}</div><div class='prix'>{p.get('prix','')} FCFA</div><div class='lieu'>{p.get('ville','')} - {p.get('cat','')}</div><div class='date'>📅 {p.get('date','')}</div><a class='btn-cmd' href='/commander/{idx}'>Commander</a><br><a class='suppr' href='/supprimer_produit/{idx}' onclick=\"return confirmer('Produit plus en stock ? Supprimer ?')\">🗑️ Supprimer</a></div></div>"
 h+="</div><div class='topbtn'><a class='btn-orange' href='/publier'>+ PUBLIER UNE OFFRE GRATUIT</a></div></body>"
 return h

@app.route("/inscription", methods=["GET","POST"])
def insc():
 if request.method=="POST":
  nom=request.form["nom"]; wa=request.form["whatsapp"].replace(" ","").replace("+","")
  if not any(isinstance(x,dict) and x.get("whatsapp")==wa for x in users):
   users.append({"nom":nom,"whatsapp":wa,"type":request.form["type"],"date":today()}); save("users.json",users)
  session["user"]=nom; session["whatsapp"]=wa
  return redirect(request.args.get("next","/vendre"))
 return STYLE+"<body>"+header()+"<div style='padding:15px'><div class='alert'>👀 Regarder = Sans compte<br>🔒 VENDRE ou POSTULER = Crée un compte GRATUIT</div><form method='POST'><input name='nom' placeholder='Ton Nom' required><input name='whatsapp' placeholder='WhatsApp 22670000000' required><select name='type'><option>Vendeur</option><option>Cherche Emploi</option><option>Recruteur</option></select><button>CRÉER MON COMPTE GRATUIT</button></form></div></body>"

@app.route("/vendre", methods=["GET","POST"])
def vendre():
 if "user" not in session: return redirect("/inscription?next=/vendre")
 if request.method=="POST":
  img_url = request.form.get("img","")
  if "photo" in request.files:
   f = request.files["photo"]
   if f and f.filename != "":
    ext = secure_filename(f.filename).rsplit(".",1)[-1].lower() if "." in f.filename else "jpg"
    if ext not in ["jpg","jpeg","png","webp"]: ext="jpg"
    fname = f"{uuid.uuid4().hex[:8]}.{ext}"
    f.save(os.path.join("static/uploads", fname))
    img_url = f"/static/uploads/{fname}"
  if not img_url: img_url="https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500"
  produits.append({"nom":request.form["nom"],"prix":request.form["prix"],"cat":request.form["cat"],"ville":request.form["ville"],"whatsapp":request.form["whatsapp"].replace(" ","").replace("+",""),"img":img_url,"date":today()}); save("produits.json",produits); return redirect("/")
 return STYLE+f"""<body>{header()}<div style='padding:15px'><h2 style='text-align:center'>💰 VENDRE - {session.get('user')}</h2>
 <form method='POST' enctype='multipart/form-data'>
 <input name='nom' placeholder='Nom du produit : Ex: Samsung Galaxy A14' required>
 <input name='prix' placeholder='Prix : Ex: 85000' required>
 <select name='cat'><option>Telephones</option><option>Vetements</option><option>Chaussures</option><option>Beaute</option><option>Maison</option><option>Autre</option></select>
 <input name='ville' placeholder='Quartier : Koulouba' required>
 <input name='whatsapp' placeholder='WhatsApp : 22670000000' required>
 <div class='photo-box'><b>📸 PHOTO DE TON ARTICLE</b><br><small>Choisis depuis ta galerie</small><br><br>
 <input type='file' name='photo' accept='image/*' onchange='showPreview(event)' style='border:none'>
 <img id='preview'><p style='font-size:12px'>Ou colle un lien photo :</p><input name='img' placeholder='https://...'></div>
 <button>💰 VENDRE MON PRODUIT AVEC PHOTO</button></form></div></body>"""

@app.route("/publier", methods=["GET","POST"])
def publier():
 if "user" not in session: return redirect("/inscription?next=/publier")
 if request.method=="POST":
  jobs.append({"titre":request.form["titre"],"ville":request.form["ville"],"salaire":request.form["salaire"],"whatsapp":request.form["whatsapp"].replace(" ","").replace("+",""),"desc":request.form["desc"],"date":today()}); save("jobs.json",jobs); return redirect("/")
 return STYLE+"<body>"+header()+"<div style='padding:15px'><h2 style='text-align:center'>+ PUBLIER UNE OFFRE GRATUIT</h2><form method='POST'><input name='titre' placeholder='Ex: Dame de ménage' required><input name='ville' placeholder='Ex: Ouagadougou / Nioko 2' required><input name='salaire' placeholder='Ex: 50000' required><input name='whatsapp' placeholder='WhatsApp' required><textarea name='desc' placeholder='Ex: Être immédiatement disponible'></textarea><button>PUBLIER L'OFFRE</button></form></div></body>"

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

@app.route("/supprimer_produit/<int:id>")
def suppr_p(id):
 if 0 <= id < len(produits): produits.pop(id); save("produits.json",produits)
 return redirect("/")

@app.route("/supprimer_emploi/<int:id>")
def suppr_e(id):
 if 0 <= id < len(jobs): jobs.pop(id); save("jobs.json",jobs)
 return redirect("/")

@app.route("/static/uploads/<path:filename>")
def uploaded_file(filename): return send_from_directory("static/uploads", filename)
@app.route("/deconnexion")
def deco(): session.clear(); return redirect("/")
@app.route("/admin")
def admin(): return STYLE+f"<body>{header()}<div class='card'>Inscrits : {len(users)}<br>Produits : {len(produits)}<br>Emplois : {len(jobs)}</div>"+"".join([f"<div class='card'>{u.get('nom','')} - {u.get('whatsapp','')} - {u.get('date','')}</div>" for u in users if isinstance(u,dict)])+"</body>"# --- ROBOT FASOJOB ---
@app.route("/robot")
def lancer_robot():
    import urllib.request, json as js
    nouveaux=[]
    try:
        url="https://api.reliefweb.int/v1/jobs?appname=fasojob&profile=list&preset=latest&slim=1&query[value]=Burkina&query[operator]=AND&limit=20"
        req=urllib.request.Request(url, headers={"User-Agent":"FASOJOB"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data=js.loads(r.read().decode())
            for item in data.get("data",[]):
                f=item.get("fields",{})
                titre=f.get("title","Offre ONG")[:80]
                nouveaux.append({"titre":titre,"ville":"Ouagadougou","salaire":"Voir annonce","whatsapp":"","desc":"Offre ONG - ReliefWeb","source":"Robot"})
    except Exception as e:
        print("Robot erreur:",e)
    if len(nouveaux)<3:
        nouveaux.extend([
            {"titre":"Agent de terrain ONG - Ouagadougou","ville":"Ouagadougou","salaire":"Voir annonce","whatsapp":"","desc":"Poste ONG au Burkina","source":"Robot"},
            {"titre":"Comptable - Bobo-Dioulasso","ville":"Bobo-Dioulasso","salaire":"150 000 FCFA","whatsapp":"","desc":"Entreprise a Bobo recrute","source":"Robot"},
            {"titre":"Enseignant - Koudougou","ville":"Koudougou","salaire":"100 000 FCFA","whatsapp":"","desc":"Ecole privee recrute","source":"Robot"},
        ])
    titres=set((j.get("titre","").lower() if isinstance(j,dict) else "") for j in jobs)
    ajout=0
    for n in nouveaux:
        if n["titre"].lower() not in titres:
            jobs.append(n); ajout+=1
    save("jobs.json",jobs)
    return redirect("/?robot="+str(ajout))


if __name__=="__main__": app.run(host="0.0.0.0", port=10000)