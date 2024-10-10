from flask import render_template, abort
import util.bdd
import util.general
import util.classements
import datetime
from dateutil.relativedelta import relativedelta
import accounts.accounts

def profil(profil):
    #On commence par obtenir le numéro de la fic
    conn = util.bdd.getConnexion()
    cursor = conn.cursor()
    session = accounts.accounts.Session(conn)

    #On chope la liste des chapitres de la fic
    cursor.execute("""SELECT id,pseudo,description,comptes_autres_sites,inscription,derniere_conn,pp 
                    FROM users WHERE validee = true AND pseudo ILIKE %s""", (profil,))
    info_raw = cursor.fetchall()
    if len(info_raw) < 1:
        util.bdd.releaseConnexion(conn)
        abort(404)
    print(info_raw)
    id = info_raw[0][0]
    info = {
        "id": info_raw[0][0],
        "pseudo": info_raw[0][1],
        "description": util.formateur.formater(info_raw[0][2]),
        "derniere_conn": util.general.convDate(info_raw[0][5]),
    }

    #La date d'inscription
    diffdate_jours = (datetime.datetime.now() - info_raw[0][4]).days
    diffdate_années = relativedelta(datetime.datetime.now(), info_raw[0][4]).years
    info["inscription"] = diffdate_jours
    if(diffdate_années > 1):
        info["inscription_annees"] = diffdate_années

    #Comptes autres sites
    comptes_externes_raw = info_raw[0][3]
    if(len(comptes_externes_raw)) > 0:
        comptes_externes = []
        for i in comptes_externes_raw:
            #TODO ici on fait un traitement pour avoir l'icône de chaque site
            i["icon"] = util.general.autresSitesIcon(i["site"])
            comptes_externes.append(i)
        info["comptes_externes"] = comptes_externes
    #Photo de profil
    info["avatar"] = util.general.getAvatar(info["pseudo"], info_raw[0][6])

    #Les chapitres (du plus récent au plus vieux)
    cursor.execute("""SELECT fics.id, fics.titre, chapitres.num, chapitres.titre FROM chapitres 
        LEFT JOIN fics ON fics.id = chapitres.fic
        WHERE chapitres.auteur = %s
        ORDER BY chapitres.id DESC""", (id,))
    chapitres_raw = cursor.fetchall()

    chapitres = []
    for i in chapitres_raw:
        cur = {}
        cur["lien"] = util.general.getFicLink(i[0], i[1], i[2])
        cur["fic"] = i[1]
        cur["num"] = i[2]
        if i[3] != "":
            cur["titre_chapitre"] = i[3]
        chapitres.append(cur)

    info["nbChapitres"] = len(chapitres)

    editButton = False #Permet d'afficher le boutton pour modifier le profil
    if session.logged and session.id == info["id"]:
        editButton = True

    util.bdd.releaseConnexion(conn)
    return render_template("profil.html", titre=info["pseudo"], customCSS="profil.css", info=info, chapitres=chapitres, session=session, editButton=editButton)