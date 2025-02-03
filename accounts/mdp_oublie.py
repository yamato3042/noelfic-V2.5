#Contient requête et pages pour les mots de passe oubliés et aussi les migrations
from flask import render_template, request, redirect, make_response, abort
import re 
import accounts.accounts
from werkzeug.security import generate_password_hash
import hashlib
import secrets
import util.captcha
import send_mail
import param

def resetpass():
    cursor: psycopg2.extensions.cursor = request.environ["conn"].cursor()
    session: accounts.accounts.Session = request.environ["session"]
    err=""
    if request.method == "POST":
        if "email" in request.form:
            email = request.form.get("email")
            ok = True
            if not util.captcha.checkCaptcha():
                ok = False
                err = "Captcha invalide"
            if ok:
                #On vérifie que l'email soit attribué
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
                    request.environ["conn"].commit()
                    
                    err = "Un mail vous a été envoyé."
                    #Envoyer le mail
                    send_mail.send_mail("Changer de mot de passe", "Voici le lien pour changer votre mot de passe suite à votre demande. Si vous n'êtes pas à l'origine de cette demande merci de contacter un administrateur", f"noelfic.fr/comptes/update_mdp?token={clée}", email)
                else:
                    ok = False
                    err= "Email invalide"   
    #La page qui reset les mots de passe
    #Si y'a un argument d'url nommé token on affiche le truc de changement de mdp au lieu du truc qui demande le mail
    captcha = util.captcha.getCaptcha()
    return render_template("accounts/mdp_oublie_migration.html", err=err, customCSS="accounts.css", session=session, captcha=captcha)


def migrepass():
    cursor: psycopg2.extensions.cursor = request.environ["conn"].cursor()
    session: accounts.accounts.Session = request.environ["session"]
    err=""
    if request.method == "POST":
        if "email" in request.form:
            email = request.form.get("email")
            ok = True
            if not util.captcha.checkCaptcha():
                ok = False
                err = "Captcha invalide"
            if ok:
                #On vérifie que l'email soit attribué
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
                    request.environ["conn"].commit()
                    
                    err = "Un mail vous a été envoyé."
                    #Envoyer le mail
                    send_mail.send_mail("Migration de votre compte", "Voici le lien pour changer votre mot de passe suite à la demande de migration de votre compte.", f"noelfic.fr/comptes/update_mdp?token={clée}", email)
                    
                else:
                    ok = False
                    err= "Votre email est invalide ou alors votre compte a déjà été migré"
    #La page qui reset les mots de passe
    #Si y'a un argument d'url nommé token on affiche le truc de changement de mdp au lieu du truc qui demande le mail
    captcha = util.captcha.getCaptcha()
    return render_template("accounts/mdp_oublie_migration.html", err=err, customCSS="accounts.css", session=session, captcha=captcha, migration=True)


def update_mdp():
    cursor: psycopg2.extensions.cursor = request.environ["conn"].cursor()
    session: accounts.accounts.Session = request.environ["session"]
    
    if "token" not in request.args:
        abort(404) 
    err = ""
    
    if request.method == "POST":
        if "mdp" in request.form:
            new_mdp = request.form.get("mdp")
            token = request.args.get("token")
            
            #On vérifie que le token soit bon
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
                
                request.environ["conn"].commit()
                
                return redirect("/?msg=3")
            
            err = "token invalide"
            #On vérifie que le mot de passe soit ok
                
    captcha = util.captcha.getCaptcha()
    return render_template("accounts/mdp_oublie_migration.html", err=err, customCSS="accounts.css", session=session, captcha=captcha, update=True)