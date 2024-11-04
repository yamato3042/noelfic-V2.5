#Renvoie vers une fic aléatoire
from flask import redirect, request
import util.general
def random_fic():
    cursor: psycopg2.extensions.cursor = request.environ["conn"].cursor()

    cursor.execute("""
        SELECT id, titre
        FROM fics
        ORDER BY RANDOM()
        LIMIT 1;
    """)
    ret = cursor.fetchone()
    lien = util.general.getFicLink(ret[0], ret[1])

    return redirect(lien)
