"""Point d'entrée du CRM Epic Events.

Usage : python epicevents.py <commande>
"""

import argparse

from crm.controllers.create_user import UserController
from crm.database import Session


def create_user():
    with Session() as session:
        UserController(session).create_user()

def login():
    with Session() as session:
        UserController(session).login()


COMMANDS = {
    "create-user": (create_user, "créer un collaborateur"),
    "login": (login, "Se connecter"),
}


def main():
    parser = argparse.ArgumentParser(prog="epicevents", description="CRM Epic Events")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name, (_, help_text) in COMMANDS.items():
        subparsers.add_parser(name, help=help_text)
    args = parser.parse_args()
    COMMANDS[args.command][0]()


if __name__ == "__main__":
    main()
