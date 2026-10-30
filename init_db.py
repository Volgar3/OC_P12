"""Initialise la base de données du CRM Epic Events.

À lancer après avoir rempli le fichier .env (voir .env.example). Le script :
1. crée les comptes PostgreSQL propriétaire et applicatif, avec les mots de passe du .env ;
2. crée la base et ne donne au compte applicatif que les droits nécessaires ;
3. lance seed.py, qui crée les tables puis insère les départements et leurs permissions.

Il peut être relancé sans risque : rien n'est recréé s'il existe déjà. Pour changer
le mot de passe d'un compte, modifier le .env puis relancer le script.
"""

import os
import sys

import psycopg
from psycopg import sql

import seed
from database import get_env


def admin_connection(dbname):
    """Ouvre une connexion super-utilisateur sur la base `dbname` (autocommit)."""
    return psycopg.connect(
        host=get_env("DB_HOST"),
        port=get_env("DB_PORT"),
        user=get_env("DB_ADMIN_USER"),
        password=os.getenv("DB_ADMIN_PASSWORD") or None,
        dbname=dbname,
        autocommit=True,
    )


def create_role(cursor, name, password):
    """Crée le compte `name` sans aucun privilège, ou met à jour son mot de passe."""
    cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (name,))
    action = "ALTER" if cursor.fetchone() else "CREATE"
    cursor.execute(
        sql.SQL(
            "{} ROLE {} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD {}"
        ).format(sql.SQL(action), sql.Identifier(name), sql.Literal(password))
    )


def create_database(cursor, name, owner, app_user):
    """Crée la base `name` (si besoin) et n'autorise que `app_user` à s'y connecter."""
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (name,))
    if cursor.fetchone() is None:
        cursor.execute(
            sql.SQL("CREATE DATABASE {} OWNER {}").format(
                sql.Identifier(name), sql.Identifier(owner)
            )
        )
    database = sql.Identifier(name)
    cursor.execute(sql.SQL("REVOKE ALL ON DATABASE {} FROM PUBLIC").format(database))
    cursor.execute(
        sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(
            database, sql.Identifier(app_user)
        )
    )


def grant_app_privileges(cursor, owner, app_user):
    """Donne à `app_user` la lecture/écriture des données, sans droit sur la structure."""
    owner, app_user = sql.Identifier(owner), sql.Identifier(app_user)
    statements = [
        "GRANT USAGE ON SCHEMA public TO {app}",
        "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO {app}",
        "GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO {app}",
        "ALTER DEFAULT PRIVILEGES FOR ROLE {owner} IN SCHEMA public "
        "GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {app}",
        "ALTER DEFAULT PRIVILEGES FOR ROLE {owner} IN SCHEMA public "
        "GRANT USAGE, SELECT ON SEQUENCES TO {app}",
    ]
    for statement in statements:
        cursor.execute(sql.SQL(statement).format(owner=owner, app=app_user))


def main():
    db_name = get_env("DB_NAME")
    owner = get_env("DB_OWNER_USER")
    app_user = get_env("DB_APP_USER")

    with admin_connection("postgres") as connection, connection.cursor() as cursor:
        create_role(cursor, owner, get_env("DB_OWNER_PASSWORD"))
        create_role(cursor, app_user, get_env("DB_APP_PASSWORD"))
        print(f"1/3 Comptes {owner} et {app_user} prêts.")
        create_database(cursor, db_name, owner, app_user)

    with admin_connection(db_name) as connection, connection.cursor() as cursor:
        grant_app_privileges(cursor, owner, app_user)
    print(f"2/3 Base {db_name} prête, droits du compte applicatif appliqués.")

    seed.seed()
    print("3/3 Tables, départements et permissions créés.")


if __name__ == "__main__":
    try:
        main()
    except psycopg.OperationalError as error:
        sys.exit(
            "Connexion à PostgreSQL impossible : vérifiez que le serveur est démarré "
            f"et les identifiants DB_ADMIN_* du .env.\nDétail : {error}"
        )
