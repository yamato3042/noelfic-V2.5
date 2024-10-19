#Ce script prend le nom d'une fic et le transforme en nom pour les liens (plus d'accents, tout en minuscule avec des -)
#Ce fichier prend en charge les tâches générales (génération des liens, conversion des dates, etc)
import datetime
import hashlib

def getFicLink(id : int, nom : str, chapitre : int = 1) -> str:
    nom_conv = nom.lower()
    nom_conv = nom_conv.strip()
    nom_conv = nom_conv.replace(" ", "-")
    return f"/fic/{id}-{nom_conv}/{chapitre}"

def getUserLink(user: str) -> str:
    nom = user.lower()
    nom = nom.strip()
    nom = nom.replace(" ", "-")
    return f"/profil/{nom}"

def convDate(date: datetime):
    return date.strftime("%d/%m/%y à %H:%M:%S")

def getDicStatus():
    dicStatus = {
        1: "En cours",
        2: "En cours, sweet quotidienne",
        3: "C'est compliqué",
        4: "Terminée",
        5: "Abandonnée",

        11: "En cours, viens de la V1",
        12: "En cours, sweet quotidienne, viens de la V1",
        13: "C'est compliqué, viens de la V1",
        14: "Terminée, viens de la V1",
        15: "Abandonnée, viens de la V1",
    }
    return dicStatus

def getStatus(status: int) -> str:
    dicStatus = getDicStatus()

    if status in dicStatus:
        return dicStatus[status]
    else:
        return ""

def getNote(note : int) -> list: #Cette fonction elle doit prendre la note et retourné un tableau avec l'état des cinq noel
    ret = [False for i in range(5)]
    for a in range(note): #TODO: Le bot doit calculer la note et la mettre dans la bdd
        ret[a] = True
    return ret

def getAvatar(pseudo : str, have_avatar : bool) -> str:
    if have_avatar == True:
        #La pp
        hash_avatar = hashlib.md5(pseudo.strip().lower().encode()).hexdigest()
        return f"/static/avatars/{hash_avatar}-1.jpg"
    else:
        #PP par défaut
        return "/static/img/avatar-default.jpg"
    
def autresSitesIcon(site : str) -> str:
    liste_sites = ["2sucres", "onche", "jvc", "avenoel"]
    if site in liste_sites:
        return f"/static/img/sites_externes/{site}.png"
    else:
        return ""