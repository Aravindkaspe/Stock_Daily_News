from __future__ import annotations

import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

log = logging.getLogger(__name__)


def send_digest(subject: str, html: str) -> None:
    gmail_user = os.environ["GMAIL_USER"]
    gmail_key = os.environ["GMAIL_KEY"]
    recipient = os.environ["EMAIL_TO"]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Stock Digest <{gmail_user}>"
    msg["To"] = recipient
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_user, gmail_key)
        server.sendmail(gmail_user, recipient, msg.as_string())

    log.info("email sent to %s", recipient)