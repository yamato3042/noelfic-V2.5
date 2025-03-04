from flask import render_template, request
import psycopg2
import util.general
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
    cursor: psycopg2.extensions.cursor = request.environ["conn"].cursor()
    ret = render_chat(cursor)
    return ret

def page_minichat():
    #Retournes tous le minichat
    cursor: psycopg2.extensions.cursor = request.environ["conn"].cursor()
    messages = render_chat(cursor, limit=None) #On met la limit sur null pour qu'il n'y en ai pas
    return render_template("minichat_all.html", titre="Tous les messages du minichat", customCSS="minichat_all.css", messages=messages, session=request.environ["session"])