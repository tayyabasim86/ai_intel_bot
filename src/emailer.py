import os, smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465

def send_email(subject: str, body: str, to_addrs: list[str], attach_path: str | None = None):
    user = os.getenv("GMAIL_USER")
    pwd  = os.getenv("GMAIL_APP_PASSWORD")
    if not user or not pwd:
        raise RuntimeError("Missing GMAIL_USER or GMAIL_APP_PASSWORD")

    msg = MIMEMultipart()
    msg["From"] = user
    msg["To"] = ", ".join(to_addrs)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    if attach_path and os.path.exists(attach_path):
        with open(attach_path, "rb") as f:
            part = MIMEBase("audio", "mp3")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        filename = os.path.basename(attach_path)
        part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
        msg.attach(part)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
        server.login(user, pwd)
        server.sendmail(user, to_addrs, msg.as_string())
