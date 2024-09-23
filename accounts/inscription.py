#Ce fichier vas contenir la page et la requête post permettant de s'inscrire sur le site
from flask import render_template, request, redirect
import re 
import accounts.accounts
def page_inscription():
    #TODO si request post, on regarde si y'a tout
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
                err = accounts.accounts.createUser(pseudo, email, password)
                
                if err == None:
                    return redirect("/?msg=1")
        else:
            err = "Merci de remplir tous les champs"
        print(request.form)
    
    return render_template("accounts/inscription.html", err=err, customCSS="accounts.css")