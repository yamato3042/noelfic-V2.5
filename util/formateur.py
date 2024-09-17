#Ce fichier a pour but de permettre de formater les textes (fics, commentaires, description, etc)
#pour éviter les failles XSS tout en conservant les balises HTML, en transformant les \n en <br/>, en affichant les images
#et aussi en mettant les liens youtube dans des iframe
import bleach
import re

def clean_text(text):
    # Nettoyer le texte pour éviter les failles XSS
    allowed_tags = ['a', 'b', 'i', 'em', 'strong', 'p', 'br', 'img', 'iframe', 'c']
    allowed_attrs = {
        '*': ['href', 'src', 'alt', 'width', 'height', 'frameborder', 'allowfullscreen'],
        'a': ['href', 'title'],
        'img': ['src', 'alt'],
    }
    return bleach.clean(text, tags=allowed_tags, attributes=allowed_attrs)

def convert_links(text):
    # Convertir les liens en balises <a>
    pattern = re.compile(r'(https?://\S+)')
    return pattern.sub(r'<a href="\1">\1</a>', text)

def convert_emoticons(text):
    # Convertir les émoticônes en images ou icônes
    emoticons = {
        ':smile:': '<img src="smile.png" alt="smile">',
        ':sad:': '<img src="sad.png" alt="sad">',
        # Ajoutez d'autres émoticônes ici
    }
    for emoticon, replacement in emoticons.items():
        text = text.replace(emoticon, replacement)
    return text

def convert_youtube_links(text):
    # Convertir les liens YouTube en iframes
    pattern = re.compile(r'(https?://www\.youtube\.com/watch\?v=([a-zA-Z0-9_-]+))')
    return pattern.sub(r'<iframe width="560" height="315" src="https://www.youtube.com/embed/\2" frameborder="0" allowfullscreen></iframe>', text)

def convert_custom_tags(text):
    # Convertir les balises [i], [/i], [c], [/c], [b], [/b] en balises HTML
    text = text.replace("[i]", "<i>")
    text = text.replace("[/i]", "</i>")
    text = text.replace("[c]", "<c>")
    text = text.replace("[/c]", "</c>")
    text = text.replace("[b]", "<b>")
    text = text.replace("[/b]", "</b>")
    return text

def formater(text : str) -> str:
    #Les sauts de lignes
    texte_lignes_sautées = text.replace("\n", "<br/>")
    
    converted_custom_tags_result = convert_custom_tags(texte_lignes_sautées)
    
    # Nettoyer le texte
    clean_text_result = clean_text(converted_custom_tags_result)

    # Convertir les liens
    converted_links_result = convert_links(clean_text_result)

    # Convertir les émoticônes
    converted_emoticons_result = convert_emoticons(converted_links_result)

    # Convertir les liens YouTube
    final_result = convert_youtube_links(converted_emoticons_result)

    return final_result