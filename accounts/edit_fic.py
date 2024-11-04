#Ce code contient la page et la requête post pour se connecter sur le site
from flask import render_template, request, redirect, make_response
import accounts.accounts
from accounts.ajax import getUserIdFromTempToken
import json
import util.ajax_util
import util.genre
import util.general
import util.formateur
def edit_fic_page():
    cursor: psycopg2.extensions.cursor = request.environ["conn"].cursor()
    session: accounts.accounts.Session = request.environ["session"]
    
    if not session.logged:
        return redirect("/")
        
    genres = util.genre.getGenresDic()
    status = util.general.getDicStatus()

    return render_template("accounts/edit_fics.html", customCSS="edit_fics.css", session=session, genres=genres, status=status)

def getfics():
    util.ajax_util.checkFormsVal(["token"])
    
    cursor: psycopg2.extensions.cursor = request.environ["conn"].cursor()
    #On récup le token
    userId = getUserIdFromTempToken(cursor, request.form["token"]);
    if userId == None:
        return "ERR"
    
    cursor.execute("""SELECT id_fics, titre FROM collaborateur 
                LEFT JOIN fics ON fics.id = collaborateur.id_fics
                WHERE id_users = %s""", (userId,))
    val = cursor.fetchall()
    ret = []
    for i in val:
        cur = {
            "id": i[0],
            "titre": i[1]
        }
        ret.append(cur)

    return json.dumps(ret)

def getcolaborateurs():
    util.ajax_util.checkFormsVal(["token", "fic"])
        
    fic = int(request.form["fic"])
    
    cursor: psycopg2.extensions.cursor = request.environ["conn"].cursor()
    #On récup le token
    userId = getUserIdFromTempToken(cursor, request.form["token"]);
    if userId == None:
        return "ERR"
    
    #On récupère l'auteur de la fic (on peux pas l'enlever donc faut le préciser)
    cursor.execute("""SELECT users.id FROM fics 
                    LEFT JOIN users ON users.id = fics.auteur
                    WHERE fics.id = %s""", (fic,))
    proprio = cursor.fetchone()[0]
    #On récupère la liste des collaborateurs
    cursor.execute("""SELECT id, pseudo FROM collaborateur 
                LEFT JOIN users ON users.id = id_users
                WHERE id_fics = %s""", (fic,))
    val = cursor.fetchall()
    
    ret =  []
    for i in val:
        cur = {
            "id": i[0],
            "name": i[1]
        }
        if cur["id"] == proprio:
            cur["type"] = "proprio"
        elif cur["id"] == userId:
            cur["type"] = "current"
        else:
            cur["type"] = "writer"
        ret.append(cur)
    
    return json.dumps(ret)

def collaborateur_delete():
    util.ajax_util.checkFormsVal(["token", "fic", "toremove"])
        
    fic = int(request.form["fic"])
    toremove = int(request.form["toremove"])
    
    cursor: psycopg2.extensions.cursor = request.environ["conn"].cursor()
    #On récup le token
    userId = getUserIdFromTempToken(cursor, request.form["token"]);
    if userId == None:
        return "ERR"
    
    if toremove == userId:
        return "ERRUSR"
    
    #On récupère le proprio pour pas pouvoir l'enlever
    cursor.execute("SELECT auteur FROM fics WHERE id = %s", (fic,))
    proprio = cursor.fetchone()[0]
    if toremove == proprio:
        return "ERRUSR"
    
    #On vérifie que l'user soit bien collaborateur
    cursor.execute("SELECT * FROM collaborateur WHERE id_fics = %s AND id_users = %s", (fic, userId,))
    if len(cursor.fetchall()) != 1:
        return "ERRUSR"
    
    #Tout est bon, on enlève de la BDD
    cursor.execute("DELETE FROM collaborateur WHERE id_fics = %s AND id_users = %s", (fic, toremove,))
    request.environ["conn"].commit()
    
    return "OK"

