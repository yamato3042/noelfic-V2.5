#Ce code contient la page et la requête post pour se connecter sur le site
from flask import render_template, request, redirect, make_response
import util.bdd
import re 
import accounts.accounts
from werkzeug.security import check_password_hash
import hashlib
import secrets
import util.captcha

def connexionUser(pseudo, password):
    conn = util.bdd.getConnexion()
    cursor = conn.cursor()
    #Cette fonction vas récupérer l'utilisateur et le token
    cursor.execute("SELECT id, mdp FROM users WHERE pseudo = %s AND mdp IS NOT NULL AND validee = true", (pseudo,))
    val = cursor.fetchall()
    if len(val) != 1:
        util.bdd.releaseConnexion(conn)
        return "Mot de passe ou pseudo invalide"
    #Vérification du mot de passe
    print(val[0][1])
    if not check_password_hash(val[0][1], password+accounts.accounts.PASSWORD_SALT):
        util.bdd.releaseConnexion(conn)
        return "Mot de passe ou pseudo invalide"
    
    #Génération du token
    #La clée
    clée = ""
    while True:
        #On génère une nouvelle clée
        clée = hashlib.sha256(secrets.token_urlsafe(128).encode()).hexdigest()
        cursor.execute("SELECT id_users FROM users_token WHERE token = %s", (clée,))
        if len(cursor.fetchall()) == 0:
            break;
    
    cursor.execute("INSERT INTO users_token VALUES (%s,%s,NOW(), NOW())", (val[0][0], clée))
    conn.commit()
    
    #On retourne la clée
    util.bdd.releaseConnexion(conn)
    return [True, clée]

def page_connexion():
    err = None
    if request.method == "POST":
        if "pseudo" in request.form and "password" in request.form:
            pseudo = request.form.get("pseudo")
            password = request.form.get("password")
            ok = True
            if pseudo == "":
                ok = False
                err = "Pseudonyme invalide"
            if password == "":
                ok = False
                err = "Mot de passe invalide"
            #Le captcha
            if "g-recaptcha-response" not in request.form:
                ok = False
                err = "Captcha invalide"
            elif request.form["g-recaptcha-response"] == "":
                ok = False
                err = "Captcha invalide"
            else:
                #On vérifie la valeur du captcha
                if not util.captcha.verifyCaptcha(request.form["g-recaptcha-response"]):
                    ok = False
                    err = "Captcha invalide"
                    
            if ok:
                err = connexionUser(pseudo, password)
                
                if not isinstance(err, str):
                    #Alors tout est bon
                    resp = make_response(redirect("/?msg=2"))
                    resp.set_cookie("userToken", err[1], httponly=True)
                    return resp
        else:
            err = "Merci de remplir tous les champs"
        print(request.form)
    
    conn = util.bdd.getConnexion()
    session = accounts.accounts.Session(conn)
    captcha = util.captcha.getCaptcha()
    util.bdd.releaseConnexion(conn)
    return render_template("accounts/connexion.html", err=err, customCSS="accounts.css", session=session, captcha=captcha)