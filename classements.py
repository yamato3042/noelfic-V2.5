from flask import render_template
import util.bdd
import util.general
from flask import abort
import psycopg2
import util.classements
import util.genre
import accounts.accounts

def classement_tout(page_):
    if not page_.isdigit():
        abort(404)
    page = int(page_)
    titre = f"Classement par ordre alphabétique - Page {page}"
    conn = util.bdd.getConnexion()
    cursor = conn.cursor()
    session = accounts.accounts.Session(conn)

    pages_raw = util.classements.getPages(page, cursor)
    if pages_raw == "err":
        util.bdd.releaseConnexion(conn)
        abort(404)
    nbPages = pages_raw["nbPages"]
    offset = pages_raw["offset"]

    
    #On chope la liste des fics par rapport au nom de l'offset
    cursor.execute("""SELECT fics.id, fics.titre, users.pseudo, fics.creation,fics.status, fics.collaboratif, fics.note FROM fics
                    LEFT JOIN users ON users.id = fics.auteur
                    ORDER BY fics.titre
                    LIMIT 20
                    OFFSET %s""", (offset,))
    fics_raw = cursor.fetchall()
    
    fics = util.classements.gen_fics(fics_raw)

    liste_pages = util.classements.gen_liste_pages(page, nbPages)

    util.bdd.releaseConnexion(conn)
    return render_template("rank.html", customCSS="rank.css", titre=titre, fics=fics, liste_pages=liste_pages, curPage = page, maxPage = nbPages, session=session)

def classement_popularite(page_):
    if not page_.isdigit():
        abort(404)
    page = int(page_)
    titre = f"Classement par popularité - Page {page}"
    conn = util.bdd.getConnexion()
    cursor = conn.cursor()
    session = accounts.accounts.Session(conn)

    pages_raw = util.classements.getPages(page, cursor)
    if pages_raw == "err":
        util.bdd.releaseConnexion(conn)
        abort(404)
    nbPages = pages_raw["nbPages"]
    offset = pages_raw["offset"]

    
    #On chope la liste des fics par rapport au nom de l'offset
    cursor.execute("""SELECT fics.id, fics.titre, users.pseudo, fics.creation,fics.status, fics.collaboratif, fics.note FROM fics
                    LEFT JOIN users ON users.id = fics.auteur
                    ORDER BY fics.vues DESC
                    LIMIT 20
                    OFFSET %s""", (offset,))
    fics_raw = cursor.fetchall()
    
    fics = util.classements.gen_fics(fics_raw)

    liste_pages = util.classements.gen_liste_pages(page, nbPages)

    util.bdd.releaseConnexion(conn)
    return render_template("rank.html", customCSS="rank.css", titre=titre, fics=fics, liste_pages=liste_pages, curPage = page, maxPage = nbPages, session=session)

def classement_date(page_):
    if not page_.isdigit():
        abort(404)
    page = int(page_)
    titre = f"Classement par popularité - Page {page}"
    conn = util.bdd.getConnexion()
    cursor = conn.cursor()
    session = accounts.accounts.Session(conn)

    pages_raw = util.classements.getPages(page, cursor)
    if pages_raw == "err":
        util.bdd.releaseConnexion(conn)
        abort(404)
    nbPages = pages_raw["nbPages"]
    offset = pages_raw["offset"]

    
    #On chope la liste des fics par rapport au nom de l'offset
    cursor.execute("""SELECT fics.id, fics.titre, users.pseudo, fics.creation,fics.status, fics.collaboratif, fics.note FROM fics
                    LEFT JOIN users ON users.id = fics.auteur
                    ORDER BY fics.creation DESC
                    LIMIT 20
                    OFFSET %s""", (offset,))
    fics_raw = cursor.fetchall()
    
    fics = util.classements.gen_fics(fics_raw)

    liste_pages = util.classements.gen_liste_pages(page, nbPages)

    util.bdd.releaseConnexion(conn)
    return render_template("rank.html", customCSS="rank.css", titre=titre, fics=fics, liste_pages=liste_pages, curPage = page, maxPage = nbPages, session=session)

def classement_note(page_):
    if not page_.isdigit():
        abort(404)
    page = int(page_)
    titre = f"Classement par popularité - Page {page}"
    conn = util.bdd.getConnexion()
    cursor = conn.cursor()
    session = accounts.accounts.Session(conn)

    pages_raw = util.classements.getPages(page, cursor)
    if pages_raw == "err":
        util.bdd.releaseConnexion(conn)
        abort(404)
    nbPages = pages_raw["nbPages"]
    offset = pages_raw["offset"]

    
    #On chope la liste des fics par rapport au nom de l'offset
    cursor.execute("""SELECT fics.id, fics.titre, users.pseudo, fics.creation,fics.status, fics.collaboratif, fics.note FROM fics
                    LEFT JOIN users ON users.id = fics.auteur
                    ORDER BY fics.note DESC
                    LIMIT 20
                    OFFSET %s""", (offset,))
    fics_raw = cursor.fetchall()
    
    fics = util.classements.gen_fics(fics_raw)

    liste_pages = util.classements.gen_liste_pages(page, nbPages)

    util.bdd.releaseConnexion(conn)
    return render_template("rank.html", customCSS="rank.css", titre=titre, fics=fics, liste_pages=liste_pages, curPage = page, maxPage = nbPages, session=session)



def classement_genre(genre_,page_):
    if not page_.isdigit():
        abort(404)
    page = int(page_)

    #Le truc des genres
    genreId = util.genre.getGenreId(genre_)
    if genreId == -1:
        abort(404)
    genre = util.genre.getGenre(genreId)

    titre = f"Classement par genre : {genre} - Page {page}"

    conn = util.bdd.getConnexion()
    cursor = conn.cursor()
    session = accounts.accounts.Session(conn)

    pages_raw = util.classements.getPages(page, cursor, "SELECT count(*) FROM fics RIGHT JOIN tags ON tags.fic = fics.id WHERE tag = " + str(genreId)) #TODO: oups la faille (impossible)
    if pages_raw == "err":
        util.bdd.releaseConnexion(conn)
        abort(404)
    nbPages = pages_raw["nbPages"]
    offset = pages_raw["offset"]


    #On chope la liste des fics par rapport au nom de l'offset
    cursor.execute("""SELECT fics.id, fics.titre, users.pseudo, fics.creation,fics.status, fics.collaboratif, fics.note FROM fics
                    LEFT JOIN tags ON fics.id = tags.fic
                    LEFT JOIN users ON users.id = fics.auteur
                    WHERE tags.tag = %s
                    ORDER BY fics.id DESC
                    LIMIT 20
                    OFFSET %s""", (genreId, offset,))
    fics_raw = cursor.fetchall()
    
    fics = util.classements.gen_fics(fics_raw)

    liste_pages = util.classements.gen_liste_pages(page, nbPages)

    util.bdd.releaseConnexion(conn)
    return render_template("rank.html", customCSS="rank.css", modeGenre=True, titre=titre, fics=fics, liste_pages=liste_pages, curPage = page, maxPage = nbPages, session=session)