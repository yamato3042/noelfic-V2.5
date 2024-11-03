#Contient requête et pages pour les mots de passe oubliés et aussi les migrations
from flask import render_template, request, redirect, make_response, abort
import util.bdd
import re 
import accounts.accounts
from werkzeug.security import generate_password_hash
import hashlib
import secrets
import util.captcha
import send_mail
import param

def resetpass():
    err=""
    if request.method == "POST":
        if "email" in request.form:
            email = request.form.get("email")
            ok = True
            if param.CHECK_CHAPTCHA:
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
                #On vérifie que l'email soit attribué
                conn = util.bdd.getConnexion()
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM users WHERE mail LIKE %s AND from_v1 = false", (email,))
                val = cursor.fetchall()
                if len(val) == 1:
                    #On a un mail
                    user = val[0][0]
                    #On génère le token
                    clée = ""
                    while True:
                        #On génère une nouvelle clée
                        clée = hashlib.sha256(secrets.token_urlsafe(512).encode()).hexdigest()
                        cursor.execute("SELECT id_users FROM token_changement_mdp WHERE token = %s", (clée,))
                        if len(cursor.fetchall()) == 0:
                            break;
                    #On crée le token dans la bdd
                    cursor.execute("INSERT INTO token_changement_mdp VALUES (%s,%s, false, NOW())", (user, clée))
                    conn.commit()
                    
                    err = "Un mail vous a été envoyé."
                    #Envoyer le mail
                    send_mail.send_mail("Changer de mot de passe", "Voici le lien pour changer votre mot de passe suite à votre demande. Si vous n'êtes pas à l'origine de cette demande merci de contacter un administrateur", f"noelfic.fr/comptes/update_mdp?token={clée}", email)
                else:
                    ok = False
                    err= "Email invalide"   
                util.bdd.releaseConnexion(conn)
    #La page qui reset les mots de passe
    #Si y'a un argument d'url nommé token on affiche le truc de changement de mdp au lieu du truc qui demande le mail
    conn = util.bdd.getConnexion()
    session = accounts.accounts.Session(conn)
    captcha = util.captcha.getCaptcha()
    util.bdd.releaseConnexion(conn)
    return render_template("accounts/mdp_oublie_migration.html", err=err, customCSS="accounts.css", session=session, captcha=captcha)


def migrepass():
    err=""
    if request.method == "POST":
        if "email" in request.form:
            email = request.form.get("email")
            ok = True
            if param.CHECK_CHAPTCHA:
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
                #On vérifie que l'email soit attribué
                conn = util.bdd.getConnexion()
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM users WHERE mail LIKE %s AND from_v1 = true", (email,))
                val = cursor.fetchall()
                if len(val) == 1:
                    #On a un mail
                    user = val[0][0]
                    #On génère le token
                    clée = ""
                    while True:
                        #On génère une nouvelle clée
                        clée = hashlib.sha256(secrets.token_urlsafe(512).encode()).hexdigest()
                        cursor.execute("SELECT id_users FROM token_changement_mdp WHERE token = %s", (clée,))
                        if len(cursor.fetchall()) == 0:
                            break;
                    #On crée le token dans la bdd
                    cursor.execute("INSERT INTO token_changement_mdp VALUES (%s,%s, true, NOW())", (user, clée))
                    conn.commit()
                    
                    err = "Un mail vous a été envoyé."
                    #Envoyer le mail
                    send_mail.send_mail("Migration de votre compte", "Voici le lien pour changer votre mot de passe suite à la demande de migration de votre compte.", f"noelfic.fr/comptes/update_mdp?token={clée}", email)
                    
                else:
                    ok = False
                    err= "Votre email est invalide ou alors votre compte a déjà été migré"
                util.bdd.releaseConnexion(conn)
    #La page qui reset les mots de passe
    #Si y'a un argument d'url nommé token on affiche le truc de changement de mdp au lieu du truc qui demande le mail
    conn = util.bdd.getConnexion()
    session = accounts.accounts.Session(conn)
    captcha = util.captcha.getCaptcha()
    util.bdd.releaseConnexion(conn)
    return render_template("accounts/mdp_oublie_migration.html", err=err, customCSS="accounts.css", session=session, captcha=captcha, migration=True)


def update_mdp():
    if "token" not in request.args:
        abort(404) 
    err = ""
    
    if request.method == "POST":
        if "mdp" in request.form:
            new_mdp = request.form.get("mdp")
            token = request.args.get("token")
            
            #On vérifie que le token soit bon
            conn = util.bdd.getConnexion()
            cursor = conn.cursor()
            cursor.execute("SELECT id_users, migration FROM token_changement_mdp WHERE token LIKE %s", (token,))
            val = cursor.fetchall()
            
            if len(val) == 1:
                userid = val[0][0]
                migration = val[0][1]
                
                #On change le mot de passe
                
                #On crypte le mot de passe
                mdp = generate_password_hash(new_mdp + param.PASSWORD_SALT)
    
                if migration:
                    cursor.execute("UPDATE users SET mdp = %s, from_v1 = false WHERE id = %s", (mdp, userid))
                else:
                    cursor.execute("UPDATE users SET mdp = %s WHERE id = %s", (mdp, userid))
                    
                #On suprimme le token
                cursor.execute("DELETE FROM token_changement_mdp WHERE token LIKE %s", (token,))
                
                conn.commit()
                
                util.bdd.releaseConnexion(conn)
                return redirect("/?msg=3")
            
            util.bdd.releaseConnexion(conn)
            err = "token invalide"
            #On vérifie que le mot de passe soit ok
                
    conn = util.bdd.getConnexion()
    session = accounts.accounts.Session(conn)
    captcha = util.captcha.getCaptcha()
    util.bdd.releaseConnexion(conn)
    return render_template("accounts/mdp_oublie_migration.html", err=err, customCSS="accounts.css", session=session, captcha=captcha, update=True)