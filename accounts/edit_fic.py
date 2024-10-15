#Ce code contient la page et la requête post pour se connecter sur le site
from flask import render_template, request, redirect, make_response
import util.bdd
import accounts.accounts
from accounts.ajax import getUserIdFromTempToken
import json
def edit_fic_page():

    conn = util.bdd.getConnexion()
    session = accounts.accounts.Session(conn)
    
    if not session.logged:
        redirect("/")
    
    util.bdd.releaseConnexion(conn)
    return render_template("accounts/edit_fics.html", customCSS="edit_fics.css", session=session)

def getfics():
    for i in ["token"]:
        if i not in request.form:
            return "ERR"
    
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