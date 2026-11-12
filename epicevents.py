"""Point d'entrée du CRM Epic Events.

Usage :
    python epicevents.py <commande>             (login, logout)
    python epicevents.py <entité> <action>      (ex. : user create)
"""

import argparse

from crm.controllers.user import UserController
from crm.database import Session

# Commandes de session, au premier niveau : nom -> (contrôleur, méthode, aide)
SESSION_COMMANDS = {
    "login": (UserController, "login", "se connecter"),
    "logout": (UserController, "logout", "se déconnecter"),
}

# Un sous-parser par entité : entité -> (contrôleur, aide, {action: (méthode, aide)})
ENTITY_COMMANDS = {
    "user": (
        UserController,
        "gérer les collaborateurs",
        {
            "create": ("create_user", "créer un collaborateur"),
            "update": ("update_user", "modifier un collaborateur (et son mdp)"),
            "delete": ("delete_user", "supprimer un collaborateur"),
        },
    ),
}


def build_parser():
    """Construit le parser : les commandes de session puis un sous-parser par
    entité ; chaque commande retient le contrôleur et la méthode à appeler."""
    parser = argparse.ArgumentParser(prog="epicevents", description="CRM Epic Events")
    commands = parser.add_subparsers(dest="command", required=True)

    for name, (controller, method, help_text) in SESSION_COMMANDS.items():
        command = commands.add_parser(name, help=help_text)
        command.set_defaults(controller=controller, method=method)

    for entity, (controller, help_text, actions) in ENTITY_COMMANDS.items():
        entity_parser = commands.add_parser(entity, help=help_text)
        entity_actions = entity_parser.add_subparsers(dest="action", required=True)
        for action, (method, action_help) in actions.items():
            command = entity_actions.add_parser(action, help=action_help)
            command.set_defaults(controller=controller, method=method)

    return parser


def main():
    args = build_parser().parse_args()
    with Session() as session:
        controller = args.controller(session)
        getattr(controller, args.method)()


if __name__ == "__main__":
    main()
