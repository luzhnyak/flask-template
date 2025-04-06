import asyncio
import requests
from app.services.user import UserService
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_user, logout_user

import app.utils.utilites as utilites
from app.infrastructure.database import Base, async_engine, sync_session, async_session, get_session
from app.infrastructure.models import Category, User
from config import config

auth_bp = Blueprint("auth", __name__)


# ================================================ User Login
@auth_bp.route("/login", methods=["GET", "POST"])
# @check_recaptcha
async def login():
    user_servise = UserService(async_session())
    if request.method == "POST":        
        email = request.form["email"]
        password_candidate = request.form["password"]           

        user = await user_servise.get_user_by_email(email=email)

        if user is not None:
            # Compare Passwords
            if password_candidate == user.password:
                flash("You are now logged in", "success")
                login_user(user)
                return redirect("/admin")

            else:
                error = "Невiрний пароль чи логiн"
                return render_template("login.html", error=error)
        else:
            error = "Користувач не знайдений"
            return render_template("login.html", error=error, CONFIG=config)

    return render_template("login.html", CONFIG=config)


# ===============================================================Login Facebook
def oauthFacebook(code):

    url = "https://graph.facebook.com/oauth/access_token"

    params = {
        "client_id": config.FB_CLIENT_ID,
        "client_secret": config.FB_SECRET,
        "redirect_uri": "https://" + config.DOMEN + "/loginfb",
        "code": code,
    }

    response = requests.get(url, params=params)
    url = "https://graph.facebook.com/me"

    # print(response.json().get("access_token"))
    params = {
        "access_token": response.json().get("access_token"),
        "fields": "id,name,email,link",
    }

    response = requests.get(url, params=params)
    return response.json()


@auth_bp.route("/loginfb", methods=["GET", "POST"])
def loginfb():

    if "code" not in request.args:
        url = (
            "https://www.facebook.com/v3.0/dialog/oauth?client_id="
            + config.FB_CLIENT_ID
            + "&redirect_uri=https://"
            + config.DOMEN
            + "/loginfb&state=goldfishnetfacebooktoken&scope=email"
        )
        return redirect(url)

    elif "code" in request.args:
        user_social = oauthFacebook(request.args.get("code"))
        # Get user by username
        if "error" in user_social:
            return redirect(url_for("login"))

        user = User.query.filter_by(fb_id=user_social.get("id")).first()

        if user is not None:
            login_user(user)

            # flash('Ви ввійшли на сайт', 'success')
            return redirect(url_for("index"))

        else:
            user = User.query.filter_by(email=user_social.get("email")).first()

            if user is None:
                # Створюємо нового користувача
                user = User(
                    user_social.get("name"),
                    user_social.get("email"),
                    user_social.get("email"),
                )
                user.fb_id = user_social.get("id")
                # db.session.add(user)
                # db.session.commit()
                login_user(user)

                return redirect(url_for("index"))

            else:
                # error = 'Оновлено користувача'

                user.fb_id = user_social.get("id")
                login_user(user)
                return redirect(url_for("index"))

    return render_template("login.html")


# def login_save(user):
#     db.session.commit()
#     session['logged_in'] = True
#     session['username'] = user.username
#     session['name'] = user.name
#     session['user_id'] = user.id


# ============================================================ User Logout
@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("You are now logged out", "success")
    return redirect(url_for("index"))


# ===============================================================Login Google


def oauthGoogle(code):

    session = requests.Session()
    # session.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; rv:40.0) Gecko/20100101 Firefox/40.0'}
    session.headers = {"Content-Type": "db.lication/x-www-form-urlencoded"}
    # session.headers = {'Host:': 'www.googleapis.com'}
    # POST /oauth2/v4/token HTTP/1.1

    url = "https://www.googleapis.com/oauth2/v4/token"

    params = {
        "client_id": config.OAUTH_CLIENT_ID,
        "client_secret": config.OAUTH_SECRET,
        "redirect_uri": "https://" + config.DOMEN + "/logingl",
        "grant_type": "authorization_code",
        "code": code,
    }

    response = session.post(url, params=params)
    # print(response.json().get("access_token"))
    # access_token = "ya29.GlvnBRNFa3L86FP_ArgItbhC6SPq20Sfhx8bAcwaEFXGhg6Newt7b12d3b_zbaN20tcFbP_f_8VR0gzQLADYvMiwN1sIBuM7mNC0Kr1ifJq9_r5q7pncKQAjJdmw"

    url = "https://www.googleapis.com/oauth2/v1/userinfo"
    # print (response.json().get("access_token"))
    params = {
        "access_token": response.json().get("access_token"),
        "fields": "id,name,email",
    }

    response = requests.get(url, params=params)
    return response.json()


@auth_bp.route("/logingl", methods=["GET", "POST"])
def logingl():

    if "code" not in request.args:
        return redirect(
            f"https://accounts.google.com/o/oauth2/auth?redirect_uri=https://{config.DOMEN}/logingl&response_type=code&client_id="
            + config.OAUTH_CLIENT_ID
            + "&scope=https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile"
        )

    elif "code" in request.args:
        user_social = oauthGoogle(request.args.get("code"))
        # print (user_social)
        if "error" in user_social:
            return redirect(url_for("login"))

        user = User.query.filter_by(google_id=user_social.get("id")).first()

        if user is not None:

            login_user(user)
            return redirect(url_for("index"))

        else:
            user = User.query.filter_by(email=user_social.get("email")).first()
            if user is None:
                # error = 'Створено нового користувача'

                user = User(
                    user_social.get("name"),
                    user_social.get("email"),
                    user_social.get("email"),
                )
                user.google_id = user_social.get("id")
                # db.session.add(user)
                # db.session.commit()
                login_user(user)

                return redirect(url_for("index"))
            else:
                # error = 'Оновлено користувача'

                user.google_id = user_social.get("id")
                login_user(user)
                return redirect(url_for("index"))

    return render_template("login.html")
