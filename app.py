from flask import Flask, render_template_string, request, redirect

app = Flask(__name__)

jobs = []

HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FasoJob - Emploi au Burkina</title>
<style>
body{font-family:Arial;margin:0;background:#f4f4f4}
header{background:#008751;color:white;padding:20px;text-align:center}
h1{margin:0}
.container{max-width:800px;margin:20px auto;padding:0 15px}
.card{background:white;padding:15px;border-radius:10px;margin-bottom:12px;box-shadow:0 2px 5px #ddd}
.btn{background:#008751;color:white;padding:10px 15px;border:none;border-radius:5px;text-decoration:none;display:inline-block}
input,textarea{width:100%;padding:10px;margin:5px 0;border:1px solid #ddd;border-radius:5px;box-sizing:border-box}
</style>
</head>
<body>
<header><h1>🇧🇫 FasoJob</h1><p>Trouve un emploi au Burkina Faso</p></header>
<div class="container">
<div class="card">
<h3>Publier une offre</h3>
<form method="post" action="/add">
<input name="titre" placeholder="Titre du poste ex: Chauffeur" required>
<input name="entreprise" placeholder="Entreprise" required>
<input name="lieu" placeholder="Lieu ex: Ouagadougou" required>
<textarea name="desc" placeholder="Description"></textarea>
<button class="btn" type="submit">Publier</button>
</form>
</div>
<h2>Offres disponibles ({{ jobs|length }})</h2>
{% for j in jobs %}
<div class="card"><b>{{ j.titre }}</b><br>{{ j.entreprise }} - {{ j.lieu }}<br>{{ j.desc }}</div>
{% else %}
<div class="card">Aucune offre pour le moment. Sois le premier à publier !</div>
{% endfor %}
</div>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML, jobs=jobs)

@app.route("/add", methods=["POST"])
def add():
    jobs.append({
        "titre": request.form.get("titre"),
        "entreprise": request.form.get("entreprise"),
        "lieu": request.form.get("lieu"),
        "desc": request.form.get("desc")
    })
    return redirect("/")

@app.route("/health")
def health():
    return "OK"

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)