import asyncio
import os

from app import create_app

# import app.presentation.views as views
# import app.presentation.admin as admin

os.environ["FLASK_RUN_FROM_CLI"] = "false"

app = create_app()

if __name__ == "__main__":
    # app.run(port=int("5000"), debug=True)

    os.environ["FLASK_RUN_FROM_CLI"] = "false"
    asyncio.run(app.run_async(debug=True))
