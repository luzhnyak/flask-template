import io
import re

import pytest
from PIL import Image as PILImage

from extensions import db
from models import Image


def csrf_token(client, path="/login"):
    response = client.get(path)
    match = re.search(rb'name="csrf_token"[^>]*value="([^"]+)"', response.data)
    assert match, "Form must contain a CSRF token"
    return match.group(1).decode()


def picture():
    buffer = io.BytesIO()
    PILImage.new("RGB", (3, 3), "green").save(buffer, "PNG")
    buffer.seek(0)
    return buffer


@pytest.mark.parametrize(
    "path",
    [
        "/admin/",
        "/admin/post/",
        "/admin/post/new/",
        "/admin/category/",
        "/admin/image/",
        "/admin/check-file/1",
    ],
)
def test_admin_requires_login(client, path):
    response = client.get(path)
    assert response.status_code == 302
    assert "/login" in response.location


def test_upload_requires_login(client):
    response = client.post("/admin/upload-file/1", data={"upload": (picture(), "fish.png")})
    assert response.status_code in (302, 400)
    with client.application.app_context():
        assert db.session.scalar(db.select(db.func.count()).select_from(Image)) == 0


def test_login_requires_csrf(client):
    response = client.post("/login", data={"username": "admin", "password": "correct-password"})
    assert response.status_code == 400


def test_hashed_password_login(client):
    response = client.post(
        "/login",
        data={
            "username": "admin",
            "password": "correct-password",
            "csrf_token": csrf_token(client),
        },
    )
    assert response.status_code == 302
    assert "/admin" in response.location
    assert client.get("/admin/").status_code == 200


def test_login_errors_do_not_reveal_user_or_password(client):
    token = csrf_token(client)
    bodies = []
    for username in ("admin", "missing"):
        response = client.post(
            "/login",
            data={
                "username": username,
                "password": "private-password",
                "csrf_token": token,
            },
        )
        assert "Невірний логін або пароль".encode() in response.data
        assert b"private-password" not in response.data
        bodies.append(response.status_code)
    assert bodies[0] == bodies[1]


def test_logout_is_post_only(authenticated):
    assert authenticated.get("/logout").status_code == 405
    response = authenticated.post("/logout", data={"csrf_token": csrf_token(authenticated, "/")})
    assert response.status_code == 302
    assert authenticated.get("/admin/").status_code == 302


def test_post_must_belong_to_url_category(client):
    assert client.get("/other/post-0").status_code == 404
    assert client.get("/fishing/post-0").status_code == 200


def test_category_paginates(client):
    response = client.get("/fishing?page=1")
    assert b"Post 2" in response.data
    assert b"Post 0" not in response.data
    assert b"Post 0" in client.get("/fishing?page=2").data
    assert client.get("/fishing?page=100").status_code == 404


def test_missing_pages_are_404(client):
    assert client.get("/unknown").status_code == 404
    assert client.get("/fishing/unknown").status_code == 404


@pytest.mark.parametrize(
    "path",
    ["/admin/", "/admin/post/", "/admin/post/new/", "/admin/category/", "/admin/image/"],
)
def test_authenticated_admin_pages_render(authenticated, path):
    assert authenticated.get(path).status_code == 200


def test_admin_create_form_is_create_not_edit(authenticated):
    response = authenticated.get("/admin/post/new/")
    assert b'name="csrf_token"' in response.data
    assert b"/static/js/admin.js" in response.data


def test_upload_valid_image(authenticated, app):
    response = authenticated.post(
        "/admin/upload-file/1",
        data={
            "upload": (picture(), "fish.png"),
            "csrf_token": csrf_token(authenticated, "/"),
        },
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["uploaded"] == 1
    assert payload["url"].startswith("/media/posts/1/")
    assert authenticated.get(payload["url"]).status_code == 200
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count()).select_from(Image)) == 1
        image = db.session.scalar(db.select(Image))
        assert image.post_id == 1
        assert payload["url"].encode() in authenticated.get("/admin/check-file/1").data


