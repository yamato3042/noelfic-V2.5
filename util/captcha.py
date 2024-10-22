#Ce code permet de générer et de vérifier un captcha avec hcaptcha
from param import HCAPTCHA_SITE_KEY, HCAPTCHA_SECRET
import requests

def getCaptcha() -> str :
    return f"""<script src="https://js.hcaptcha.com/1/api.js" async defer></script>
                <div class="h-captcha" data-sitekey="{HCAPTCHA_SITE_KEY}"></div>
    """
    
    
def verifyCaptcha(response_token : str) -> bool:
    
    url = 'https://hcaptcha.com/siteverify'
    data = {
        'secret': HCAPTCHA_SECRET,
        'response': response_token
    }
    response = requests.post(url, data=data)
    result = response.json()
    return result.get('success', False)