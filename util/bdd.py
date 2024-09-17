import psycopg2

def getConnexion() -> psycopg2.extensions.connection:
    conn = psycopg2.connect(database="noelfic",
                        host="localhost",
                        user="postgres",
                        password="66pzyBi3V7S2Qv",
                        port="5432")
    return conn

def releaseConnexion(conn : psycopg2.extensions.connection):
    conn.close()