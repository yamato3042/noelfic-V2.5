#Ce code contient la page et la requête post pour se connecter sur le site
from flask import render_template, request, redirect, make_response
import util.bdd
import accounts.accounts
from accounts.ajax import getUserIdFromTempToken
import json
import util.ajax_util
import util.genre
import util.general
import util.formateur
def edit_fic_page():

    conn = util.bdd.getConnexion()
    session = accounts.accounts.Session(conn)
    
    if not session.logged:
        return redirect("/")
        
    genres = util.genre.getGenresDic()
    status = util.general.getDicStatus()
    
    util.bdd.releaseConnexion(conn)
    return render_template("accounts/edit_fics.html", customCSS="edit_fics.css", session=session, genres=genres, status=status)

def getfics():
    util.ajax_util.checkFormsVal(["token"])
    
    conn = util.bdd.getConnexion()
    cursor = conn.cursor()
    #On récup le token
    userId = getUserIdFromTempToken(cursor, request.form["token"]);
    if userId == None:
        util.bdd.releaseConnexion(conn)
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
    
    util.bdd.releaseConnexion(conn)
    return json.dumps(ret)

def getcolaborateurs():
    util.ajax_util.checkFormsVal(["token", "fic"])
        
    fic = int(request.form["fic"])
    
    conn = util.bdd.getConnexion()
    cursor = conn.cursor()
    #On récup le token
    userId = getUserIdFromTempToken(cursor, request.form["token"]);
    if userId == None:
        util.bdd.releaseConnexion(conn)
        return "ERR"
    
    #On récupère l'auteur de la fic (on peux pas l'enlever donc faut le préciser)
    cursor.execute("""SELECT users.id FROM fics 
                    LEFT JOIN users ON users.id = fics.auteur
                    WHERE fics.id = 2447""", (fic,))
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
    
    util.bdd.releaseConnexion(conn)
    return json.dumps(ret)

def collaborateur_delete():
    util.ajax_util.checkFormsVal(["token", "fic", "toremove"])
        
    fic = int(request.form["fic"])
    toremove = int(request.form["toremove"])
    
    conn = util.bdd.getConnexion()
    cursor = conn.cursor()
    #On récup le token
    userId = getUserIdFromTempToken(cursor, request.form["token"]);
    if userId == None:
        util.bdd.releaseConnexion(conn)
        return "ERR"
    
    if toremove == userId:
        util.bdd.releaseConnexion(conn)
        return "ERRUSR"
    
    #On récupère le proprio pour pas pouvoir l'enlever
    cursor.execute("SELECT auteur FROM fics WHERE id = %s", (fic,))
    proprio = cursor.fetchone()[0]
    if toremove == proprio:
        util.bdd.releaseConnexion(conn)
        return "ERRUSR"
    
    #On vérifie que l'user soit bien collaborateur
    cursor.execute("SELECT * FROM collaborateur WHERE id_fics = %s AND id_users = %s", (fic, userId,))
    if len(cursor.fetchall()) != 1:
        util.bdd.releaseConnexion(conn)
        return "ERRUSR"
    
    #Tout est bon, on enlève de la BDD
    cursor.execute("DELETE FROM collaborateur WHERE id_fics = %s AND id_users = %s", (fic, toremove,))
    conn.commit()
    
    util.bdd.releaseConnexion(conn)
    return "OK"

def collaborateur_add():
    util.ajax_util.checkFormsVal(["token", "fic", "user"])
        
    fic = int(request.form["fic"])
    username = request.form["user"]
    
    conn = util.bdd.getConnexion()
    cursor = conn.cursor()
    #On récup le token
    userId = getUserIdFromTempToken(cursor, request.form["token"]);
    if userId == None:
        util.bdd.releaseConnexion(conn)
        return "ERR"
    
    #On vérifie que l'user soit bien collaborateur
    cursor.execute("SELECT * FROM collaborateur WHERE id_fics = %s AND id_users = %s", (fic, userId,))
    if len(cursor.fetchall()) != 1:
        util.bdd.releaseConnexion(conn)
        return "ERRUSR"
    
    #On regarde si l'user existe
    cursor.execute("SELECT id FROM users WHERE pseudo ILIKE %s", (username,))
    val = cursor.fetchall()
    if len(val) != 1:
        util.bdd.releaseConnexion(conn)
        return "ERR_INVALID_USER"
    username_id = val[0][0]
    #On regarde si il y est pas déjà dedans
    cursor.execute("SELECT FROM collaborateur WHERE id_fics = %s AND id_users = %s", (fic, username_id,))
    val = cursor.fetchall()
    if len(val) != 0:
        util.bdd.releaseConnexion(conn)
        return "ERR_ALREADY_USER"
    
    #On l'ajoute
    cursor.execute("INSERT INTO collaborateur VALUES (%s, %s)", (fic,username_id,))
    conn.commit()
    
    util.bdd.releaseConnexion(conn)
    return "OK" 


def personalisation_get():
    util.ajax_util.checkFormsVal(["token", "fic"])
        
    fic = int(request.form["fic"])
    
    conn = util.bdd.getConnexion()
    cursor = conn.cursor()
    #On récup le token
    userId = getUserIdFromTempToken(cursor, request.form["token"]);
    if userId == None:
        util.bdd.releaseConnexion(conn)
        return "ERR"
    
    #On vérifie que l'user soit bien collaborateur
    cursor.execute("SELECT * FROM collaborateur WHERE id_fics = %s AND id_users = %s", (fic, userId,))
    if len(cursor.fetchall()) != 1:
        util.bdd.releaseConnexion(conn)
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
    cursor.execute("SELECT tag FROM tags WHERE fic = 2447")
    for i in cursor.fetchall():
        ret["tags"].append(str(i[0]))
    
    util.bdd.releaseConnexion(conn)
    return json.dumps(ret)

def personalisation_set():
    util.ajax_util.checkFormsVal(["token", "fic", "val"])
        
    fic = int(request.form["fic"])
    
    conn = util.bdd.getConnexion()
    cursor = conn.cursor()
    #On récup le token
    userId = getUserIdFromTempToken(cursor, request.form["token"]);
    if userId == None:
        util.bdd.releaseConnexion(conn)
        return "ERR"
    
    #On vérifie que l'user soit bien collaborateur
    cursor.execute("SELECT * FROM collaborateur WHERE id_fics = %s AND id_users = %s", (fic, userId,))
    if len(cursor.fetchall()) != 1:
        util.bdd.releaseConnexion(conn)
        return "ERRUSR"
    
    val = json.loads(request.form["val"])
    
    titre = util.formateur.desinfecter(val["titre"])
    status = int(val["status"])
    lien = util.formateur.desinfecter(val["lien"])
    description = util.formateur.desinfecter(val["description"])
    #TODO: faire la requête pour changer les trucs, et aussi les tags là
    cursor.execute("UPDATE fics SET titre = %s, status = %s, lien = %s, description = %s WHERE id = %s", (titre, status, lien, description, fic,))
    
    #TODO: Les tags
    cursor.execute("DELETE FROM tags WHERE fic = %s", (fic,))
    
    #INSULTEZ MOI JE VOUS HAIS DÉJÀ
    for i in val["tags"]:
        cursor.execute("INSERT INTO tags VALUES (%s,%s)", (fic, int(i)))
    
    conn.commit()
    
    util.bdd.releaseConnexion(conn)
    return "OK"