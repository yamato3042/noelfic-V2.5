#Ce bot vas lire une fois par jour les valeurs de stats_visits et faire un recap en JSON dans static/stats/
#Ce script est un bot qui doit tourner à peu près toutes les dix minutes pour mettre à jour les notes et aussi suprimmer les tokens périmés

import psycopg2
import datetime
import time
import json
from param import BDD_DATABASE, BDD_HOST, BDD_USER, BDD_PASSWORD, BDD_PORT

def get_val(cursor: psycopg2.extensions.cursor) -> list:
    #On récup les valeurs de la bdd
    cursor.execute("SELECT * FROM stats_visits")
    return cursor.fetchall()

def work_val(val : list) -> dict:
    ret = {
        "date": None, #Le jour correspondant aux données
        "user_agents": {}, #La proportion des différents users_agents
        "logged": {True: 0, False: 0}, #La proportion d'utilisateurs connectés
        "page": {}, #Les pages uniques
        "fics": {} #Les fics (contenant les chapitres)
    }
    
    fics = {} #Ce dict il sert à faire en sorte qu'il n'y ai qu'une vue par IP
    
    #On traite les valeurs
    for i in val:
        try:
            date = i[0]
            url : str = i[1]
            user_agent : str = i[2]
            ip : str = i[3]
            logged : bool = i[4]
            
            #Si l'agent est un bot on s'en fout
            isBot = False
            lowered_agent = user_agent.lower()
            for i in ["bot", "bytespider"]:
                if i in lowered_agent:
                    isBot = True
            
            
            if ret["date"] == None:
                #On prend le premier enregistrement comme date de réference
                ret["date"] = date.strftime("%d-%m-%Y")
            
            if not isBot:
                #On regarde le path
                #Si c'est une fic on comptabilise dans un autre tableau
                if url.startswith("/fic/"):
                    #Il s'agit d'une fic
                    #On récupère le numéro de la fic et le nom du chapitre
                    fic_data = url.split("/")
                    chapitre = int(fic_data[-1])
                    fic = fic_data[-2]

                    if fic not in fics:
                        fics[fic] = {"sum" : set()}
                    #On ajoute le chapitre
                    fics[fic]["sum"].add(ip)
                    
                    if chapitre not in fics[fic]:
                        fics[fic][chapitre] = set()
                    fics[fic][chapitre].add(ip)
                    
                else:
                    if url not in ret["page"]:
                        ret["page"][url] = 1
                    else:
                        ret["page"][url] += 1
                    
                #On regarde l'user agent
                if user_agent not in ret["user_agents"]:
                    ret["user_agents"][user_agent] = 1
                else: 
                    ret["user_agents"][user_agent] += 1
                    
                #On regarde le logged
                if logged != None:
                    ret["logged"][logged] += 1
        except Exception as e:
            print("Erreur bot analytics, work val")
            print(e)
            
            
    for i in fics:
        cur_fic = {}
        #On calcule la somme
        cur_fic["sum"] = len(fics[i]["sum"])
        #On enlève la somme et on calcule par chapitres
        del fics[i]["sum"]
        
        for a in fics[i]:
            cur_fic[a] = len(fics[i][a])
        
        ret["fics"][i] = cur_fic
    
    return ret

def save_val(val : dict):
    #On enregistre
    if val["date"] != None:
        f = open(f"analytics/{val['date']}.json", "w")
        f.write(json.dumps(val, indent=2))
        f.close()

def clean_db(cursor : psycopg2.extensions.cursor):
    cursor.execute("DELETE FROM stats_visits")
    
def update_vues(fics: dict, cursor : psycopg2.extensions.cursor):
    for i in fics:
        try:
            #On récupère l'id de la fic
            ficId = int(i.split("-")[0])
            #On met à jour les vues de la fic
            cursor.execute("UPDATE fics SET vues = vues + %s WHERE id = %s", (fics[i]["sum"], ficId))
            #On s'occupe des chapitres
            for a in fics[i]:
                if a != "sum":
                    cursor.execute("UPDATE chapitres SET vues = vues + %s WHERE fic = %s AND num = %s", (fics[i][a], ficId, a,))
        except Exception as e:
            print("Erreur bot analytics, updates vues")
            print(e)
        
        
        
        
debut = time.perf_counter()
date_début = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
f = open("bot_analytics.log", "a")
f.write(f"[{date_début}] Starting job\n")
f.close()

conn = psycopg2.connect(database=BDD_DATABASE,
                        host=BDD_HOST,
                        user=BDD_USER,
                        password=BDD_PASSWORD,
                        port=BDD_PORT)
cursor = conn.cursor()

#On récupère les valeurs
val = get_val(cursor)
ret = work_val(val)
update_vues(ret["fics"], cursor)
save_val(ret)

clean_db(cursor)
conn.commit()
conn.close()

fin = time.perf_counter()
duree = (fin - debut) * 1000  # Convertir en millisecondes

date_fin = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

f = open("bot_analytics.log", "a")
f.write(f"[{date_début}] Ending job, {duree:.6f}ms\n")
f.close()