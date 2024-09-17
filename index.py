from flask import render_template
import util.bdd
import util.general
import re
import minichat
def index():
    conn = util.bdd.getConnexion()
    cursor = conn.cursor()

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

    #TODO: la penséedeo
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
    penseedeo["content"] = penseedeo_raw[0][5]

    #TODO: faire une fonction pour formater les chapitres
    print(penseedeo["content"])
    penseedeo["content"] = penseedeo["content"].replace("\n", "<br/>")
    #Conversion des liens youtube
    regex_youtube = r'(https?://(?:www\.)?youtube\.com/watch\?v=[a-zA-Z0-9_-]+)'
    liens_youtube = re.findall(regex_youtube, penseedeo["content"])
    for i in liens_youtube:
        print(i)
        youtube_ifram = '<iframe style="display:block; margin:0 auto;" width="560" height="315" src="https://www.youtube.com/embed/{lien}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>'
        lien = i.split("v=")[-1]
        penseedeo["content"] = penseedeo["content"].replace(i, youtube_ifram.replace("{lien}", lien))
    
    #Les liens en dehors de iframe
    
    #TODO: le chat
    minichat_messages = minichat.render_chat(cursor)

    conn.close()

    return render_template("index.html", customCSS="index.css", chapitres=chapitres, penseedeo=penseedeo, minichat_messages=minichat_messages)
