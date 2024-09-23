#Ce fichier vas contenir la page et la requête post permettant de s'inscrire sur le site
from flask import render_template, request, redirect
import re 
import accounts.accounts
import util.bdd
from werkzeug.security import generate_password_hash
import hashlib
import secrets

def createUser(pseudo: str, email : str, password : str):
    #Cette fonction crée un utilisateur dans la BDD et renvoie une erreur si problème
    conn = util.bdd.getConnexion()
    cursor = conn.cursor()
    
    # on vérifie que le pseudo n'existe pas déjà
    cursor.execute("SELECT id FROM users WHERE pseudo ILIKE %s", (pseudo,))
    ps = list(cursor.fetchall())
    cursor.execute("SELECT id FROM users WHERE pseudo ILIKE %s", (util.general.getUserLink(pseudo),))
    ps.extend(list(cursor.fetchall()))
    
    if len(ps) > 0:
        util.bdd.releaseConnexion(conn)
        return "Ce pseudonyme existe déjà"
    
    #On vérifie que l'email n'existe pas déjà
    cursor.execute("SELECT id FROM users WHERE mail ILIKE %s", (email,))
    if len(cursor.fetchall()) > 0:
        util.bdd.releaseConnexion(conn)
        return "L'adresse email est déjà utilisée"
    
    #On crypte le mot de passe
    mdp = generate_password_hash(password + accounts.accounts.PASSWORD_SALT)
    
    #On génère le hash de validation
    hashValidation = hashlib.sha256(secrets.token_urlsafe(128).encode()).hexdigest()
    
    #On ajoute l'utilisateur dans la BDD
    cursor.execute("""INSERT INTO users (pseudo, mdp, mail, description, comptes_autres_sites, inscription, validee, hash_validation)
                        VALUES (%s,%s,%s, '', '[]', NOW(), false, %s)
                        RETURNING id""",
                        (pseudo, mdp, email, hashValidation,))
    id = cursor.fetchall()[0][0]
    conn.commit()
    
    
    #TODO: Envoie du mail
    
    util.bdd.releaseConnexion(conn)
    return None


def page_inscription():
    err = None
    if request.method == "POST":
        if "pseudo" in request.form and "email" in request.form and "password" in request.form:
            pseudo = request.form.get("pseudo")
            email = request.form.get("email")
            password = request.form.get("password")
            ok = True
            if pseudo == "":
                ok = False
                err = "Pseudonyme invalide"
            if password == "":
                ok = False
                err = "Mot de passe invalide"
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                ok = False
                err = "Email invalide"
            #TODO: le captcha
            if ok:
                #On crée le compte
                err = createUser(pseudo, email, password)
                
                if err == None:
                    return redirect("/?msg=1")
        else:
            err = "Merci de remplir tous les champs"
        print(request.form)
    
    return render_template("accounts/inscription.html", err=err, customCSS="accounts.css")