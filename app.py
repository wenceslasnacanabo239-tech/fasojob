from flask import Flask, request, redirect, render_template_string, jsonify, Response
import json, os, io
from PIL import Image, ImageDraw, ImageFont
app = Flask(__name__)
FICHIER="jobs.json"
def charger():
 if os.path.exists(FICHIER):
  try:
   with open(FICHIER,"r",encoding="utf-8") as f: return json.load(f)
  except: pass
 return [
 {"titre":"Vendeuse","ville":"Ouaga 2000","salaire":"75 000 FCFA","whatsapp":"","desc":""},
 {"titre":"Chauffeur","ville":"Tampouy","salaire":"90 000 FCFA","whatsapp":"","desc":""},
 {"titre":"Secretaire","ville":"Koulouba","salaire":"120 000 FCFA","whatsapp":"","desc":""},
 ]
def sauver(jobs):
 with open(FICHIER,"w",encoding="utf-8") as f: json.dump(jobs,f,ensure_ascii=False)
jobs=charger()
ACCUEIL = """
<html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="manifest" href="/manifest.json"><meta name="theme-color" content="#008751"><meta name="apple-mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-title" content="FASOJOB"><link rel="apple-touch-icon" href="/icon.png">
<style>body{font-family:Arial;background:#FFF8E7;margin:0} .h{background:#008751;color:white;text-align:center;padding:20px} .c{background:white;margin:10px;padding:12px;border-left:5px solid #F7941D} .b{background:#008751;color:white;padding:8px 12px;text-decoration:none;display:inline-block;border-radius:5px} .o{background:#F7941D;color:white;padding:12px 20px;text-decoration:none;display:inline-block;border-radius:5px;font-weight:bold} .ct{text-align:center;margin:20px} .s{width:80%;padding:12px;border:1px solid #ccc;border-radius:5px} .d{color:red;font-size:12px;text-decoration:none;margin-left:10px} #inst{display:none;background:#111;color:white;padding:12px;text-align:center}</style></head>
<body><div id="inst">📱 Installer FASOJOB sur ton telephone <button onclick="installer()" style="background:#F7941D;color:white;border:none;padding:8px 12px;border-radius:5px">INSTALLER</button></div>
<div class="h"><h1>FASOJOB</h1><p>Emplois au Burkina Faso</p></div>
<div class="ct"><a class="o" href="/publier">+ PUBLIER UNE OFFRE GRATUIT</a></div>
<div class="ct"><form method="GET" action="/"><input class="s" name="q" value="{{q}}" placeholder="Rechercher: Chauffeur, Ouaga..."><br><br><button class="b" type="submit">Rechercher</button></form></div>
{% for idx,j in jobs %}<div class="c"><b>{{j.titre}} - {{j.ville}}</b><br>{{j.salaire}}<br>{% if j.desc %}<p>{{j.desc}}</p>{% endif %}
{% if j.whatsapp %}<a class="b" href="https://wa.me/{{j.whatsapp}}">Postuler sur WhatsApp</a>{% else %}<a class="b" href="#">Postuler</a>{% endif %}
<a class="d" href="/supprimer/{{idx}}" onclick="return confirm('Supprimer cette offre ?')">Supprimer</a></div>{% endfor %}
{% if not jobs %}<p style="text-align:center">Aucune offre trouvee.</p>{% endif %}
<div class="ct"><a class="o" href="/publier">S'INSCRIRE GRATUIT</a></div>
<script>let p=null;window.addEventListener('beforeinstallprompt',e=>{e.preventDefault();p=e;document.getElementById('inst').style.display='block'});function installer(){if(p){p.prompt()}};if('serviceWorker' in navigator){navigator.serviceWorker.register('/sw.js')}</script></body></html>
"""
PUBLIER = """
<html><head><meta name="viewport" content="width=device-width, initial-scale=1"><link rel="manifest" href="/manifest.json"><meta name="theme-color" content="#008751">
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
 q=request.args.get("q","").lower()
 liste=list(enumerate(jobs)); liste=list(reversed(liste))
 if q: liste=[(i,j) for i,j in liste if q in j["titre"].lower() or q in j["ville"].lower() or q in j["desc"].lower()]
 return render_template_string(ACCUEIL, jobs=liste, q=request.args.get("q",""))
@app.route("/publier", methods=["GET","POST"])
def publier():
 if request.method=="POST":
  jobs.append({"titre":request.form["titre"],"ville":request.form["ville"],"salaire":request.form["salaire"],"whatsapp":request.form["whatsapp"].replace(" ","").replace("+",""),"desc":request.form["desc"]}); sauver(jobs); return redirect("/")
 return render_template_string(PUBLIER)
@app.route("/supprimer/<int:id>")
def supprimer(id):
 if 0 <= id < len(jobs): jobs.pop(id); sauver(jobs)
 return redirect("/")
@app.route("/manifest.json")
def manifest():
 return jsonify({"name":"FASOJOB","short_name":"FASOJOB","start_url":"/","display":"standalone","background_color":"#FFF8E7","theme_color":"#008751","icons":[{"src":"/icon.png?v=2","sizes":"512x512","type":"image/png","purpose":"any"}]})
@app.route("/sw.js")
def sw():
 return Response("self.addEventListener('fetch',e=>{e.respondWith(fetch(e.request).catch(()=>caches.match(e.request)))})", mimetype="application/javascript")
@app.route("/icon.png")
def icon():
 img=Image.new("RGB",(512,512),"#008751"); d=ImageDraw.Draw(img)
 try: f1=ImageFont.truetype("DejaVuSans-Bold.ttf",150); f2=ImageFont.truetype("DejaVuSans-Bold.ttf",62); f3=ImageFont.truetype("DejaVuSans-Bold.ttf",38)
 except: f1=ImageFont.load_default(); f2=f1; f3=f1
 d.rectangle([15,15,497,497],outline="#F7941D",width=12)
 d.text((512/2,180),"F",font=f1,fill="white",anchor="mm")
 d.text((512/2,330),"FASOJOB",font=f2,fill="white",anchor="mm")
 d.text((512/2,400),"BURKINA",font=f3,fill="#F7941D",anchor="mm")
 buf=io.BytesIO(); img.save(buf,format="PNG"); buf.seek(0); return Response(buf.getvalue(), mimetype="image/png")
if __name__=="__main__":
 app.run(host="0.0.0.0", port=10000)