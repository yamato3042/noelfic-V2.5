#Renvoie vers une fic aléatoire
from flask import redirect
import util.bdd
import util.general
def random_fic():
    conn = util.bdd.getConnexion()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, titre
        FROM fics
        ORDER BY RANDOM()
        LIMIT 1;
    """)
    ret = cursor.fetchone()
    lien = util.general.getFicLink(ret[0], ret[1])

    conn.close()
    return redirect(lien)
