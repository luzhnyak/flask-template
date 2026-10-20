import requests
from flask import current_app, request


def verify_recaptcha(token):
    secret = current_app.config["GOOGLE_RECAPTCHA_SECRET_KEY"]
    if not secret:
        return True
    if not token:
        return False
    try:
        response = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={"secret": secret, "response": token, "remoteip": request.remote_addr},
            timeout=5,
        )
        response.raise_for_status()
        return response.json().get("success") is True
    except (requests.RequestException, ValueError, AttributeError):
        current_app.logger.warning("reCAPTCHA verification failed")
        return False
