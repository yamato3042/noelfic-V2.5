import param
from flask import request
import requests
def getCaptcha() -> str:
    ret = f"""
    <div class="cf-turnstile" data-sitekey="{param.CAPTCHA_SITE_KEY}"></div>
    <script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>
    """
    print(ret)
    return ret
    
def checkCaptcha() -> bool:
    if param.CAPTCHA_CHECK:
        if "cf-turnstile-response" in request.form:
            response = requests.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={
                "secret": param.CAPTCHA_SECRET_KEY,
                "response": request.form["cf-turnstile-response"],
            })
            result = response.json()
            if not result.get("success"):
                return False
            else:
                return True
        else:
            return False
    else:
        return True