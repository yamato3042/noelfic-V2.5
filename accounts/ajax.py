#Ce script contient les différentes actions des requêtes ajax
#TODO: à la limite faudrait utiliser un template ou un truc du style pour n'importer q'une fois toutes les requêtes d'ici dans le main genre un subsystem
from flask import request
import psycopg2
import util.formateur
import json
import accounts.accounts
from werkzeug.security import check_password_hash, generate_password_hash
from PIL import Image
import util.general
import io
import param

def getUserIdFromTempToken(cursor : psycopg2.extensions.cursor, token):
    cursor.execute("SELECT id_users FROM users_shorts_tokens WHERE token = %s", (request.form["token"],))
    id_raw = cursor.fetchall()
    if len(id_raw) != 1:
        return None
    else:
        return id_raw[0][0]
    
def changenote():
    #Changement de note sur une fic
    for i in ["token", "note", "fic"]:
        if i not in request.form:
            return "ERR"
    
    cursor: psycopg2.extensions.cursor = request.environ["conn"].cursor()
    
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
    request.environ["conn"].commit()
    
    return "OK"

def minichat_send_msg():
    for i in ["token", "content"]:
        if i not in request.form:
            return "ERR"
    
    cursor: psycopg2.extensions.cursor = request.environ["conn"].cursor()
    #On récup le token
    userId = getUserIdFromTempToken(cursor, request.form["token"]);
    if userId == None:
        return "ERR"
    
    #Formater le content
    formatedContent = util.formateur.formatEntrée(request.form["content"])
    
    
    #On met dans la base
    cursor.execute("INSERT INTO chat_messages (auteur, date, content) VALUES (%s, NOW(), %s)", (userId, formatedContent,))
    request.environ["conn"].commit()
    
    return "OK"


def chapitre_send_comment():
    for i in ["token", "content", "chapitre"]:
        if i not in request.form:
            return "ERR"
    
    
    cursor: psycopg2.extensions.cursor = request.environ["conn"].cursor()
    #On récup le token
    userId = getUserIdFromTempToken(cursor, request.form["token"]);
    if userId == None:
        return "ERR"
    
    #Formater le content
    formatedContent = util.formateur.formatEntrée(request.form["content"])

    
    #On met dans la base
    cursor.execute("""INSERT INTO comments (auteur, chapitre, deleted, creation, content)
                    VALUES (%s,%s, false, NOW(), %s)""", (userId, request.form["chapitre"], request.form["content"]))
    request.environ["conn"].commit()

    return "OK"



def ajax_modif_profil():
    for i in ["token", "description", "email"]:
        if i not in request.form:
            return "ERR"
    site_externes = ["jvc", "onche", "avenoel", "2sucres"]
    for i in site_externes:
        if f"site_externe_{i}" not in request.form:
            return "ERR"
        
    cursor: psycopg2.extensions.cursor = request.environ["conn"].cursor()
    
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
    
    
    #La pp
    if "pp" in request.files:
        file = request.files["pp"]
        
        if file.mimetype not in ['image/jpeg', 'image/png']:
            return "ERRIMG_MIME"
        try:
            # Ouvre l'image en utilisant PIL
            image = Image.open(io.BytesIO(file.read()))
        except Exception as e:
            # Renvoie une erreur si l'image ne peut pas être ouverte
            return "ERRIMG"
        
        resized_image = image.resize((144, 144))
        resized_image = resized_image.convert("RGB")
        #On récupère le pseudo
        cursor.execute("UPDATE users SET pp = true WHERE id = %s RETURNING pseudo", (userId,))
        val_pseudo = cursor.fetchone()
        #On crée le nom du fichier
        nom = util.general.getAvatar(val_pseudo[0], True)[1:]
        #On enregistre l'image
        resized_image.save(nom)
        
    request.environ["conn"].commit()
    return "OK"

def ajax_modif_mdp():
    for i in ["token", "ancien_mdp", "nouveau_mdp"]:
        if i not in request.form:
            return "ERR"        
    cursor: psycopg2.extensions.cursor = request.environ["conn"].cursor()
    
    userId = getUserIdFromTempToken(cursor, request.form["token"]);
    if userId == None:
        return "ERR"
    
    #On compare le mot de passe
    cursor.execute("SELECT mdp FROM users WHERE id = %s", (userId,))
    val = cursor.fetchall()
    
    if not check_password_hash(val[0][0], request.form["ancien_mdp"]+ param.PASSWORD_SALT):
        return "ERRMDP"
    
    #Changer le mdp dans la bdd
    #Génération du hash
    new_mdp = generate_password_hash(request.form["nouveau_mdp"] + param.PASSWORD_SALT)
    #Insertion dans la BDD
    cursor.execute("UPDATE users SET mdp = %s WHERE id = %s", (new_mdp, userId))
    #Supression de tous les tokens pour cette utilisateur
    cursor.execute("DELETE FROM users_token WHERE id_users = %s", (userId,))
    cursor.execute("DELETE FROM users_shorts_tokens WHERE id_users = %s", (userId,))    
    
    request.environ["conn"].commit()

    return "OK"