#Ce code contient la page et la requête post pour se connecter sur le site
from flask import render_template, request, redirect, make_response
import util.bdd
import accounts.accounts
from accounts.ajax import getUserIdFromTempToken
import json
import util.ajax_util
def edit_fic_page():

    conn = util.bdd.getConnexion()
    session = accounts.accounts.Session(conn)
    
    if not session.logged:
        redirect("/")
    
    util.bdd.releaseConnexion(conn)
    return render_template("accounts/edit_fics.html", customCSS="edit_fics.css", session=session)

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
    conn.commit()
    
    util.bdd.releaseConnexion(conn)
    return "OK"