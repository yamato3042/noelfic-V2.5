#Ce fichier a pour but de permettre de formater les textes (fics, commentaires, description, etc)
#pour éviter les failles XSS tout en conservant les balises HTML, en transformant les \n en <br/>, en affichant les images
#et aussi en mettant les liens youtube dans des iframe
import bleach
import re
import util.emots
def clean_text(text, balises):
    # Nettoyer le texte pour éviter les failles XSS
    allowed_tags = ['a', 'em', 'p', 'br', 'img',]
    allowed_tags.extend(balises)
    allowed_attrs = {
        '*': ['href', 'src', 'alt', 'width', 'height', 'frameborder', 'allowfullscreen'],
        'a': ['href', 'title'],
        'img': ['src', 'alt'],
    }
    return bleach.clean(text, tags=allowed_tags, attributes=allowed_attrs)

def convert_img_tags(texte):
    # Expression régulière pour trouver les balises [img]
    pattern = r'\[img\](.*?)\[/img\]'

    # Fonction de remplacement
    def remplacer_balise(match):
        url = match.group(1)
        print("url : ", url)
        return f'<img src="{url}"/>'

    # Remplacer les balises [img] par les balises <img>
    texte_converti = re.sub(pattern, remplacer_balise, texte)

    return texte_converti

def convert_links(texte):
    # Expression régulière pour trouver les liens qui ne sont pas dans des balises iframe ou img
    pattern = r'(?<!src=")(?<!href=")(?<!<a href=")(?<!<iframe src=")(http[s]?://\S+)'

    # Fonction de remplacement
    def remplacer_lien(match):
        url = match.group(0)
        print(url)
        return f'<a href="{url}">{url}</a>'

    # Remplacer les liens restants par des balises <a>
    texte_converti = re.sub(pattern, remplacer_lien, texte)

    return texte_converti

def convert_emoticons(text): #TODO: à refaire
    # Convertir les émoticônes en images ou icônes
    emots_dic = util.emots.emotdic()
    for i in emots_dic:
        text = text.replace(i, f'<img src="/static/emots/{emots_dic[i]}.gif" alt="{i}"/>')
    
    return text

def convert_youtube_links(text):
    # Si le texte est une liste, on le joint en une seule chaîne de caractères
    if isinstance(text, list):
        text = " ".join(text)
    
    # Expression régulière pour capturer les liens YouTube
    youtube_regex = r'(https?://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+))'
    
    # Fonction qui remplace un lien YouTube par l'iframe correspondante
    def replace_link_with_iframe(match):
        video_id = match.group(2)  # Récupérer l'ID de la vidéo
        return f'<iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe>'
    
    # Remplacer tous les liens par leur iframe
    result_text = re.sub(youtube_regex, replace_link_with_iframe, text)
    
    return result_text

def convert_custom_tags(text, balises): #TODO: update le CSS
    # Convertir les balises [i], [/i], [c], [/c], [b], [/b] en balises HTML
    
    for i in balises:
        text = text.replace(f"[{i}]", f"<{i}>")
        text = text.replace(f"[/{i}]", f"</{i}>")
    return text

def formater(text : str) -> str:
    
    
    balises = ["c","i","r","u","b"]
    text = convert_custom_tags(text, balises)
    
    # Nettoyer le texte
    text = clean_text(text, balises)

    # Convertir les liens YouTube
    text = convert_youtube_links(text)
    
    #Convertir les images [img][/img]
    text = convert_img_tags(text)
    
    # Convertir les liens
    text = convert_links(text)
    
    # Convertir les émoticônes
    text = convert_emoticons(text)
    
    #Les sauts de lignes
    text = text.replace("\n", "<br/>")

    

    return text