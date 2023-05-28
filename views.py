# -*- coding: utf-8 -*-
import os
import json
import requests

from flask import render_template, redirect, abort, url_for, session, request, flash, send_from_directory
from werkzeug.utils import secure_filename

import utilites
from app import app, db
from models import Article, Category, Users, Images
from functions import check_recaptcha, is_logged_in
from config import Config




# @app.errorhandler(404)
# def page_not_fount(e):
# 	redirect_url = Redirect.query.filter_by(url=request.path).first()
# 	if redirect_url != None:
# 		return redirect(request.url_root[:-1] + redirect_url.redirect_url)
# 	add_to_log404(request.path, request.referrer)
# 	return render_template('404.html'), 404


# ================================================ Home page
@app.route("/")
def index():
    # categoryes = Category.query.filter_by(id=1).all()
    
    # categoryes = db.scalars(db.select(Category))
    # categoryes = Article.query.all()
    categoryes = Category.query.all()
    print (categoryes)
    return render_template('index.html', CATEGORYES=categoryes)


# ================================================ Posts
@app.route("/<cat_name>/<alias>/")
@app.route("/<cat_name>/<alias>")
@app.route("/<cat_name>/")
@app.route("/<cat_name>")
def posts(cat_name="", alias=""):
    categoryes = Category.query.all()
    category = Category.query.filter_by(alias=cat_name).first()
    if category is None:
        print("##### Категорiя '{category}' не знайдена #####".format(category=category))
        return redirect(abort(404))

    if alias == "":
        articles = Article.query.filter_by(cat_id=category.id)
        return render_template("/articles.html", ARTICLES=articles, CATEGORY=category, CATEGORYES=categoryes)

    article = Article.query.filter_by(alias=alias).first()
    if article is None:
        print("##### Публiкацiя '{alias}' не знайдена #####".format(alias=alias))
        return redirect(abort(404))

    return render_template("/article.html", ARTICLE=article, CATEGORYES=categoryes)


# ================================================ User Login
@app.route('/login', methods=['GET', 'POST'])
#@check_recaptcha
def login():
    categoryes = Category.query.all()
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Get user by username
        user = Users.query.filter_by(username=username).first()

        if user is not None:
            # Compare Passwords
            if password_candidate == user.password:

                flash('You are now logged in', 'success')
                session['logged_in'] = True
                session['username'] = user.username
                session['name'] = user.name
                session['user_id'] = user.id

                return redirect("/admin")

            else:
                error = 'Невiрний пароль чи логiн'
                return render_template('login.html', error=error)
        else:
            error = 'Користувач не знайдений'
            return render_template('login.html', error=error, CATEGORYES=categoryes, CONFIG=Config)

    return render_template('login.html', CATEGORYES=categoryes, CONFIG=Config)


# ===============================================================Login Facebook
def oauthFacebook(code):

    url = "https://graph.facebook.com/oauth/access_token"

    params = {
        "client_id": Config.FB_CLIENT_ID,
        "client_secret": Config.FB_SECRET,
        "redirect_uri": "https://" + Config.domen + "/loginfb",
        "code": code}

    response = requests.get(url, params=params)
    url = "https://graph.facebook.com/me"

    # print(response.json().get("access_token"))
    params = {
        "access_token": response.json().get("access_token"),
        "fields": "id,name,email,link"}

    response = requests.get(url, params=params)
    return response.json()


@app.route('/loginfb', methods=['GET', 'POST'])
def loginfb():

    if "code" not in request.args:
        url = "https://www.facebook.com/v3.0/dialog/oauth?client_id=" + Config.FB_CLIENT_ID + "&redirect_uri=https://" + Config.domen + "/loginfb&state=goldfishnetfacebooktoken&scope=email"
        return redirect(url)

    elif "code" in request.args:
        user_social = oauthFacebook(request.args.get("code"))
        # Get user by username
        if "error" in user_social:  
            return redirect(url_for('login'))

        user = Users.query.filter_by(fb_id=user_social.get("id")).first()

        if user is not None:
            login_save(user)

            # flash('Ви ввійшли на сайт', 'success')
            return redirect(url_for('index'))

        else:
            user = Users.query.filter_by(email=user_social.get("email")).first()

            if user is None:
                # Створюємо нового користувача
                user = Users(user_social.get("name"), user_social.get("email"), user_social.get("email"))
                user.fb_id = user_social.get("id")
                db.session.add(user)
                db.session.commit()
                login_save(user)

                return redirect(url_for('index'))

            else:
                # error = 'Оновлено користувача'

                user.fb_id = user_social.get("id")
                login_save(user)
                return redirect(url_for('index'))

    return render_template('login.html')