def collaborateur_add():
    util.ajax_util.checkFormsVal(["token", "fic", "user"])
        
    fic = int(request.form["fic"])
    username = request.form["user"]
    
    cursor: psycopg2.extensions.cursor = request.environ["conn"].cursor()
    #On récup le token
    userId = getUserIdFromTempToken(cursor, request.form["token"]);
    if userId == None:
        return "ERR"
    
    #On vérifie que l'user soit bien collaborateur
    cursor.execute("SELECT * FROM collaborateur WHERE id_fics = %s AND id_users = %s", (fic, userId,))
    if len(cursor.fetchall()) != 1:
        return "ERRUSR"
    
    #On regarde si l'user existe
    cursor.execute("SELECT id FROM users WHERE pseudo ILIKE %s", (username,))
    val = cursor.fetchall()
    if len(val) != 1:
        return "ERR_INVALID_USER"
    username_id = val[0][0]
    #On regarde si il y est pas déjà dedans
    cursor.execute("SELECT FROM collaborateur WHERE id_fics = %s AND id_users = %s", (fic, username_id,))
    val = cursor.fetchall()
    if len(val) != 0:
        return "ERR_ALREADY_USER"
    
    #On l'ajoute
    cursor.execute("INSERT INTO collaborateur VALUES (%s, %s)", (fic,username_id,))
    request.environ["conn"].commit()
    
    return "OK" 


def personalisation_get():
    util.ajax_util.checkFormsVal(["token", "fic"])
        
    fic = int(request.form["fic"])
    
    cursor: psycopg2.extensions.cursor = request.environ["conn"].cursor()
    #On récup le token
    userId = getUserIdFromTempToken(cursor, request.form["token"]);
    if userId == None:
        return "ERR"
    
    #On vérifie que l'user soit bien collaborateur
    cursor.execute("SELECT * FROM collaborateur WHERE id_fics = %s AND id_users = %s", (fic, userId,))
    if len(cursor.fetchall()) != 1:
        return "ERRUSR"
    
    #On récupère les valeurs de base
    cursor.execute("SELECT titre, status, COALESCE(lien, '') as lien, COALESCE(description, '') as description FROM fics WHERE id = %s", (fic,))
    val = cursor.fetchone()
    
    ret = {
        "titre": val[0],
        "status": val[1],
        "lien": val[2],
        "description": val[3],
        "tags": []
    }
    
    #On récupère les tags
    cursor.execute("SELECT tag FROM tags WHERE fic = %s", (fic,))
    for i in cursor.fetchall():
        ret["tags"].append(str(i[0]))
        
    #On récupère le bordel des chapitres
    cursor.execute("SELECT COALESCE(MAX(num), 0) FROM chapitres WHERE fic = %s", (fic,))
    ret["nbchapitres"] = cursor.fetchone()[0]
    
    return json.dumps(ret)

def personalisation_set():
    util.ajax_util.checkFormsVal(["token", "fic", "val"])
        
    fic = int(request.form["fic"])
    
    cursor: psycopg2.extensions.cursor = request.environ["conn"].cursor()
    #On récup le token
    userId = getUserIdFromTempToken(cursor, request.form["token"]);
    if userId == None:
        return "ERR"
    
    #On vérifie que l'user soit bien collaborateur
    cursor.execute("SELECT * FROM collaborateur WHERE id_fics = %s AND id_users = %s", (fic, userId,))
    if len(cursor.fetchall()) != 1:
        return "ERRUSR"
    
    val = json.loads(request.form["val"])
    
    titre = util.formateur.desinfecter(val["titre"])
    status = int(val["status"])
    lien = util.formateur.desinfecter(val["lien"])
    description = util.formateur.formatEntrée(val["description"])
    #Faire la requête pour changer les trucs, et aussi les tags là
    cursor.execute("UPDATE fics SET titre = %s, status = %s, lien = %s, description = %s WHERE id = %s", (titre, status, lien, description, fic,))
    
    #Les tags
    cursor.execute("DELETE FROM tags WHERE fic = %s", (fic,))
    
    #INSULTEZ MOI JE VOUS HAIS DÉJÀ
    for i in val["tags"]:
        cursor.execute("INSERT INTO tags VALUES (%s,%s)", (fic, int(i)))
    
    request.environ["conn"].commit()
    
    return "OK"


def chapitre_get():
    util.ajax_util.checkFormsVal(["token", "fic", "chapitre"])
        
    fic = int(request.form["fic"])
    chapitre = int(request.form["chapitre"])
    
    cursor: psycopg2.extensions.cursor = request.environ["conn"].cursor()
    #On récup le token
    userId = getUserIdFromTempToken(cursor, request.form["token"]);
    if userId == None:
        return "ERR"
    
    #On vérifie que l'user soit bien collaborateur
    cursor.execute("SELECT * FROM collaborateur WHERE id_fics = %s AND id_users = %s", (fic, userId,))
    if len(cursor.fetchall()) != 1:
        return "ERRUSR"
    
    #On récupère les trucs
    cursor.execute("SELECT titre, auteur, content FROM chapitres WHERE fic = %s AND num = %s", (fic, chapitre))
    val = cursor.fetchone()
    
    ret = {
        "titre": val[0],
        "auteur": val[1],
        "content": util.formateur.formatPourEspaceEcriture(val[2]) #Y'a des trucs qui marchent pas côté quill faut regarder ça
    }
    return json.dumps(ret)