def test_upload_rejects_non_image(authenticated):
    response = authenticated.post(
        "/admin/upload-file/1",
        data={
            "upload": (io.BytesIO(b"not an image"), "fish.png"),
            "csrf_token": csrf_token(authenticated, "/"),
        },
    )
    assert response.status_code == 400
    assert response.get_json()["uploaded"] == 0


def test_upload_rejects_missing_post(authenticated):
    response = authenticated.post(
        "/admin/upload-file/999",
        data={
            "upload": (picture(), "fish.png"),
            "csrf_token": csrf_token(authenticated, "/"),
        },
    )
    assert response.status_code == 404


def test_upload_requires_csrf(authenticated):
    response = authenticated.post("/admin/upload-file/1", data={"upload": (picture(), "fish.png")})
    assert response.status_code == 400


def test_missing_asset_does_not_return_html(client):
    assert client.get("/static/js/admin.js").status_code == 200


def test_login_ignores_external_next(client):
    response = client.post(
        "/login?next=https://evil.example/",
        data={
            "username": "admin",
            "password": "correct-password",
            "csrf_token": csrf_token(client),
        },
    )
    assert response.status_code == 302
    assert response.location.startswith("/")


def test_admin_can_create_edit_and_delete_post(authenticated, app):
    token = csrf_token(authenticated, "/admin/post/new/")
    response = authenticated.post(
        "/admin/post/new/",
        data={
            "csrf_token": token,
            "category": "1",
            "title": "Нова стаття",
            "alias": "",
            "textbody": "<p>New body</p>",
            "main_image": "",
        },
    )
    assert response.status_code == 302
    from models import Post

    post = db.session.scalar(db.select(Post).where(Post.title == "Нова стаття"))
    assert post is not None
    assert post.alias == "nova-stattia"
    response = authenticated.post(
        f"/admin/post/edit/?id={post.id}",
        data={
            "csrf_token": token,
            "category": "1",
            "title": "Updated",
            "alias": post.alias,
            "textbody": "Updated text",
            "main_image": "",
        },
    )
    assert response.status_code == 302
    assert b"Updated text" in authenticated.get("/fishing/nova-stattia").data
    post_id = post.id
    response = authenticated.post("/admin/post/delete/", data={"csrf_token": token, "id": post_id})
    assert response.status_code == 302
    assert db.session.get(Post, post_id) is None


def test_category_with_posts_cannot_be_deleted(authenticated):
    token = csrf_token(authenticated, "/")
    authenticated.post("/admin/category/delete/", data={"csrf_token": token, "id": 1})
    from models import Category

    assert db.session.get(Category, 1) is not None


def test_admin_rejects_duplicate_alias(authenticated):
    token = csrf_token(authenticated, "/admin/post/new/")
    response = authenticated.post(
        "/admin/post/new/",
        data={
            "csrf_token": token,
            "category": "1",
            "title": "Duplicate",
            "alias": "post-0",
            "textbody": "Body",
        },
    )
    assert response.status_code == 200
    from models import Post

    assert db.session.scalar(db.select(db.func.count()).select_from(Post)) == 3


def test_upload_collision_does_not_overwrite(authenticated, app):
    token = csrf_token(authenticated, "/")
    urls = []
    for _ in range(2):
        response = authenticated.post(
            "/admin/upload-file/1",
            data={
                "upload": (picture(), "same.png"),
                "csrf_token": token,
            },
        )
        assert response.status_code == 200
        urls.append(response.get_json()["url"])
    assert urls[0] != urls[1]
    assert all(authenticated.get(url).status_code == 200 for url in urls)


def test_upload_limit_returns_json(authenticated, app):
    token = csrf_token(authenticated, "/")
    app.config["MAX_CONTENT_LENGTH"] = 1024
    response = authenticated.post(
        "/admin/upload-file/1",
        data={
            "upload": (io.BytesIO(b"x" * 2048), "fish.png"),
            "csrf_token": token,
        },
    )
    assert response.status_code == 413
    assert response.get_json()["uploaded"] == 0


