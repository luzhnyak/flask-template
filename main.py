from app import create_app
import app.presentation.views as views
import app.presentation.admin as admin


app = create_app()

if __name__ == "__main__":
    app.run(port=int("5000"), debug=True)
