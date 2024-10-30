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
        #print("url : ", url)
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
        #print(url)
        return f'<a href="{url}">{url}</a>'

    # Remplacer les liens restants par des balises <a>
    texte_converti = re.sub(pattern, remplacer_lien, texte)

    return texte_converti

def convert_emoticons(text):
    # Convertir les émoticônes en images ou icônes
    """emots_dic = util.emots.emotdic()
    for i in emots_dic:
        text = text.replace(i, f'<img src="/static/emots/{emots_dic[i]}.gif" alt="{i}"/>')
    
    return text"""
    # Fonction de remplacement pour l'expression régulière
    #D'après ChatGPT ça c'est plus performant
    emots_dic = util.emots.emotdic()
    def replace_match(match):
        emoticon = match.group(0)
        img_id = emots_dic.get(emoticon)
        return f'<img src="/static/emots/{img_id}.gif" alt="{emoticon}"/>'
    
    # Créer une expression régulière qui détecte toutes les clés du dictionnaire EMOTS
    pattern = re.compile('|'.join(re.escape(emot) for emot in emots_dic.keys()))
    # Remplacer tous les émoticônes d'un coup
    return pattern.sub(replace_match, text)

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

def convert_custom_tags(text, balises):
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


def replace_html_tags(html_content, opening_tag, closing_tag, new_opening_tag, new_closing_tag):
    # Échappez les caractères spéciaux dans les balises pour les utiliser dans l'expression régulière
    opening_tag_escaped = re.escape(opening_tag)
    closing_tag_escaped = re.escape(closing_tag)

    # Utilisez une expression régulière pour trouver les balises spécifiées
    pattern = re.compile(f'{opening_tag_escaped}(.*?){closing_tag_escaped}', re.DOTALL)

    # Remplacez les balises par les nouvelles balises
    replaced_content = pattern.sub(rf'{new_opening_tag}\1{new_closing_tag}', html_content)

    return replaced_content

def replace_img_tags(html_content):
    # Utilisez une expression régulière pour trouver les balises <img> avec l'attribut src
    pattern = re.compile(r'<img\s+src="([^"]+)"\s*>', re.IGNORECASE)

    # Remplacez les balises <img> par [img]...[/img]
    replaced_content = pattern.sub(r'[img]\1[/img]', html_content)

    return replaced_content

def convert_to_custom_tags(text, reverse=False):
    # Convertir les balises [i], [/i], [c], [/c], [b], [/b] en balises HTML
    tags = {
        "<strong>": "[b]",
        "</strong>": "[/b]",
        "<em>": "[i]",
        "</em>": "[/i]",
        "<u>": "[u]",
        "</u>": "[/u]",
    }
    
    if not reverse:
        #De HTML vers balises normales
        for i in tags.keys():
            text = text.replace(i, tags[i])
        text = replace_html_tags(text, '<p class="ql-align-center">', '</p>', '[c]', '[/c]')
        text = replace_html_tags(text, '<p class="ql-align-right">', '</p>', '[r]', '[/r]')
        #Les img
        text = replace_img_tags(text)
    else:
        for i in tags.keys():
            text = text.replace(tags[i], i)
        text = replace_html_tags(text, '[c]', '[/c]', '<p class="ql-align-center">', '</p>')
        text = replace_html_tags(text, '[r]', '[/r]', '<p class="ql-align-right">', '</p>')
        #L'inverse de replace_img_tags
        pattern = re.compile(r'\[img\]([^\]]+)\[/img\]', re.IGNORECASE)
        # Remplacez les balises [img]...[/img] par <img src="...">
        text = pattern.sub(r'<img src="\1">', text)
    
    """
    text = text.replace("<strong>", "[b]")
    text = text.replace("</strong>", "[/b]")
    
    text = text.replace("<em>", "[i]")
    text = text.replace("</em>", "[/i]")
    
    text = text.replace("<u>", "[u]")
    text = text.replace("</u>", "[/u]")"""
    
    
    
    
    return text    

def formatEntrée(content): #Prend un texte en entrée et le rend propre pour la BDD
    #Ici on remplace les balises
    content = convert_to_custom_tags(content)
    #Puis on nettoie
    content = bleach.clean(content, tags=[], attributes={}, strip=True)
    
    return content

def desinfecter(content):
    content = bleach.clean(content, tags=[], attributes={}, strip=True)
    return content

def formatPourEspaceEcriture(content): #En gros cette fonction elle vas permettre de prendre un texte de la BDD et de l'envoyer dans le quill
    #Pas besoin de convertir les liens youtubes
    #Pas besoin de convertir les emots elles sont déjà de base dans le truc normalement
    content = convert_to_custom_tags(content, True)
    return content