#Ce fichier vas regarder le cookie, etc et génerer les tokens temporaires pour le système de compte de base sur l'ensemble du site.
import psycopg2
import util.bdd
from flask import request
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
    
    
    
def CreateUser(pseudo: string, email : string, password : string):
    #Cette fonction crée un utilisateur dans la BDD et renvoie une erreur si problème
    pass