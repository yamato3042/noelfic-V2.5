import psycopg2
from param import BDD_DATABASE, BDD_HOST, BDD_USER, BDD_PASSWORD, BDD_PORT
def getConnexion() -> psycopg2.extensions.connection:
    conn = psycopg2.connect(database=BDD_DATABASE,
                        host=BDD_HOST,
                        user=BDD_USER,
                        password=BDD_PASSWORD,
                        port=BDD_PORT)
    return conn

def releaseConnexion(conn : psycopg2.extensions.connection):
    conn.close()