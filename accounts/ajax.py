#Ce script contient les différentes actions des requêtes ajax
#TODO: à la limite faudrait utiliser un template ou un truc du style pour n'importer q'une fois toutes les requêtes d'ici dans le main genre un subsystem
import util.bdd
from flask import request
import psycopg2
import util.formateur
import json
import accounts.accounts
from werkzeug.security import check_password_hash, generate_password_hash

def getUserIdFromTempToken(cursor : psycopg2.extensions.cursor, token):
    cursor.execute("SELECT id_users FROM users_shorts_tokens WHERE token = %s", (request.form["token"],))
    id_raw = cursor.fetchall()
    if len(id_raw) != 1:
        util.bdd.releaseConnexion(conn)
        return None
    else:
        return id_raw[0][0]
    
def changenote():
    #Changement de note sur une fic
    for i in ["token", "note", "fic"]:
        if i not in request.form:
            return "ERR"
    
    conn = util.bdd.getConnexion()
    cursor = conn.cursor()
    
    userId = getUserIdFromTempToken(cursor, request.form["token"]);
    if userId == None:
        return "ERR"
    
    #On change la note
    cursor.execute("""INSERT INTO note (fic, auteur, date, note)
                VALUES (%s, %s, NOW(), %s)
                ON CONFLICT (fic, auteur) DO UPDATE SET
                note = EXCLUDED.note,
                date = NOW()""",
                (request.form["fic"],userId,request.form["note"]))
    conn.commit()
    
    util.bdd.releaseConnexion(conn)
    return "OK"

def minichat_send_msg():
    for i in ["token", "content"]:
        if i not in request.form:
            return "ERR"
    
    conn = util.bdd.getConnexion()
    cursor = conn.cursor()
    #On récup le token
    userId = getUserIdFromTempToken(cursor, request.form["token"]);
    if userId == None:
        return "ERR"
    
    #Formater le content
    formatedContent = util.formateur.formatEntrée(request.form["content"])
    
    
    #On met dans la base
    cursor.execute("INSERT INTO chat_messages (auteur, date, content) VALUES (%s, NOW(), %s)", (userId, formatedContent,))
    conn.commit()
    
    return "OK"


def chapitre_send_comment():
    for i in ["token", "content", "chapitre"]:
        if i not in request.form:
            return "ERR"
    
    print(request.form)
    
    conn = util.bdd.getConnexion()
    cursor = conn.cursor()
    #On récup le token
    userId = getUserIdFromTempToken(cursor, request.form["token"]);
    if userId == None:
        return "ERR"
    
    #Formater le content
    formatedContent = util.formateur.formatEntrée(request.form["content"])

    
    #On met dans la base
    cursor.execute("""INSERT INTO comments (auteur, chapitre, deleted, creation, content)
                    VALUES (%s,%s, false, NOW(), %s)""", (userId, request.form["chapitre"], request.form["content"]))
    conn.commit()
    
    return "OK"



def ajax_modif_profil():
    for i in ["token", "description", "email"]:
        if i not in request.form:
            return "ERR"
    site_externes = ["jvc", "onche", "avenoel", "2sucres"]
    for i in site_externes:
        if f"site_externe_{i}" not in request.form:
            return "ERR"
        
    conn = util.bdd.getConnexion()
    cursor = conn.cursor()
    
    userId = getUserIdFromTempToken(cursor, request.form["token"]);
    if userId == None:
        return "ERR"
    
    
    description = util.formateur.desinfecter(request.form["description"])
    email = util.formateur.desinfecter(request.form["email"])
    #Comptes autres sites
    comptes_autres_sites = []
    for i in site_externes:
        val = util.formateur.desinfecter(request.form[f"site_externe_{i}"])
        if val != "":
            comptes_autres_sites.append({"site": i, "pseudo": val})
    
    cursor.execute("""UPDATE users
                SET mail = %s, description = %s, comptes_autres_sites = %s
                WHERE id = %s""",
                (email, description, json.dumps(comptes_autres_sites), userId,))   
    conn.commit() 
    
    print("ok")
    return "OK"

def ajax_modif_mdp():
    for i in ["token", "ancien_mdp", "nouveau_mdp"]:
        if i not in request.form:
            return "ERR"        
    conn = util.bdd.getConnexion()
    cursor = conn.cursor()
    
    userId = getUserIdFromTempToken(cursor, request.form["token"]);
    if userId == None:
        return "ERR"
    
    #On compare le mot de passe
    cursor.execute("SELECT mdp FROM users WHERE id = %s", (userId,))
    val = cursor.fetchall()
    
    if not check_password_hash(val[0][0], request.form["ancien_mdp"]+accounts.accounts.PASSWORD_SALT):
        return "ERRMDP"
    
    #Changer le mdp dans la bdd
    #Génération du hash
    new_mdp = generate_password_hash(request.form["nouveau_mdp"] + accounts.accounts.PASSWORD_SALT)
    #Insertion dans la BDD
    cursor.execute("UPDATE users SET mdp = %s WHERE id = %s", (new_mdp, userId))
    #Supression de tous les tokens pour cette utilisateur
    cursor.execute("DELETE FROM users_token WHERE id_users = %s", (userId,))
    cursor.execute("DELETE FROM users_shorts_tokens WHERE id_users = %s", (userId,))
    
    conn.commit()
    util.bdd.releaseConnexion(conn)

    return "OK"