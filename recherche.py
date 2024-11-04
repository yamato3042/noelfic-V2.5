from flask import render_template
import util.general
from flask import abort
import psycopg2
import util.classements
import util.genre
from flask import request
import accounts.accounts
import re 
def sanitize_search(search_term: str) -> str:
    # Nettoie la chaîne de recherche
    # Garde uniquement les caractères alphanumériques et quelques caractères spéciaux
    return re.sub(r'[^a-zA-Z0-9\s\-_]', '', search_term)

def recherche():
    search = request.args.get("search", None)
    cursor: psycopg2.extensions.cursor = request.environ["conn"].cursor()
    
    page = 1
    if(request.args.get("page", None) != None):
        if request.args.get("page").isdigit():
            page = int(request.args.get("page"))

    #On check que la recherche soit valide
    search = sanitize_search(search)
        
    if len(search) > 100:
        search = search[:100]
        
    titre = f"Recherche pour : {search} - Page {page}"

    if search == '':
        err = "Recherche vide"
        return render_template("rank.html", titre=titre, customCSS="rank.css", err=err, session=request.environ["session"])
        
    if len(search) < 2:
        err = "Recherche trop courte (minimum deux caractères)"
        return render_template("rank.html", titre=titre, customCSS="rank.css", err=err, session=request.environ["session"])
    
    pages_raw = util.classements.getPages(page, cursor, "SELECT count(*) FROM fics WHERE titre ILIKE %s", (f"%{search}%",))
    if pages_raw == "err":
        err = "Aucun résultats"
        return render_template("rank.html", titre=titre, customCSS="rank.css", err=err, session=request.environ["session"])
    
    nbPages = pages_raw["nbPages"]
    offset = pages_raw["offset"]

    #On chope la liste des fics par rapport au nom de l'offset
    cursor.execute("""SELECT fics.id, fics.titre, users.pseudo, fics.creation,fics.status, fics.collaboratif, fics.note FROM fics
                    LEFT JOIN users ON users.id = fics.auteur
                    WHERE titre ILIKE %s
                    ORDER BY fics.titre
                    LIMIT 20
                    OFFSET %s""", (f"%{search}%", offset,))
    fics_raw = cursor.fetchall()
    
    fics = util.classements.gen_fics(fics_raw)

    liste_pages = util.classements.gen_liste_pages(page, nbPages)

    return render_template("rank.html", customCSS="rank.css", titre=titre, fics=fics, liste_pages=liste_pages, curPage = page, maxPage = nbPages, recherche=search, session=request.environ["session"])