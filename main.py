from flask import Flask, render_template, redirect, url_for 
app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024


import psycopg2
import util.bdd
import accounts.accounts

import index
import classements
import fic
import recherche
import random_fic
import profil
import minichat

import accounts.inscription
import accounts.connexion
import accounts.modif_profil
import accounts.logout
import accounts.ajax
import accounts.edit_fic
import accounts.mdp_oublie

app.add_url_rule("/", view_func=index.index)
app.add_url_rule("/actions/action_get_chat_messages", view_func=minichat.action_get_chat_messages)

app.add_url_rule("/classement/toutes/<page_>", view_func=classements.classement_tout)
app.add_url_rule("/classement/popularite/<page_>", view_func=classements.classement_popularite)
app.add_url_rule("/classement/date/<page_>", view_func=classements.classement_date)
app.add_url_rule("/classement/note/<page_>", view_func=classements.classement_note) 
app.add_url_rule("/classement/genre/<genre_>/<page_>", view_func=classements.classement_genre)

app.add_url_rule("/fic/<fic_>/<chapitre_>", view_func=fic.fic)

app.add_url_rule("/recherche/", view_func=recherche.recherche)

app.add_url_rule("/random/", view_func=random_fic.random_fic)

app.add_url_rule("/profil/<profil>", view_func=profil.profil)

app.add_url_rule("/minichat", view_func=minichat.page_minichat)

@app.route("/charte")
def page_charte():
    conn = util.bdd.getConnexion()
    session = accounts.accounts.Session(conn)
    util.bdd.releaseConnexion(conn)
    return render_template("charte.html", customCSS="charte.css", titre="Charte", session=session)

app.add_url_rule("/comptes/inscription", view_func=accounts.inscription.page_inscription, methods=['GET', 'POST'])
app.add_url_rule("/comptes/connexion", view_func=accounts.connexion.page_connexion, methods=['GET', 'POST'])
app.add_url_rule("/comptes/logout", view_func=accounts.logout.logout)
app.add_url_rule("/comptes/modif_profil", view_func=accounts.modif_profil.modif_profil)

app.add_url_rule("/comptes/changenote", view_func=accounts.ajax.changenote, methods=["POST"])
app.add_url_rule("/comptes/minichat_send_msg", view_func=accounts.ajax.minichat_send_msg, methods=["POST"])
app.add_url_rule("/comptes/chapitre_send_comment", view_func=accounts.ajax.chapitre_send_comment, methods=["POST"])
app.add_url_rule("/comptes/ajax_modif_profil", view_func=accounts.ajax.ajax_modif_profil, methods=["POST"])
app.add_url_rule("/comptes/ajax_modif_mdp", view_func=accounts.ajax.ajax_modif_mdp, methods=["POST"])

app.add_url_rule("/comptes/edit_fics", view_func=accounts.edit_fic.edit_fic_page)
app.add_url_rule("/comptes/edit_fics/getFics", view_func=accounts.edit_fic.getfics, methods=["POST"])
app.add_url_rule("/comptes/edit_fics/collaborateur_select", view_func=accounts.edit_fic.getcolaborateurs, methods=["POST"])
app.add_url_rule("/comptes/edit_fics/collaborateur_delete", view_func=accounts.edit_fic.collaborateur_delete, methods=["POST"])
app.add_url_rule("/comptes/edit_fics/collaborateur_add", view_func=accounts.edit_fic.collaborateur_add, methods=["POST"])
app.add_url_rule("/comptes/edit_fics/personalisation_get", view_func=accounts.edit_fic.personalisation_get, methods=["POST"])
app.add_url_rule("/comptes/edit_fics/personalisation_set", view_func=accounts.edit_fic.personalisation_set, methods=["POST"])
app.add_url_rule("/comptes/edit_fics/chapitre_get", view_func=accounts.edit_fic.chapitre_get, methods=["POST"])
app.add_url_rule("/comptes/edit_fics/chapitre_save", view_func=accounts.edit_fic.chapitre_save, methods=["POST"])
app.add_url_rule("/comptes/edit_fics/chapitre_create", view_func=accounts.edit_fic.chapitre_create, methods=["POST"])
app.add_url_rule("/comptes/edit_fics/fic_create", view_func=accounts.edit_fic.fic_create, methods=["POST"])

app.add_url_rule("/comptes/resetpass", view_func=accounts.mdp_oublie.resetpass, methods=["GET", "POST"])
app.add_url_rule("/comptes/changepasseV1", view_func=accounts.mdp_oublie.migrepass, methods=["GET", "POST"])
app.add_url_rule("/comptes/update_mdp", view_func=accounts.mdp_oublie.update_mdp, methods=["GET", "POST"])

@app.errorhandler(404)
def error_404(e):
    conn = util.bdd.getConnexion()
    session = accounts.accounts.Session(conn)
    util.bdd.releaseConnexion(conn)
    return render_template("404.html", titre="404", session=session)

if __name__ == "__main__": 
    app.run(debug=True)