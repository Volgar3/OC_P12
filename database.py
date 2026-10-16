import os

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()


def get_env(name):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Variable d'environnement manquante : {name} (voir .env.example)")
    return value


def build_url(account="APP"):
    return URL.create(
        drivername="postgresql+psycopg",
        username=get_env(f"DB_{account}_USER"),
        password=get_env(f"DB_{account}_PASSWORD"),
        host=get_env("DB_HOST"),
        port=int(get_env("DB_PORT")),
        database=get_env("DB_NAME"),
    )


engine = create_engine(build_url("APP"))
Session = sessionmaker(bind=engine)


def check_connection():
    with engine.connect() as connection:
        return connection.execute(
            text("SELECT current_user, current_database(), current_setting('server_version')")
        ).one()


if __name__ == "__main__":
    user, database, version = check_connection()
    print(f"Connexion OK : {user} sur la base {database} (PostgreSQL {version})")
