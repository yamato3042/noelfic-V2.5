def send_mail(objet: str, content : str, link: str, email: str):
    # Configuration de l'email
    sender_email = "comptes@noelfic.fr"
    receiver_email = email
    subject = objet
    body = f"{content}\n\n{link}"

    # Création de l'objet MIME
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Connexion au serveur SMTP local (Sendmail)
    try:
        server = smtplib.SMTP('localhost')
        server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Email envoyé avec succès.")
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email: {e}")
    finally:
        server.quit()