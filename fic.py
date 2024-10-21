from flask import render_template, abort
import util.bdd
import util.general
import util.classements
import util.formateur
import accounts.accounts

def fic(fic_, chapitre_):
    #On commence par obtenir le numéro de la fic
    fic_dic = fic_.split("-")
    
    if len(fic_dic) < 1:
        abort(404)
    if not fic_dic[0].isdigit():
        abort(404)
    
    fic = int(fic_dic[0])
    
    #On chope le numéro du chapitre
    if not chapitre_.isdigit():
        abort(404)
    chapitre = int(chapitre_)

    conn = util.bdd.getConnexion()
    cursor = conn.cursor()
    session = accounts.accounts.Session(conn)

    #On chope la liste des chapitres de la fic
    cursor.execute("SELECT COUNT(*) FROM chapitres WHERE fic = %s", (fic,))
    nbChapitres = cursor.fetchall()[0][0]
    
    if chapitre > nbChapitres:
        abort(404)

    #On génère la liste des pages pour le curseur
    listChapitres = util.classements.gen_liste_pages(chapitre, nbChapitres)

    cursor.execute("""SELECT fics.titre, fics.status, fics.lien, fics.description, fics.note, chapitres.titre, chapitres.creation,users.pseudo, chapitres.content, chapitres.id FROM fics
                    LEFT JOIN chapitres ON chapitres.fic = fics.id
                    LEFT JOIN users ON users.id = chapitres.auteur
                    WHERE fics.id = %s AND chapitres.num = %s""", (fic,chapitre,))
    chapitre_raw = cursor.fetchall()
    if len(chapitre_raw) == 0:
        util.bdd.releaseConnexion(conn)
        abort(404)
    
    #On traite le chapitre
    chapitre_dic = {
        "fic_id" : fic,
        "fic_titre" : chapitre_raw[0][0], 
        "fic_status" : util.general.getStatus(chapitre_raw[0][1]),
        "fic_lien" : chapitre_raw[0][2],
        "fic_description" : chapitre_raw[0][3],
        "fic_note" : util.general.getNote(chapitre_raw[0][4]),
        "chapitre_titre" : chapitre_raw[0][5],
        "chapitre_date" : util.general.convDate(chapitre_raw[0][6]),
        "chapitre_auteur_lien" : util.general.getUserLink(chapitre_raw[0][7]),
        "chapitre_auteur" : chapitre_raw[0][7],
        "chapitre_content" : util.formateur.formater(chapitre_raw[0][8]),
        "chapitre_id": chapitre_raw[0][9],
        "chapitre": chapitre,
        "nbChapitres": nbChapitres
    }
    #On récupère la liste des auteurs
    cursor.execute("""SELECT pseudo FROM collaborateur 
                    LEFT JOIN users ON users.id = id_users
                    WHERE id_fics = %s""", (fic,))
    auteurs_raw = cursor.fetchall()
    chapitre_dic["fic_auteur"] = []
    for i in auteurs_raw:
        chapitre_dic["fic_auteur"].append([
            util.general.getUserLink(i[0]), #Pour le lien
            i[0] #Juste le pseudo
            ])
        
    #On récupère la note
    if session.logged:
        #On essaie de récuperer la note
        cursor.execute("SELECT note FROM note WHERE auteur = %s AND fic = %s", (session.id, fic))
        note_raw = cursor.fetchall()
        if len(note_raw) == 1:
            chapitre_dic["user_note"] = note_raw[0][0]
        else:
            chapitre_dic["user_note"] = 0
    
    #On récupère la liste des genres
    cursor.execute("SELECT tag FROM tags WHERE fic = %s", (fic,))
    chapitre_dic["fic_genres"] = []
    genres_raw = cursor.fetchall()
    for i in genres_raw:
        chapitre_dic["fic_genres"].append(util.genre.getGenre(i[0]))


    #On récupère les commentaires
    cursor.execute("""SELECT creation, content, pp, pseudo FROM comments 
                    LEFT JOIN users on comments.auteur = users.id
                    WHERE comments.chapitre = %s AND comments.deleted = false
                    ORDER BY comments.id DESC""", 
                    (chapitre_raw[0][9],))
    commentaires_raw = cursor.fetchall()
    commentaires = []
    for i in commentaires_raw:
        cur = {
            "date": util.general.convDate(i[0]),
            "content": util.formateur.formater(i[1]),
            "avatar": util.general.getAvatar(i[3], i[2]),
            "pseudo": i[3],
            "lien": util.general.getUserLink(i[3])
        }
        commentaires.append(cur)


    titre = f"{chapitre_dic["fic_titre"]} page {chapitre_dic["chapitre"]}"
    util.bdd.releaseConnexion(conn)
    return render_template("fic.html", titre=titre, customCSS="fic.css", ajout_sidebar=render_template("fic_nav.html", listeChapitres=listChapitres), chapitre=chapitre_dic, commentaires=commentaires, session=session)