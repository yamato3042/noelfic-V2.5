#Contient un ensemble de fonctions pour gérer les classements
import psycopg2
import util.general
def gen_liste_pages(page : int, nbPages: int):
    #Calcule la liste des pages à afficher
    #(Y'a probablement plus efficace mais flemme on verra après)
    liste_pages = []
    for i in range(5,0,-1):
        liste_pages.append([page-i, "all"])
    liste_pages.append([page, "cur"])
    for i in range(1,5):
        liste_pages.append([page+i, "all"])
    
    for i in range(len(liste_pages), 0, -1):
        index = i-1
        #Si la valeur est trop grande on suprimme
        if liste_pages[index][0] > nbPages:
            del liste_pages[index]
        #Si la valeur est inférieur à 1 aussi
        elif liste_pages[index][0] < 1:
            del liste_pages[index]
    #Si le premier chiffre n'est pas 1 alors on le met avec le chevrons
    if liste_pages[0][0] != 1:
        liste_pages.insert(0, [1, "deb"])
    #De même pour la fin
    if liste_pages[-1][0] != nbPages:
        liste_pages.append([nbPages, "fin"])
    return liste_pages

def gen_fics(fics_raw : int): #Permet de convertir un fic_raw sortant de sql vers une liste de dictionnaires
    fics = []
    for i in fics_raw:
        cur = {}
        cur["fic_lien"] = util.general.getFicLink(i[0], i[1])
        cur["titre"] = i[1]
        cur["auteur"] = i[2]
        cur["auteur_lien"] = util.general.getUserLink(i[2])
        cur["date"] = util.general.convDate(i[3])
        cur["status"] = util.general.getStatus(i[4])

        """cur["note"] = [False for i in range(5)]
        for a in range(i[6]): #TODO: Le bot doit calculer la note et la mettre dans la bdd
            cur["note"][a] = True"""
        cur["note"] = util.general.getNote(i[6])
        
        if i[5] == True:
            cur["collaboratif"] = "Oui"
        else:
            cur["collaboratif"] = "Non"
        fics.append(cur)
    return fics

def getPages(page : int, cursor: psycopg2.extensions.cursor, request : str = "SELECT count(*) FROM fics", request_data : tuple =()): #Obtiens le nombre totale de pages
    cursor.execute(request, request_data)
    nbFics : int = cursor.fetchall()[0][0]

    nbPages = nbFics // 20
    if (nbFics % 20) != 0:
        nbPages +=1

    if page > nbPages or page < 1:
        return "err"

    offset = 20 * (page-1)

    return {"offset": offset, "nbPages": nbPages}
