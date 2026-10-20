import io
import re

import pytest
from PIL import Image

from extensions import db
from models import Images


def csrf_token(client, path="/login"):
    response = client.get(path)
    match = re.search(rb'name="csrf_token"[^>]*value="([^"]+)"', response.data)
    assert match, "Form must contain a CSRF token"
    return match.group(1).decode()


def picture():
    buffer = io.BytesIO()
    Image.new("RGB", (3, 3), "green").save(buffer, "PNG")
    buffer.seek(0)
    return buffer


@pytest.mark.parametrize(
    "path",
    [
        "/admin/",
        "/admin/article/",
        "/admin/article/new/",
        "/admin/category/",
        "/admin/images/",
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
        assert db.session.scalar(db.select(db.func.count()).select_from(Images)) == 0


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


def test_article_must_belong_to_url_category(client):
    assert client.get("/other/article-0").status_code == 404
    assert client.get("/fishing/article-0").status_code == 200


def test_category_paginates(client):
    response = client.get("/fishing?page=1")
    assert b"Article 2" in response.data
    assert b"Article 0" not in response.data
    assert b"Article 0" in client.get("/fishing?page=2").data
    assert client.get("/fishing?page=100").status_code == 404


def test_missing_pages_are_404(client):
    assert client.get("/unknown").status_code == 404
    assert client.get("/fishing/unknown").status_code == 404


@pytest.mark.parametrize(
    "path",
    ["/admin/", "/admin/article/", "/admin/article/new/", "/admin/category/", "/admin/images/"],
)
def test_authenticated_admin_pages_render(authenticated, path):
    assert authenticated.get(path).status_code == 200


def test_admin_create_form_is_create_not_edit(authenticated):
    response = authenticated.get("/admin/article/new/")
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
    assert authenticated.get(payload["url"]).status_code == 200
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count()).select_from(Images)) == 1


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


def test_upload_rejects_missing_article(authenticated):
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


def test_admin_can_create_edit_and_delete_article(authenticated, app):
    token = csrf_token(authenticated, "/admin/article/new/")
    response = authenticated.post(
        "/admin/article/new/",
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
    from models import Article

    article = db.session.scalar(db.select(Article).where(Article.title == "Нова стаття"))
    assert article is not None
    assert article.alias == "nova-stattia"
    response = authenticated.post(
        f"/admin/article/edit/?id={article.id}",
        data={
            "csrf_token": token,
            "category": "1",
            "title": "Updated",
            "alias": article.alias,
            "textbody": "Updated text",
            "main_image": "",
        },
    )
    assert response.status_code == 302
    assert b"Updated text" in authenticated.get("/fishing/nova-stattia").data
    article_id = article.id
    response = authenticated.post(
        "/admin/article/delete/", data={"csrf_token": token, "id": article_id}
    )
    assert response.status_code == 302
    assert db.session.get(Article, article_id) is None


def test_category_with_articles_cannot_be_deleted(authenticated):
    token = csrf_token(authenticated, "/")
    authenticated.post("/admin/category/delete/", data={"csrf_token": token, "id": 1})
    from models import Category

    assert db.session.get(Category, 1) is not None


def test_admin_rejects_duplicate_alias(authenticated):
    token = csrf_token(authenticated, "/admin/article/new/")
    response = authenticated.post(
        "/admin/article/new/",
        data={
            "csrf_token": token,
            "category": "1",
            "title": "Duplicate",
            "alias": "article-0",
            "textbody": "Body",
        },
    )
    assert response.status_code == 200
    from models import Article

    assert db.session.scalar(db.select(db.func.count()).select_from(Article)) == 3


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
    from models import Users

    user = db.session.get(Users, 1)
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


def test_empty_article_body_renders(client):
    from models import Article

    article = db.session.get(Article, 1)
    article.textbody = None
    db.session.commit()
    assert client.get("/fishing/article-0").status_code == 200


def test_cli_creates_admin_and_resets_legacy_password(app):
    runner = app.test_cli_runner()
    assert runner.invoke(args=["init-db"]).exit_code == 0
    result = runner.invoke(
        args=["create-admin", "--username", "second", "--email", "second@example.test"],
        input="a-long-password\na-long-password\n",
    )
    assert result.exit_code == 0, result.output
    from models import Users

    user = db.session.scalar(db.select(Users).where(Users.username == "second"))
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
    assert db.session.scalar(db.select(db.func.count()).select_from(Images)) == 0


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
