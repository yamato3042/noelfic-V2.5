from flask import render_template
import psycopg2
import util.general
import util.bdd
import util.formateur
import accounts.accounts
def render_chat(cursor: psycopg2.extensions.cursor, limit = 20):
    cursor.execute("""select date, content, pp, pseudo from chat_messages 
                    LEFT JOIN users on chat_messages.auteur = users.id
                    ORDER BY chat_messages.id DESC
                    LIMIT %s""", (limit,))
    val = list(cursor.fetchall())
    val.reverse()

    messages = []
    for i in val:
        cur = {}
        cur["date"] = util.general.convDate(i[0])
        cur["content"] = util.formateur.formater(i[1])
        cur["avatar"] = util.general.getAvatar(i[3], i[2])
        cur["pseudo"] = i[3]

        cur["lien"] = util.general.getUserLink(i[3])
        messages.append(cur)
    return render_template("minichat.html", msg=messages)

def action_get_chat_messages():
    conn = util.bdd.getConnexion()
    cursor = conn.cursor()
    ret = render_chat(cursor)
    util.bdd.releaseConnexion(conn)
    return ret

def page_minichat():
    #Retournes tous le minichat
    conn = util.bdd.getConnexion()
    cursor = conn.cursor()
    session = accounts.accounts.Session(conn)
    messages = render_chat(cursor, limit=None) #On met la limit sur null pour qu'il n'y en ai pas
    util.bdd.releaseConnexion(conn)
    return render_template("minichat_all.html", titre="Tous les messages du minichat", customCSS="minichat_all.css", messages=messages, session=session)