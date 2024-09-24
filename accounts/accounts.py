#Ce fichier vas regarder le cookie, etc et génerer les tokens temporaires pour le système de compte de base sur l'ensemble du site.
import psycopg2
import util.bdd
from flask import request
import util.general
from werkzeug.security import generate_password_hash
import hashlib
import secrets

PASSWORD_SALT = "45Scnr7V_NOELFIC_Fa5Mt35q"
class Session:
    def __init__(self, conn : psycopg2.extensions.connection):
        self.connection = conn
        self.cursor = conn.cursor()
        
        self.logged = False
        self.pseudo = ""
        self.pp = False
        self.profil_lien = ""
        self.temp_token = ""
        self.id = -1
        
        #Connexion à la base si y'a rien
        """if self.cursor == None:
            self.conn = util.bdd.getConnexion()
            self.cursor = self.conn.cursor()"""
        #Login avec token normal
        if "userToken" in request.cookies:
            self.login(request.cookies.get("userToken"))
        #Login avec token temporaire
        #Si c'est un token temporaire alors c'est en post
        if request.method == "POST":
            if "tempToken" in request.form:
                self.loginTempToken(request.form.get("tempToken"))
                
        self.pp_photo = util.general.getAvatar(self.pseudo, self.pp)
    """def __del__(self):
        if self.conn != None:
            self.conn.close()"""
            
    def login(self, token):
        #Connexion avec le token du cookie
        print(token)
        self.cursor.execute("""SELECT id,pseudo,pp FROM users_token 
                            LEFT JOIN users ON users.id = users_token.id_users
                            WHERE token = %s""", (token,))
        val = self.cursor.fetchall()
        if len(val) == 1:
            self.logged = True
            self.id = val[0][0]
            self.pseudo = val[0][1]
            self.pp = val[0][2]
            self.profil_lien = util.general.getUserLink(self.pseudo)
            #Génération du token temporaire
            self.temp_token = genTempToken(self.cursor, self.id)
            self.connection.commit()
            
    
    def loginTempToken(self, token): 
        #Connexion avec le token temporaire
        pass


def genTempToken(cursor : psycopg2.extensions.cursor, user):
    clée = ""
    while True:
        #On génère une nouvelle clée
        clée = hashlib.sha256(secrets.token_urlsafe(128).encode()).hexdigest()
        cursor.execute("SELECT id_users FROM users_shorts_tokens WHERE token = %s", (clée,))
        if len(cursor.fetchall()) == 0:
            break;
    
    cursor.execute("INSERT INTO users_token VALUES (%s,%s,NOW())", (user, clée))
    
    return clée