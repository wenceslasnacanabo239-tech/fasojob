# ROBOT FASOJOB - GitHub Actions
import requests, json
from datetime import datetime

def chercher():
    offres = []
    sites = [
        ("ReliefWeb", "https://reliefweb.int/jobs?search=Burkina%20Faso"),
        ("UNJobs", "https://unjobs.org/search/burkina-faso"),
        ("Emploi BF", "https://www.emploi.bf"),
        ("FasoJobs", "https://www.fasojobs.com"),
    ]
    print(f"Demarrage {datetime.now()}")
    for nom, url in sites:
        try:
            r = requests.get(url, timeout=20, headers={'User-Agent':'Mozilla/5.0'})
            print(f"{nom} : {r.status_code} OK - {len(r.text)} caracteres")
            offres.append({"site": nom, "url": url, "status": r.status_code})
        except Exception as e:
            print(f"{nom} : ERREUR {e}")
    with open("resultats.json","w",encoding="utf-8") as f:
        json.dump(offres,f,ensure_ascii=False,indent=2)
    print(f"Termine : {len(offres)} sites testes")
    return offres

if __name__ == "__main__":
    chercher()
  
