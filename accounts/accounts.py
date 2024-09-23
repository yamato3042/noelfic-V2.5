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
    def __init__(self, cursor : psycopg2.extensions.cursor = None, tempToken = None):
        self.cursor : psycopg2.extensions.cursor = cursor
        self.conn : psycopg2.extensions.connection = None #En gros ici on met sur None comme ça si on fait une connection sur le moment on pourra la quitter à la desctruction
        self.logged = False
        
        #Connexion à la base si y'a rien
        if self.cursor == None:
            self.conn = util.bdd.getConnexion()
            self.cursor = self.conn.cursor()
        #Login avec token normal
        if "userToken" in request.cookies:
            self.login(request.cookies.get("userToken"))
        #Login avec token temporaire
        #Si c'est un token temporaire alors c'est en post
        if request.method == "POST":
            if "tempToken" in request.form:
                self.loginTempToken(request.form.get("tempToken"))
    def __del__(self):
        if self.conn != None:
            self.conn.close()
            
    def login(self, token):
        #Connexion avec le token du cookie
        pass
    
    def loginTempToken(self, token): 
        #Connexion avec le token temporaire
        pass
    
    
    
def createUser(pseudo: str, email : str, password : str):
    #Cette fonction crée un utilisateur dans la BDD et renvoie une erreur si problème
    conn = util.bdd.getConnexion()
    cursor = conn.cursor()
    
    # on vérifie que le pseudo n'existe pas déjà
    cursor.execute("SELECT id FROM users WHERE pseudo ILIKE %s", (pseudo,))
    ps = list(cursor.fetchall())
    cursor.execute("SELECT id FROM users WHERE pseudo ILIKE %s", (util.general.getUserLink(pseudo),))
    ps.extend(list(cursor.fetchall()))
    
    if len(ps) > 0:
        util.bdd.releaseConnexion(conn)
        return "Ce pseudonyme existe déjà"
    
    #On vérifie que l'email n'existe pas déjà
    cursor.execute("SELECT id FROM users WHERE mail ILIKE %s", (email,))
    if len(cursor.fetchall()) > 0:
        util.bdd.releaseConnexion(conn)
        return "L'adresse email est déjà utilisée"
    
    #On crypte le mot de passe
    mdp = generate_password_hash(pseudo + PASSWORD_SALT)
    
    #On génère le hash de validation
    hashValidation = hashlib.sha256(secrets.token_urlsafe(128).encode()).hexdigest()
    
    #On ajoute l'utilisateur dans la BDD
    cursor.execute("""INSERT INTO users (pseudo, mdp, mail, description, comptes_autres_sites, inscription, validee, hash_validation)
                        VALUES (%s,%s,%s, '', '[]', NOW(), false, %s)
                        RETURNING id""",
                        (pseudo, mdp, email, hashValidation,))
    id = cursor.fetchall()[0][0]
    conn.commit()
    
    
    #TODO: Envoie du mail
    
    util.bdd.releaseConnexion(conn)
    return None