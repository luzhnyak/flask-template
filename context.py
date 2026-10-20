from flask import current_app


def inject_constants():
    return {
        "GOOGLE_RECAPTCHA_SITE_KEY": current_app.config["GOOGLE_RECAPTCHA_SITE_KEY"],
        "GOOGLE_CSE_ID": current_app.config["GOOGLE_CSE_ID"],
    }
