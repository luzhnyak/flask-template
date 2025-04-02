import os
import json
import requests

from flask import (
    Blueprint,
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

import app.utils.utilites as utilites
from app import db
from app.infrastructure.models import Post, Category, User, Image
from config import config

views_bp = Blueprint("views", __name__)

# @app.errorhandler(404)
# def page_not_fount(e):
# 	redirect_url = Redirect.query.filter_by(url=request.path).first()
# 	if redirect_url != None:
# 		return redirect(request.url_root[:-1] + redirect_url.redirect_url)
# 	add_to_log404(request.path, request.referrer)
# 	return render_template('404.html'), 404


# ================================================ Home page
@views_bp.route("/")
def index():
    return render_template("index.html")


# ================================================ Posts
@views_bp.route("/posts/<slug>")
@views_bp.route("/posts/")
@views_bp.route("/posts")
def post(slug=""):
    if slug == "":
        posts = Post.query.all()
        return render_template(
            "/articles.html",
            POSTS=posts,
        )

    post = Post.query.filter_by(slug=slug).first()

    if post is None:
        return redirect(abort(404))

    article = Post.query.filter_by(slug=slug).first()
    if article is None:
        return redirect(abort(404))

    return render_template("/article.html", POST=post)


# ============================================================ Search
@views_bp.route("/search", methods=["GET", "POST"])
@views_bp.route("/search/", methods=["GET", "POST"])
def search():
    return render_template("/search.html")


# ============================================================ Files
@views_bp.route("/admin/check-file/<id>", methods=["GET", "POST"])
def check_file(id=""):
    return render_template("file-browse.html", files=Image.query.all(), ARTICLE_ID=id)


@views_bp.route("/admin/upload-file/<id>", methods=["GET", "POST"])
def upload_file(id=""):
    JSON = {}
    if request.method == "POST":
        files = request.files.getlist("upload")

        if files:

            # load_photo(files, path_image, 768, path_thumbnail, 150)
            filename = secure_filename(utilites.transliterate(files[0].filename, "."))
            input_image_folder = (
                config.full_images_folder + "/articles/" + str(id) + "/"
            )

            if os.path.exists(input_image_folder):
                files[0].save(input_image_folder + filename)
            else:
                os.mkdir(input_image_folder)
                files[0].save(input_image_folder + filename)

            path = "/articles/" + str(id) + "/" + filename

            JSON["fileName"] = filename
            JSON["uploaded"] = 1
            JSON["url"] = config.images_folder + path

            image = Image(filename, path, "", utilites.timeNow("u"), id)
            db.session.add(image)
            db.session.commit()

    JSON = json.dumps(JSON, ensure_ascii=True, indent=None, sort_keys=False)
    return JSON, {"Content-Type": "text/json"}