def test_media_cannot_escape_upload_folder(client, app, tmp_path):
    (tmp_path / "secret.txt").write_text("private")
    assert client.get("/media/../secret.txt").status_code == 404


def test_plaintext_password_is_rejected(client):
    from models import User

    user = db.session.get(User, 1)
    user.password = "plaintext-password"
    db.session.commit()
    response = client.post(
        "/login",
        data={
            "username": "admin",
            "password": "plaintext-password",
            "csrf_token": csrf_token(client),
        },
    )
    assert response.status_code == 200
    assert client.get("/admin/").status_code == 302


def test_recaptcha_failure_blocks_login(client, app):
    app.config["GOOGLE_RECAPTCHA_SECRET_KEY"] = "test-secret"
    response = client.post(
        "/login",
        data={
            "username": "admin",
            "password": "correct-password",
            "csrf_token": csrf_token(client),
        },
    )
    assert response.status_code == 400
    assert client.get("/admin/").status_code == 302


def test_empty_post_body_renders(client):
    from models import Post

    post = db.session.get(Post, 1)
    post.textbody = None
    db.session.commit()
    assert client.get("/fishing/post-0").status_code == 200


def test_cli_creates_admin_and_resets_legacy_password(app):
    runner = app.test_cli_runner()
    assert runner.invoke(args=["init-db"]).exit_code == 0
    result = runner.invoke(
        args=["create-admin", "--username", "second", "--email", "second@example.test"],
        input="a-long-password\na-long-password\n",
    )
    assert result.exit_code == 0, result.output
    from models import User

    user = db.session.scalar(db.select(User).where(User.username == "second"))
    assert user.password != "a-long-password"
    assert user.check_password("a-long-password")
    result = runner.invoke(
        args=["create-admin", "--username", "second", "--email", "second@example.test"],
        input="a-long-password\na-long-password\n",
    )
    assert result.exit_code != 0
    result = runner.invoke(
        args=["set-password", "second"], input="replacement-password\nreplacement-password\n"
    )
    assert result.exit_code == 0
    assert user.check_password("replacement-password")


def test_logout_get_is_rejected_for_anonymous_user(client):
    assert client.get("/logout").status_code == 405


def test_upload_accepts_ukrainian_filename(authenticated):
    response = authenticated.post(
        "/admin/upload-file/1",
        data={
            "upload": (picture(), "щука.png"),
            "csrf_token": csrf_token(authenticated, "/"),
        },
    )
    assert response.status_code == 200


def test_upload_rolls_back_file_on_database_error(authenticated, app, monkeypatch):
    from pathlib import Path

    from sqlalchemy.exc import SQLAlchemyError

    token = csrf_token(authenticated, "/")

    def broken_commit():
        raise SQLAlchemyError("Simulated database failure")

    monkeypatch.setattr(db.session, "commit", broken_commit)
    with pytest.raises(SQLAlchemyError):
        authenticated.post(
            "/admin/upload-file/1",
            data={
                "upload": (picture(), "fish.png"),
                "csrf_token": token,
            },
        )
    assert list(Path(app.config["UPLOAD_FOLDER"]).rglob("*.png")) == []
    assert db.session.scalar(db.select(db.func.count()).select_from(Image)) == 0


def test_error_page_can_render_when_database_is_unavailable(client, app, monkeypatch):
    from sqlalchemy.exc import SQLAlchemyError

    app.config.update(TESTING=False)

    def broken_execute(*args, **kwargs):
        raise SQLAlchemyError("Simulated database failure")

    monkeypatch.setattr(db.session, "scalars", broken_execute)
    response = client.get("/")
    assert response.status_code == 500
    assert "Внутрішня помилка сервера".encode() in response.data


def test_slug_has_no_empty_segments():
    from utils import transliterate

    assert transliterate("  Щука та окунь!  ") == "shchuka-ta-okun"


