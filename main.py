from app import app
import views
import admin
from config import Config

app.run(port=int("5000"), debug=True)
