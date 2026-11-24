@app.route("/robot")
def robot():
    try:
        import requests
        # Cherche les VRAIS emplois au Burkina sur ReliefWeb
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
                "desc": (org_nom + " - Voir l'annonce sur ReliefWeb : " + lien)[:500],
                "source": "ReliefWeb"
            })
    except Exception as e:
        nouveaux = []
    
    # On n'ajoute QUE les vrais emplois, jamais de faux
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
        return f"Aucune nouvelle vraie offre pour le moment. Le robot a vérifié ReliefWeb. Réessaie plus tard. Total offres : {len(JOBS)}"
    return f"Robot OK ! {ajoutes} vraies offres ajoutées depuis ReliefWeb. Total : {len(JOBS)}"