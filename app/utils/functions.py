from flask import flash, redirect, url_for, session, request
from functools import wraps

import requests
from config import config


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))

    return wrap


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
