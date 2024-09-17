def getGenresDic():
    dicGenres = {
        1:"Action",
        2:"BD",
        3:"Concours",
        4:"Fantastique",
        5:"Horreur",
        6:"Moins de 15 ans",
        7:"Nawak",
        8:"No-Fake",
        9:"Polar",
        10:"Réaliste",
        11:"Sayks",
        12:"Science-Fiction",
        13:"Sentimental",
        14:"Inconnu",
    }
    return dicGenres

def getGenre(genre : int) -> str:
    genresDic = getGenresDic()

    if genre in genresDic:
        return genresDic[genre]
    else:
        return ""

def getGenreId(genre_ : str) -> int:
    genresDic = getGenresDic()
    genre = genre_.lower().strip().replace(" ", "_")

    for i in genresDic.keys():
        if genre == genresDic[i].lower().replace(" ", "_"):
            return i
    return -1