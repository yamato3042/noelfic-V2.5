#Ce script contient les différentes actions des requêtes ajax
#TODO: à la limite faudrait utiliser un template ou un truc du style pour n'importer q'une fois toutes les requêtes d'ici dans le main genre un subsystem
import util.bdd
from flask import request
import psycopg2
import util.formateur

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
    print(request.form)
    for i in ["token", "content"]:
        if i not in request.form:
            return "ERR"
    
    conn = util.bdd.getConnexion()
    cursor = conn.cursor()
    #On récup le token
    userId = getUserIdFromTempToken(cursor, request.form["token"]);
    if userId == None:
        return "ERR"
    
    #TODO: formater le content
    formatedContent = util.formateur.formatEntrée(request.form["content"])
    
    
    #TODO: on met dans la base
    cursor.execute("INSERT INTO chat_messages (auteur, date, content) VALUES (%s, NOW(), %s)", (userId, formatedContent,))
    conn.commit()
    
    return "OK"