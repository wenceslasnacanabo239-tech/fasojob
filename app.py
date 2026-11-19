from flask import Flask, request
app = Flask(__name__)

@app.route("/")
def accueil():
    return "<body style='background:#FFF8E7;font-family:Arial'><div style='background:#008751;color:white;padding:20px;text-align:center'><h1>FASOJOB</h1><p>Emplois au Burkina Faso</p></div><div style='padding:15px'><div style='background:white;border-left:5px solid #F7941D;padding:15px;margin:10px'><b>Vendeuse - Ouaga 2000</b><br>75 000 FCFA<br><button style='background:#008751;color:white;padding:10px'>Postuler</button></div><div style='background:white;border-left:5px solid #F7941D;padding:15px;margin:10px'><b>Chauffeur - Tampouy</b><br>90 000 FCFA<br><button style='background:#008751;color:white;padding:10px'>Postuler</button></div><div style='background:white;border-left:5px solid #F7941D;padding:15px;margin:10px'><b>Secretaire - Koulouba</b><br>120 000 FCFA<br><button style='background:#008751;color:white;padding:10px'>Postuler</button></div></div><center><a href='/inscription' style='background:#F7941D;color:white;padding:15px'>S INSCRIRE GRATUIT</a></center></div>"

@app.route("/inscription", methods=["GET", "POST"])
def inscription():
    if request.method == "POST":
        nom = request.form.get("nom")
        tel = request.form.get("tel")
        return f"<h1>Merci {nom} !</h1><p>Tu es inscrit avec le numero {tel}</p><br><a href='/'>Retour</a>"
    return "<h1>Inscription FasoJob</h1><form method='POST'><p>Nom : <input name='nom'></p><p>Telephone : <input name='tel'></p><button>S inscrire</button></form><br><a href='/'>Retour</a>"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(__import__("os").environ.get("PORT",5000)))
