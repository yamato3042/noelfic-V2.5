#Ce script contient les différentes actions des requêtes ajax
import util.bdd
from flask import request
def changenote():
    #Changement de note sur une fic
    print(request.form)
    for i in ["token", "note", "fic"]:
        if i not in request.form:
            return "ERR"
    
    conn = util.bdd.getConnexion()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id_users FROM users_shorts_tokens WHERE token = %s", (request.form["token"],))
    id_raw = cursor.fetchall()
    if len(id_raw) != 1:
        util.bdd.releaseConnexion(conn)
        return "ERR"
    
    #On change la note
    cursor.execute("""INSERT INTO note (fic, auteur, date, note)
                VALUES (%s, %s, NOW(), %s)
                ON CONFLICT (fic, auteur) DO UPDATE SET
                note = EXCLUDED.note,
                date = NOW()""",
                (request.form["fic"],id_raw[0][0],request.form["note"]))
    conn.commit()
    
    util.bdd.releaseConnexion(conn)
    return "OK"