def login_save(user):
    db.session.commit()
    session['logged_in'] = True
    session['username'] = user.username
    session['name'] = user.name
    session['user_id'] = user.id


# ===============================================================Login Google
def oauthGoogle(code):

    session = requests.Session()
    # session.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; rv:40.0) Gecko/20100101 Firefox/40.0'}
    session.headers = {'Content-Type': 'db.lication/x-www-form-urlencoded'}
    # session.headers = {'Host:': 'www.googleapis.com'}
    # POST /oauth2/v4/token HTTP/1.1

    url = "https://www.googleapis.com/oauth2/v4/token"

    params = {
        "client_id": Config.OAUTH_CLIENT_ID,
        "client_secret": Config.OAUTH_SECRET,
        "redirect_uri": "https://" + Config.domen + "/logingl",
        "grant_type": "authorization_code",
        "code": code}

    response = session.post(url, params=params)
    # print(response.json().get("access_token"))
    # access_token = "ya29.GlvnBRNFa3L86FP_ArgItbhC6SPq20Sfhx8bAcwaEFXGhg6Newt7b12d3b_zbaN20tcFbP_f_8VR0gzQLADYvMiwN1sIBuM7mNC0Kr1ifJq9_r5q7pncKQAjJdmw"

    url = "https://www.googleapis.com/oauth2/v1/userinfo"
    # print (response.json().get("access_token"))
    params = {
        "access_token": response.json().get("access_token"),
        "fields": "id,name,email"}

    response = requests.get(url, params=params)
    return response.json()


@app.route('/logingl', methods=['GET', 'POST'])
def logingl():

    if "code" not in request.args:
        return redirect("https://accounts.google.com/o/oauth2/auth?redirect_uri=https://" + Config.domen + "/logingl&response_type=code&client_id=" + Config.OAUTH_CLIENT_ID + "&scope=https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile")

    elif "code" in request.args:
        user_social = oauthGoogle(request.args.get("code"))
        # print (user_social)
        if "error" in user_social:
            return redirect(url_for('login'))

        user = Users.query.filter_by(google_id=user_social.get("id")).first()

        if user is not None:

            login_save(user)           
            return redirect(url_for('index'))

        else:
            user = Users.query.filter_by(email=user_social.get("email")).first()
            if user is None:
                # error = 'Створено нового користувача'

                user = Users(user_social.get("name"), user_social.get("email"), user_social.get("email"))
                user.google_id = user_social.get("id")
                db.session.add(user)
                db.session.commit()
                login_save(user)

                return redirect(url_for('index'))
            else:
                # error = 'Оновлено користувача'

                user.google_id = user_social.get("id")
                login_save(user)
                return redirect(url_for('index'))

    return render_template('login.html')

# ============================================================ User Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('index'))


# ============================================================ Search
@app.route("/search", methods=['GET', 'POST'])
@app.route("/search/", methods=['GET', 'POST'])
def search():
    return render_template("/search.html", CATEGORYES=categoryes)


# ============================================================ Favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/img'), 'favicon.ico')


# ============================================================ Files
@app.route('/admin/check-file/<id>', methods=['GET', 'POST'])
def check_file(id=""):
    return render_template('file-browse.html', files=Images.query.all(), ARTICLE_ID=id)


@app.route('/admin/upload-file/<id>', methods=['GET', 'POST'])
def upload_file(id=""):
    JSON = {}
    if request.method == 'POST':
        files = request.files.getlist('upload')

        if files:

            # load_photo(files, path_image, 768, path_thumbnail, 150)
            filename = secure_filename(utilites.transliterate(files[0].filename, "."))
            input_image_folder = Config.full_images_folder + "/articles/" + str(id) + "/"

            if os.path.exists(input_image_folder):
                files[0].save(input_image_folder + filename)
            else:
                os.mkdir(input_image_folder)
                files[0].save(input_image_folder + filename)

            path = "/articles/" + str(id) + "/" + filename

            JSON["fileName"] = filename
            JSON["uploaded"] = 1
            JSON["url"] = Config.images_folder + path

            image = Images(filename, path, "", utilites.timeNow("u"), id)
            db.session.add(image)
            db.session.commit()

    JSON = json.dumps(JSON, ensure_ascii=True, indent=None, sort_keys=False)
    return JSON, {'Content-Type': 'text/json'}
