from fastapi import FastAPI

from sqlalchemy import text
from database import engine

app = FastAPI()

@app.get("/")
def home():
    return {"message": "CheatPeeper backend is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/db-check")
def database_check():
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT current_database()")
        )
        database_name = result.scalar_one()

    return {
        "status": "connected",
        "database": database_name
    }
