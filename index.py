from flask import render_template
import util.bdd
import util.general
import re
import minichat
import accounts.accounts
def index():
    conn = util.bdd.getConnexion()
    cursor = conn.cursor()
    
    session = accounts.accounts.Session(conn)

    cursor.execute("""SELECT num, fic, fics.titre, chapitres.creation FROM chapitres 
                    LEFT JOIN fics ON fics.id = chapitres.fic
                    ORDER BY chapitres.id DESC LIMIT 10""")
    chapitres_raw = cursor.fetchall()
    #On transform ça en tableau
    chapitres = []
    for i in chapitres_raw:
        cur = {}
        cur["titre"] = i[2]
        cur["date"] = util.general.convDate(i[3])
        cur["num"] = i[0]
        cur["lien"] = util.general.getFicLink(i[1], i[2],i[0])
        chapitres.append(cur)

    #La penséedeo
    cursor.execute("""SELECT num, fic, fics.titre, chapitres.creation, users.pseudo, chapitres.content, fics.titre FROM chapitres 
                    LEFT JOIN fics ON fics.id = chapitres.fic
                    LEFT JOIN users ON chapitres.auteur = users.id
                    WHERE fic = 2447 ORDER BY num DESC LIMIT 1""")
    penseedeo_raw = cursor.fetchall()

    penseedeo = {}
    penseedeo["date"] = util.general.convDate(penseedeo_raw[0][3])
    penseedeo["auteur"] = penseedeo_raw[0][4]
    penseedeo["auteur_lien"] = util.general.getUserLink(penseedeo_raw[0][4])
    penseedeo["lien"] = util.general.getFicLink(penseedeo_raw[0][1], penseedeo_raw[0][6], penseedeo_raw[0][0])
    penseedeo["content"] = util.formateur.formater(penseedeo_raw[0][5])

    #Le chat
    minichat_messages = minichat.render_chat(cursor)

    util.bdd.releaseConnexion(conn)
    return render_template("index.html", session=session, customCSS="index.css", chapitres=chapitres, penseedeo=penseedeo, minichat_messages=minichat_messages)
