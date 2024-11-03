from flask import render_template
import util.bdd
import util.general
from flask import abort
import psycopg2
import util.classements
import util.genre
import accounts.accounts

def classement_tout(page_):
    def x(cursor: psycopg2.extensions.cursor, offset):
        cursor.execute("""SELECT fics.id, fics.titre, users.pseudo, fics.creation,fics.status, fics.collaboratif, fics.note FROM fics
                    LEFT JOIN users ON users.id = fics.auteur
                    ORDER BY fics.titre
                    LIMIT 20
                    OFFSET %s""", (offset,))
        return cursor.fetchall()
    
    titre = f"Classement par ordre alphabétique - Page {page_}"
    return util.classements.rank(x, page_, titre)

def classement_popularite(page_):
    def x(cursor: psycopg2.extensions.cursor, offset):
        cursor.execute("""SELECT fics.id, fics.titre, users.pseudo, fics.creation,fics.status, fics.collaboratif, fics.note FROM fics
                    LEFT JOIN users ON users.id = fics.auteur
                    ORDER BY fics.vues DESC
                    LIMIT 20
                    OFFSET %s""", (offset,))
        return cursor.fetchall()
    
    titre = f"Classement par popularité - Page {page_}"
    return util.classements.rank(x, page_, titre)

def classement_date(page_):
    def x(cursor: psycopg2.extensions.cursor, offset):
        cursor.execute("""SELECT fics.id, fics.titre, users.pseudo, fics.creation,fics.status, fics.collaboratif, fics.note FROM fics
                    LEFT JOIN users ON users.id = fics.auteur
                    ORDER BY fics.creation DESC
                    LIMIT 20
                    OFFSET %s""", (offset,))
        return cursor.fetchall()
    
    titre = f"Classement par date - Page {page_}"
    return util.classements.rank(x, page_, titre)

def classement_note(page_):
    def x(cursor: psycopg2.extensions.cursor, offset):
        cursor.execute("""SELECT fics.id, fics.titre, users.pseudo, fics.creation,fics.status, fics.collaboratif, fics.note FROM fics
                    LEFT JOIN users ON users.id = fics.auteur
                    ORDER BY fics.note DESC
                    LIMIT 20
                    OFFSET %s""", (offset,))
        return cursor.fetchall()
    
    titre = f"Classement par note - Page {page_}"
    return util.classements.rank(x, page_, titre)


def classement_genre(genre_,page_):
    genreId = util.genre.getGenreId(genre_)
    
    def x(cursor: psycopg2.extensions.cursor, offset):
        cursor.execute("""SELECT fics.id, fics.titre, users.pseudo, fics.creation,fics.status, fics.collaboratif, fics.note FROM fics
                    LEFT JOIN tags ON fics.id = tags.fic
                    LEFT JOIN users ON users.id = fics.auteur
                    WHERE tags.tag = %s
                    ORDER BY fics.id DESC
                    LIMIT 20
                    OFFSET %s""", (genreId, offset,))
        return cursor.fetchall()
    
    titre = f"Classement par genre : {util.genre.getGenre(genreId)} - Page {page_}"
    return util.classements.rank(x, page_, titre, "SELECT count(*) FROM fics RIGHT JOIN tags ON tags.fic = fics.id WHERE tag = %s", (str(genreId),), True)