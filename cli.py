import click

from extensions import db
from models import User


def register_commands(app):
    @app.cli.command("init-db")
    def init_db():
        """Create missing tables without deleting existing data."""
        db.create_all()
        click.echo("Database initialized.")

    @app.cli.command("create-admin")
    @click.option("--username", prompt=True)
    @click.option("--email", prompt=True)
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
    def create_admin(username, email, password):
        """Create an administrator. All accounts have admin access."""
        username, email = username.strip(), email.strip()
        if not username or not email or len(password) < 8:
            raise click.ClickException(
                "Username and email are required; password must have at least 8 characters."
            )
        exists = db.session.scalar(
            db.select(User).where(db.or_(User.username == username, User.email == email))
        )
        if exists:
            raise click.ClickException("Username or email already exists.")
        user = User(name=username, username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo("Administrator created.")

    @app.cli.command("set-password")
    @click.argument("username")
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
    def set_password(username, password):
        """Replace a password, including a legacy plaintext password."""
        user = db.session.scalar(db.select(User).where(User.username == username))
        if user is None:
            raise click.ClickException("User not found.")
        if len(password) < 8:
            raise click.ClickException("Password must have at least 8 characters.")
        user.set_password(password)
        db.session.commit()
        click.echo("Password updated.")
