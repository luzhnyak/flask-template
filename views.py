import os
import json
import requests

from flask import (
    render_template,
    redirect,
    abort,
    url_for,
    request,
    flash,
    send_from_directory,
)
from werkzeug.utils import secure_filename
from flask_login import current_user, login_user, logout_user

import utilites
from app import app, db
from models import Article, Category, Users, Images
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
    print(categoryes)
    return render_template("index.html", CATEGORYES=categoryes)


# ================================================ Posts
@app.route("/<cat_name>/<alias>/")
@app.route("/<cat_name>/<alias>")
@app.route("/<cat_name>/")
@app.route("/<cat_name>")
def posts(cat_name="", alias=""):
    categoryes = Category.query.all()
    category = Category.query.filter_by(alias=cat_name).first()
    if category is None:
        print(
            "##### Категорiя '{category}' не знайдена #####".format(category=category)
        )
        return redirect(abort(404))

    if alias == "":
        articles = Article.query.filter_by(cat_id=category.id)
        return render_template(
            "/articles.html",
            ARTICLES=articles,
            CATEGORY=category,
            CATEGORYES=categoryes,
        )

    article = Article.query.filter_by(alias=alias).first()
    if article is None:
        print("##### Публiкацiя '{alias}' не знайдена #####".format(alias=alias))
        return redirect(abort(404))

    return render_template("/article.html", ARTICLE=article, CATEGORYES=categoryes)


# ================================================ User Login
@app.route("/login", methods=["GET", "POST"])
# @check_recaptcha
def login():
    categoryes = Category.query.all()
    if request.method == "POST":
        # Get Form Fields
        username = request.form["username"]
        password_candidate = request.form["password"]

        # Get user by username
        user = Users.query.filter_by(username=username).first()

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
            return render_template(
                "login.html", error=error, CATEGORYES=categoryes, CONFIG=Config
            )

    return render_template("login.html", CATEGORYES=categoryes, CONFIG=Config)


# ============================================================ User Logout
@app.route("/logout")
def logout():
    logout_user()
    flash("You are now logged out", "success")
    return redirect(url_for("index"))


# ============================================================ Search
@app.route("/search", methods=["GET", "POST"])
@app.route("/search/", methods=["GET", "POST"])
def search():
    return render_template("/search.html")


# ============================================================ Favicon
@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path, "static/img"), "favicon.ico")


# ============================================================ Files
@app.route("/admin/check-file/<id>", methods=["GET", "POST"])
def check_file(id=""):
    return render_template("file-browse.html", files=Images.query.all(), ARTICLE_ID=id)


@app.route("/admin/upload-file/<id>", methods=["GET", "POST"])
def upload_file(id=""):
    JSON = {}
    if request.method == "POST":
        files = request.files.getlist("upload")

        if files:

            # load_photo(files, path_image, 768, path_thumbnail, 150)
            filename = secure_filename(utilites.transliterate(files[0].filename, "."))
            input_image_folder = (
                Config.full_images_folder + "/articles/" + str(id) + "/"
            )

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
    return JSON, {"Content-Type": "text/json"}
