"""Send the digest via Resend. 3,000 emails/month free."""

from __future__ import annotations

import logging
import os

import resend

log = logging.getLogger(__name__)


def send_digest(subject: str, html: str) -> None:
    resend.api_key = os.environ["RESEND_API_KEY"]
    sender = os.environ["EMAIL_FROM"]
    recipient = os.environ["EMAIL_TO"]

    result = resend.Emails.send(
        {
            "from": sender,
            "to": [recipient],
            "subject": subject,
            "html": html,
        }
    )
    log.info("email sent: id=%s", result.get("id") if isinstance(result, dict) else result)
