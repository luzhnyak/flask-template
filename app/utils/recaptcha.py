from flask import flash, redirect, url_for, session, request
from config import config
from functools import wraps
import requests


def check_recaptcha(f):
    """
    Checks Google  reCAPTCHA.
    :param f: view function
    :return: Function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        request.recaptcha_is_valid = None

        if request.method == 'POST':
            data = {
                'secret': config.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': request.form.get('g-recaptcha-response'),
                'remoteip': request.access_route[0]
            }
            r = requests.post(
                "https://www.google.com/recaptcha/api/siteverify",
                data=data
            )
            result = r.json()

            if result['success']:
                request.recaptcha_is_valid = True
            else:
                request.recaptcha_is_valid = False
                flash('Invalid reCAPTCHA. Please try again.', 'danger')

        return f(*args, **kwargs)

    return decorated_function
