from flask import Request
import util.bdd
import accounts.accounts

class Middleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        if environ['PATH_INFO'].startswith('/static/'):
            # Si c'est le cas, passer directement à l'application Flask sans exécuter le code du middleware
            return self.app(environ, start_response)
        #TODO: pas sûr le AJAX non plus
        
        request = Request(environ)
        
        # Code exécuté avant le traitement de la requête
        
        #La base de donnée
        conn = util.bdd.getConnexion()
        request.environ["conn"] = conn
        
        #La session
        request.environ["session"] = accounts.accounts.Session(conn, request)
        
        # Appel de l'application Flask pour traiter la requête
        response = self.app(environ, start_response)
        
        # Code exécuté après le traitement de la requête
        util.bdd.releaseConnexion(conn)

        return response