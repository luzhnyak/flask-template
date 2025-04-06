import asyncio
import os

from app import create_app, init_db

# import app.presentation.views as views
# import app.presentation.admin as admin

os.environ["FLASK_RUN_FROM_CLI"] = "false"

app = create_app()

if __name__ == "__main__":    
    asyncio.run(init_db())
    
    app.run(port=int("5000"), debug=True)
    # asyncio.run(app.run_async(debug=True))
    # asyncio.run(app.run_async(debug=True, port=5000))
