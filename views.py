import warnings
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from PIL import Image as PILImage
from PIL import UnidentifiedImageError
from sqlalchemy.orm import joinedload
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db
from models import Category, Image, Post, User
from recaptcha import verify_recaptcha

bp = Blueprint("main", __name__)
_DUMMY_PASSWORD_HASH = generate_password_hash("unused-password")


def render_page(template, **context):
    # Error pages must also render if the database is unavailable.
    context["CATEGORYES"] = db.session.scalars(db.select(Category).order_by(Category.name)).all()
    return render_template(template, **context)


@bp.get("/")
def index():
    return render_page("index.html")


@bp.get("/<cat_name>/", defaults={"alias": ""})
@bp.get("/<cat_name>", defaults={"alias": ""})
@bp.get("/<cat_name>/<alias>/")
@bp.get("/<cat_name>/<alias>")
def posts(cat_name, alias):
    category = db.first_or_404(db.select(Category).where(Category.alias == cat_name))
    if not alias:
        pages = db.paginate(
            db.select(Post)
            .where(Post.category_id == category.id)
            .options(joinedload(Post.category))
            .order_by(Post.id.desc()),
            per_page=current_app.config["POSTS_PER_PAGE"],
            max_per_page=100,
        )
        return render_page("posts.html", POSTS=pages.items, CATEGORY=category, PAGES=pages)
    post = db.first_or_404(
        db.select(Post)
        .where(Post.category_id == category.id, Post.alias == alias)
        .options(joinedload(Post.category))
    )
    post.add_hit()
    return render_page("post.html", POST=post)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.index"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not verify_recaptcha(request.form.get("g-recaptcha-response", "")):
            flash("Перевірка reCAPTCHA не пройдена. Спробуйте ще раз.", "danger")
            return render_page("login.html"), 400
        user = db.session.scalar(db.select(User).where(User.username == username))
        if user is None:
            check_password_hash(_DUMMY_PASSWORD_HASH, password)
        elif user.check_password(password):
            login_user(user)
            flash("Ви увійшли в систему.", "success")
            return redirect(url_for("admin.index"))
        flash("Невірний логін або пароль", "danger")
    return render_page("login.html")


@bp.post("/logout")
@login_required
def logout():
    logout_user()
    flash("Ви вийшли із системи.", "success")
    return redirect(url_for("main.index"))


@bp.get("/logout")
def logout_get():
    # Reserve the path so the category catch-all cannot handle this GET.
    abort(405)


@bp.get("/search/")
@bp.get("/search")
def search():
    return render_page("search.html")


@bp.get("/favicon.ico")
def favicon():
    return send_from_directory(Path(current_app.static_folder) / "img", "favicon.ico")


@bp.get("/media/<path:filename>")
def media(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)


@bp.get("/admin/check-file/<int:id>")
@login_required
def check_file(id):
    db.get_or_404(Post, id)
    files = db.session.scalars(db.select(Image).order_by(Image.id.desc())).all()
    return render_template("file-browse.html", files=files, POST_ID=id)


@bp.post("/admin/upload-file/<int:id>")
@login_required
def upload_file(id):
    db.get_or_404(Post, id)
    file = request.files.get("upload")
    # The display name may be Ukrainian; the actual disk path uses only a UUID.
    filename = (file.filename or "").replace("\\", "/").rsplit("/", 1)[-1] if file else ""
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if not filename or extension not in current_app.config["ALLOWED_EXTENSIONS"]:
        return jsonify(uploaded=0, error={"message": "Choose a PNG, JPEG, GIF or WebP image."}), 400
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", PILImage.DecompressionBombWarning)
            with PILImage.open(file.stream) as image:
                expected = {
                    "png": "PNG",
                    "jpg": "JPEG",
                    "jpeg": "JPEG",
                    "gif": "GIF",
                    "webp": "WEBP",
                }
                if image.format != expected[extension]:
                    raise ValueError("Image content does not match its extension")
                image.verify()
    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
        PILImage.DecompressionBombError,
        PILImage.DecompressionBombWarning,
    ):
        return jsonify(uploaded=0, error={"message": "Invalid image."}), 400

    file.stream.seek(0)
    relative = f"posts/{id}/{uuid4().hex}.{extension}"
    destination = Path(current_app.config["UPLOAD_FOLDER"]) / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        file.save(destination)
        db.session.add(
            Image(
                name=filename[:64],
                path=relative,
                type=extension,
                create_date=datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
                post_id=id,
            )
        )
        db.session.commit()
    except Exception:
        db.session.rollback()
        destination.unlink(missing_ok=True)
        raise
    return jsonify(fileName=filename, uploaded=1, url=url_for("main.media", filename=relative))
