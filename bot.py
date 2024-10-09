#Ce script est un bot qui doit tourner à peu près toutes les dix minutes pour mettre à jour les notes et aussi suprimmer les tokens périmés

import psycopg2

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
    
conn = psycopg2.connect(database="noelfic",
                        host="localhost",
                        user="postgres",
                        password="66pzyBi3V7S2Qv",
                        port="5432")
cursor = conn.cursor()

updateNotes(cursor)
clean_tokens(cursor)
clean_shorts_tokens(cursor)

conn.commit()
conn.close()