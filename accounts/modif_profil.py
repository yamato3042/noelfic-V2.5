from flask import redirect, render_template
import util.bdd
import util.general
import accounts.accounts
def modif_profil():
    conn = util.bdd.getConnexion()
    session = accounts.accounts.Session(conn)
    cursor = conn.cursor()
    
    if not session.logged:
        return redirect("/")
    
    #Récupère les info du profil
    cursor.execute("SELECT pseudo, mail, description, comptes_autres_sites, pp FROM users WHERE id = %s", (session.id,))
    info_raw = cursor.fetchone()
    
    info = {
        "pseudo": info_raw[0],
        "mail": info_raw[1],
        "description": info_raw[2],
        "avatar": util.general.getAvatar(info_raw[0], info_raw[4]),
        "comptes_autres_sites": {item['site']: item['pseudo'] for item in info_raw[3]}
    }
    
    print(info["comptes_autres_sites"])
    #TODO: Système changement de PP
    
    util.bdd.releaseConnexion(conn)
    return render_template("accounts/modif_profil.html", customCSS="modif_profil.css", session=session, info=info)