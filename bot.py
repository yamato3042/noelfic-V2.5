#Ce script est un bot qui doit tourner à peu près toutes les dix minutes pour mettre à jour les notes et aussi suprimmer les tokens périmés

import psycopg2
import datetime
import time
from param import BDD_DATABASE, BDD_HOST, BDD_USER, BDD_PASSWORD, BDD_PORT

def updateNotes(cursor: psycopg2.extensions.cursor):
    #Récupère toutes les notes
    cursor.execute("SELECT fic, note from note")
    notes_raw = cursor.fetchall()
    
    notes = {}
    for i in notes_raw:
        fic = i[0]
        note = float(i[1])
        
        print(f"calcule note pour {fic} : {note}")
        
        if fic not in notes:
            notes[fic] = note
        
        #On calcule
        notes[fic] = (notes[fic] + note) / 2.0
    
    #On met à jour sur la BDD
    for i in notes.keys():
        cursor.execute("UPDATE fics SET note = %s WHERE id = %s", (int(notes[i]),i,))
        
def clean_shorts_tokens(cursor:psycopg2.extensions.cursor):
    #On nettoie le bordel
    print("Nettoyage des tokens utilisateurs temporaires")
    cursor.execute("DELETE FROM users_shorts_tokens WHERE creation < NOW() - INTERVAL '1 day';")

def clean_tokens(cursor: psycopg2.extensions.cursor):
    #On nettoie les tokens en httponly, ceux pas utilisés depuis 6 mois
    print("Nettoyage des tokens utilisateurs")
    cursor.execute("DELETE FROM users_token WHERE lastconn < NOW() - INTERVAL '6 months';")
    
def update_collaboratif(cursor: psycopg2.extensions.cursor):
    print("Mise à jour des fics collaboratives")
    cursor.execute("""SELECT id_fics, COUNT(id_users) 
            FROM collaborateur 
            GROUP BY id_fics HAVING COUNT(id_users) > 1""")
    val = cursor.fetchall()
    
    fics_id = []
    for i in val:
        fics_id.append(i[0])
    
    cursor.execute("UPDATE fics SET collaboratif = false; UPDATE fics SET collaboratif = true WHERE id IN %s;", (tuple(fics_id),))

def clean_chg_mdp_tokens(cursor:psycopg2.extensions.cursor):
    #On nettoie le bordel
    print("Nettoyage des tokens de changement de mot de passe")
    cursor.execute("DELETE FROM token_changement_mdp WHERE timestamp < NOW() - INTERVAL '2 day';")
    
    
debut = time.perf_counter()
date_début = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
f = open("bot.log", "a")
f.write(f"[{date_début}] Starting job\n")
f.close()

conn = psycopg2.connect(database=BDD_DATABASE,
                        host=BDD_HOST,
                        user=BDD_USER,
                        password=BDD_PASSWORD,
                        port=BDD_PORT)
cursor = conn.cursor()

updateNotes(cursor)
clean_tokens(cursor)
clean_shorts_tokens(cursor)
update_collaboratif(cursor)
clean_chg_mdp_tokens(cursor)

conn.commit()
conn.close()

fin = time.perf_counter()
duree = (fin - debut) * 1000  # Convertir en millisecondes

date_fin = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

f = open("bot.log", "a")
f.write(f"[{date_début}] Ending job, {duree:.6f}ms\n")
f.close()