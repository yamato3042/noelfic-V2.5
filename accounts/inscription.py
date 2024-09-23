#Ce fichier vas contenir la page et la requête post permettant de s'inscrire sur le site
from flask import render_template

def page_inscription():
    return render_template("accounts/inscription.html")