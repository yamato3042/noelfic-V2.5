import util.bdd
from flask import request, redirect, make_response
def logout():
    if "token" not in request.args:
        return redirect("/")
    
    #On récupère le token
    temp_token = request.args.get("token")
    
    if "userToken" not in request.cookies:
        return redirect("/")
    
    token = request.cookies.get("userToken")
    conn = util.bdd.getConnexion()
    cursor = conn.cursor()

    cursor.execute("""SELECT users.id FROM users_shorts_tokens
                    LEFT JOIN users on users.id = users_shorts_tokens.id_users
                    LEFT JOIN users_token ON users.id = users_token.id_users

                    WHERE users_shorts_tokens.token = %s
                    AND users_token.token = %s""", (temp_token, token))
    val = cursor.fetchall()

    if len(val) == 1:
        #On suprimme le token
        cursor.execute("DELETE FROM users_token WHERE token = %s", (token,))
        conn.commit()
        #On suprimme le cookie
        resp = make_response(redirect("/"))
        resp.delete_cookie("userToken")
        return resp
    
    util.bdd.releaseConnexion(conn)
    return redirect("/")