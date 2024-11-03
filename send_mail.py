import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import param
        
def send_mail(objet: str, content : str, link: str, email: str):
    # Informations de l'email
    from_email = param.MAIL_LOGIN
    to_email = email
    subject = objet
    body = f"{content}\n\n{link}"

    # Création du message
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Connexion au serveur SMTP et envoi de l'email
    try:
        server = smtplib.SMTP(param.MAIL_HOSTNAME, param.MAIL_PORT)
        server.starttls()  # Utiliser TLS pour sécuriser la connexion
        server.login(param.MAIL_LOGIN, param.MAIL_PASSWORD)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print("Email envoyé avec succès!")
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email: {e}")