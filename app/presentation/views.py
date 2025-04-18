import os
import json

from app.services.image import get_image_service
from app.services.post import get_post_service

from flask import (
    Blueprint,
    render_template,
    redirect,
    abort,
    request,
)
from werkzeug.utils import secure_filename

import app.utils.utilites as utilites

from app.infrastructure.models import Post, Category, User, Image
from config import config


views_bp = Blueprint("views", __name__)


# @app.errorhandler(404)
# def page_not_fount(e):
#     redirect_url = Redirect.query.filter_by(url=request.path).first()
#     if redirect_url != None:
#         return redirect(request.url_root[:-1] + redirect_url.redirect_url)
#     add_to_log404(request.path, request.referrer)
#     return render_template("404.html"), 404


# ================================================ Home page
@views_bp.route("/")
def index():
    return render_template("index.html")


# ================================================ Posts
@views_bp.route("/posts/<slug>")
@views_bp.route("/posts/")
@views_bp.route("/posts")
async def post(slug=""):
    if slug == "":
        async with get_post_service() as user_service:
            posts = await user_service.get_posts()
        return render_template("/articles.html", POSTS=posts)

    async with get_post_service() as user_service:
        post = await user_service.get_post_by_slug(slug=slug)

    if post is None:
        return redirect(abort(404))

    return render_template("/article.html", POST=post)


# ============================================================ Search
@views_bp.route("/search", methods=["GET", "POST"])
@views_bp.route("/search/", methods=["GET", "POST"])
def search():
    return render_template("/search.html")


# ============================================================ Files
@views_bp.route("/admin/check-file/<id>", methods=["GET", "POST"])
async def check_file(id=""):
    async with get_image_service() as image_service:
        files = await image_service.get_images_by_post_id(id)
    return render_template("file-browse.html", files=files, ARTICLE_ID=id)


@views_bp.route("/admin/upload-file/<id>", methods=["GET", "POST"])
async def upload_file(id=""):
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

            async with get_image_service() as image_service:
                await image_service.create_image(filename, path, "")

    JSON = json.dumps(JSON, ensure_ascii=True, indent=None, sort_keys=False)
    return JSON, {"Content-Type": "text/json"}
