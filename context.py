from config import Config


def inject_constants():
    return {
        "GOOGLE_RECAPTCHA_SITE_KEY": Config.GOOGLE_RECAPTCHA_SITE_KEY,
        "DEBUG": Config.DEBUG,
    }
