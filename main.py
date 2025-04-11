import asyncio

from app import create_app, init_db

app = create_app()

if __name__ == "__main__":
    asyncio.run(init_db())

    app.run(port=int("5000"), debug=True)