def chapitre_save():
    util.ajax_util.checkFormsVal(["token", "fic", "chapitre", "titre", "auteur", "content"])
        
    fic = int(request.form["fic"])
    chapitre = int(request.form["chapitre"])
    titre = request.form["titre"]
    auteur = int(request.form["auteur"])
    content = util.formateur.formatEntrée(request.form["content"])
    
    cursor: psycopg2.extensions.cursor = request.environ["conn"].cursor()
    #On récup le token
    userId = getUserIdFromTempToken(cursor, request.form["token"]);
    if userId == None:
        return "ERR"
    
    #On vérifie que l'user soit bien collaborateur
    cursor.execute("SELECT * FROM collaborateur WHERE id_fics = %s AND id_users = %s", (fic, userId,))
    if len(cursor.fetchall()) != 1:
        return "ERRUSR"
    
    #On change les valeurs
    cursor.execute("UPDATE chapitres SET titre = %s, auteur = %s, content = %s, modification = NOW() WHERE fic = %s AND num = %s", (titre, auteur, content, fic, chapitre))
    
    #On met à jour la fic et le chapitre au niveau date de modif
    cursor.execute("UPDATE fics SET modification = NOW() WHERE id = %s", (fic,))
    cursor.execute("UPDATE chapitres SET modification=NOW() where fic = %s AND num = %s", (fic, chapitre,))
    
    request.environ["conn"].commit()
    return "OK"

def chapitre_create():
    util.ajax_util.checkFormsVal(["token", "fic", "titre", "auteur", "content"])
        
    fic = int(request.form["fic"])
    titre = request.form["titre"]
    auteur = int(request.form["auteur"])
    content = util.formateur.formatEntrée(request.form["content"])
    
    cursor: psycopg2.extensions.cursor = request.environ["conn"].cursor()
    #On récup le token
    userId = getUserIdFromTempToken(cursor, request.form["token"]);
    if userId == None:
        return "ERR"
    
    #On vérifie que l'user soit bien collaborateur
    cursor.execute("SELECT * FROM collaborateur WHERE id_fics = %s AND id_users = %s", (fic, userId,))
    if len(cursor.fetchall()) != 1:
        return "ERRUSR"
    
    #On crée un nouveau chapitre et on return le num
    cursor.execute("""INSERT INTO chapitres (fic, titre, num, auteur, content, creation, modification, vues)
                VALUES (%s, %s, (SELECT COALESCE(MAX(num), 0)+1 from chapitres WHERE fic = %s), %s, %s, NOW(), NOW(), 0)
                RETURNING num""", (fic, titre, fic, auteur, content))
    num = cursor.fetchone()[0]
    request.environ["conn"].commit()
    
    ret = {"num": num}
    
    return json.dumps(ret)


def fic_create():
    util.ajax_util.checkFormsVal(["token", "title"])
        
    titre = request.form["title"].strip()
    
    if(titre == ""): 
        return "ERR"
    
    cursor: psycopg2.extensions.cursor = request.environ["conn"].cursor()
    #On récup le token
    userId = getUserIdFromTempToken(cursor, request.form["token"]);
    if userId == None:
        return "ERR"
    
    #On vérifie que le titre ne soit pas déjà pris
    cursor.execute("SELECT id from fics WHERE titre ILIKE %s", (titre,))
    if len(cursor.fetchall()) > 0:
        return "ERR_ALREADY_EXIST"
    
    #On crée la fic
    cursor.execute("INSERT INTO fics (titre, status, creation, modification, auteur) VALUES (%s, 1, NOW(), NOW(), %s) RETURNING id", (titre, userId,))
    fic_id = cursor.fetchone()[0] #Normalement on a un id qu'on peux retourner dcp
    
    #On ajoute l'utilisateur en collaborateur
    cursor.execute("INSERT INTO collaborateur VALUES (%s, %s)", (fic_id, userId))
    
    
    
    request.environ["conn"].commit()
    return str(fic_id)