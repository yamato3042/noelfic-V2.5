#Ce fichier vas contenir la page et la requête post permettant de s'inscrire sur le site
from flask import render_template, request, redirect, abort
import re 
import accounts.accounts
from werkzeug.security import generate_password_hash
import hashlib
import secrets
import util.captcha
from param import ALLOW_AUTH, PASSWORD_SALT
import send_mail

def createUser(pseudo: str, email : str, password : str):
    #Cette fonction crée un utilisateur dans la BDD et renvoie une erreur si problème
    cursor: psycopg2.extensions.cursor = request.environ["conn"].cursor()
    
    # on vérifie que le pseudo n'existe pas déjà
    cursor.execute("SELECT id FROM users WHERE pseudo ILIKE %s", (pseudo,))
    ps = list(cursor.fetchall())
    cursor.execute("SELECT id FROM users WHERE pseudo ILIKE %s", (util.general.getUserLink(pseudo),))
    ps.extend(list(cursor.fetchall()))
    
    if len(ps) > 0:
        return "Ce pseudonyme existe déjà"
    
    #On vérifie que l'email n'existe pas déjà
    cursor.execute("SELECT id FROM users WHERE mail ILIKE %s", (email,))
    if len(cursor.fetchall()) > 0:
        return "L'adresse email est déjà utilisée"
    
    #On crypte le mot de passe
    mdp = generate_password_hash(password + PASSWORD_SALT)
    
    #On génère le hash de validation
    hashValidation = hashlib.sha256(secrets.token_urlsafe(128).encode()).hexdigest()
    
    #On ajoute l'utilisateur dans la BDD
    cursor.execute("""INSERT INTO users (pseudo, mdp, mail, description, comptes_autres_sites, inscription, validee, hash_validation)
                        VALUES (%s,%s,%s, '', '[]', NOW(), false, %s)
                        RETURNING id""",
                        (pseudo, mdp, email, hashValidation,))
    id = cursor.fetchall()[0][0]
    request.environ["conn"].commit()
    
    
    #Envoie du mail
    send_mail.send_mail("Confirmer votre inscription", "Voici le lien pour confirmer votre inscription sur Noelfic.fr", f"noelfic.fr/comptes/valider_compte?token={hashValidation}", email)
    return None


def page_inscription():
    cursor: psycopg2.extensions.cursor = request.environ["conn"].cursor()
    session: accounts.accounts.Session = request.environ["session"]
    
    if not ALLOW_AUTH:
        abort(404)
    err = None
    if request.method == "POST":
        #print(request.form)
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
            if not util.captcha.checkCaptcha():
                ok = False
                err = "Captcha invalide"
                
            if ok:
                #On crée le compte
                err = createUser(pseudo, email, password)
                
                if err == None:
                    return redirect("/?msg=1")
        else:
            err = "Merci de remplir tous les champs"
    
    
    captcha = util.captcha.getCaptcha()
    return render_template("accounts/inscription.html", err=err, customCSS="accounts.css", session=session, captcha=captcha)



def inscription_check_token():
    cursor: psycopg2.extensions.cursor = request.environ["conn"].cursor()
    #Permet de check les token envoyé par mail à l'page_inscription
    if "token" not in request.args:
        abort(404) 
    token = request.args.get("token")
    
            
    #On vérifie que le token soit bon
    cursor.execute("SELECT id FROM users WHERE hash_validation LIKE %s", (token,))
    val = cursor.fetchall()
            
    if len(val) == 1:
        userid = val[0][0]
        #On update
        cursor.execute("UPDATE users SET hash_validation = null, validee = true WHERE id = %s", (userid,))     
        request.environ["conn"].commit()      
    else:
        abort(404)
                
    return redirect("/?msg=4")