from flask import render_template
import util.bdd
import util.general
from flask import abort
import psycopg2
import util.classements
import util.genre
from flask import request
import accounts.accounts

def recherche():
    search = request.args.get("search", None)
    page = 1
    if(request.args.get("page", None) != None):
        if request.args.get("page").isdigit():
            page = int(request.args.get("page"))

    titre = f"Recherche pour : {search} - Page {page}"
    conn = util.bdd.getConnexion()
    cursor = conn.cursor()
    session = accounts.accounts.Session(conn)

    pages_raw = util.classements.getPages(page, cursor, "SELECT count(*) FROM fics WHERE titre ILIKE %s", (f"%{search}%",))
    if pages_raw == "err":
        util.bdd.releaseConnexion(conn)
        abort(404)
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

    util.bdd.releaseConnexion(conn)
    return render_template("rank.html", customCSS="rank.css", titre=titre, fics=fics, liste_pages=liste_pages, curPage = page, maxPage = nbPages, recherche=search, session=session)