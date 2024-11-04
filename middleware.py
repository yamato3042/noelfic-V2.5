from flask import Request, Response
import util.bdd
import accounts.accounts
from param import RECORD_STAT

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
        
        if RECORD_STAT:
            ip = ""
            if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
                ip = request.environ['REMOTE_ADDR']
            else:
                ip = request.environ['HTTP_X_FORWARDED_FOR'] # if behind a proxy
            #On enregistre les stats
            conn.rollback()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO stats_visits VALUES (NOW(), %s, %s, %s, %s)", (request.path, request.user_agent.string, ip, request.environ["session"].logged))
            conn.commit()
        
        # Code exécuté après le traitement de la requête
        util.bdd.releaseConnexion(conn)

        return response