def test_error_page_does_not_load_user_from_unavailable_database(authenticated, app, monkeypatch):
    from sqlalchemy.exc import SQLAlchemyError

    app.config["TESTING"] = False

    def broken_query(*args, **kwargs):
        raise SQLAlchemyError("Simulated database failure")

    monkeypatch.setattr(db.session, "scalars", broken_query)
    monkeypatch.setattr(db.session, "get", broken_query)
    response = authenticated.get("/")
    assert response.status_code == 500
    assert "Внутрішня помилка сервера".encode() in response.data


def test_schema_uses_plural_table_names(app):
    from sqlalchemy import inspect

    assert set(inspect(db.engine).get_table_names()) == {"posts", "images", "users", "categories"}


def test_model_names_are_singular():
    import models

    for name in ("Post", "Image", "User", "Category"):
        assert hasattr(models, name)
    assert not any(hasattr(models, name) for name in ("Article", "Images", "Users"))


@pytest.mark.parametrize("command", ["create-admin", "set-password"])
@pytest.mark.parametrize("password,accepted", [("1234567", False), ("12345678", True)])
def test_cli_password_minimum_is_eight(app, command, password, accepted):
    if command == "create-admin":
        args = [command, "--username", "eight", "--email", "eight@example.test"]
    else:
        args = [command, "admin"]
    result = app.test_cli_runner().invoke(args=args, input=f"{password}\n{password}\n")
    assert (result.exit_code == 0) is accepted, result.output


def test_debug_disables_recaptcha_widget_and_server_check(client, app, monkeypatch):
    import requests

    app.config.update(
        DEBUG=True, GOOGLE_RECAPTCHA_SITE_KEY="site", GOOGLE_RECAPTCHA_SECRET_KEY="secret"
    )

    def unexpected_request(*args, **kwargs):
        pytest.fail("reCAPTCHA must not contact Google in debug mode")

    monkeypatch.setattr(requests, "post", unexpected_request)
    response = client.get("/login")
    assert b"g-recaptcha" not in response.data
    assert b"google.com/recaptcha" not in response.data
    response = client.post(
        "/login",
        data={
            "username": "admin",
            "password": "correct-password",
            "csrf_token": csrf_token(client),
        },
    )
    assert response.status_code == 302
    assert client.get("/admin/").status_code == 200


def test_media_folder_is_in_project_root():
    from pathlib import Path

    from config import BASE_DIR, Config

    assert Path(Config.UPLOAD_FOLDER) == BASE_DIR / "media"


@pytest.mark.parametrize("debug", [True, False])
def test_recaptcha_key_validation_is_disabled_only_in_debug(tmp_path, debug):
    from app import create_app

    config = {
        "SECRET_KEY": "test-secret",
        "DEBUG": debug,
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
        "UPLOAD_FOLDER": str(tmp_path / "media"),
        "GOOGLE_RECAPTCHA_SITE_KEY": "site",
        "GOOGLE_RECAPTCHA_SECRET_KEY": "",
    }
    if debug:
        assert create_app(config).debug is True
    else:
        with pytest.raises(RuntimeError, match="both reCAPTCHA keys"):
            create_app(config)


def test_production_keeps_recaptcha_enabled(client, app):
    app.config.update(
        DEBUG=False, GOOGLE_RECAPTCHA_SITE_KEY="site", GOOGLE_RECAPTCHA_SECRET_KEY="secret"
    )
    response = client.get("/login")
    assert b"g-recaptcha" in response.data
    assert b"google.com/recaptcha" in response.data


def test_post_with_uploaded_image_can_be_deleted(authenticated, app):
    from models import Post

    db.session.execute(db.text("PRAGMA foreign_keys=ON"))
    assert db.session.scalar(db.text("PRAGMA foreign_keys")) == 1
    token = csrf_token(authenticated, "/")
    uploaded = authenticated.post(
        "/admin/upload-file/1",
        data={
            "upload": (picture(), "fish.png"),
            "csrf_token": token,
        },
    )
    assert uploaded.status_code == 200
    response = authenticated.post("/admin/post/delete/", data={"id": 1, "csrf_token": token})
    assert response.status_code == 302
    assert db.session.get(Post, 1) is None
    assert authenticated.get(uploaded.get_json()["url"]).status_code == 200
