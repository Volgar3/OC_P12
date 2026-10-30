"""Saisie et affichage liés aux collaborateurs (aucune logique métier ici).

Les règles de validation sont fournies par le contrôleur (`validators`) : la vue se
contente de redemander un champ tant qu'il est refusé.
"""

from getpass import getpass

from crm.exceptions import ValidationError


def ask_new_user(groups, validators):
    """Demande les informations d'un nouveau collaborateur et les retourne."""
    print("Création d'un collaborateur")
    name = ask_until_valid("Nom complet : ", validators["name"])
    email = ask_until_valid("Email : ", validators["email"])
    group = ask_group(groups)
    password = ask_password(validators["password"])
    return {"name": name, "email": email, "password": password, "group": group}


def ask_until_valid(prompt, validate):
    """Redemande la saisie tant que `validate` la refuse, puis la retourne."""
    while True:
        value = input(prompt).strip()
        try:
            validate(value)
            return value
        except ValidationError as error:
            show_error(error)


def ask_group(groups):
    """Affiche les départements numérotés et retourne celui choisi."""
    for number, group in enumerate(groups, start=1):
        print(f"  {number}. {group.name}")
    while True:
        choice = input("Département (numéro) : ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(groups):
            return groups[int(choice) - 1]
        show_error(f"entrez un numéro entre 1 et {len(groups)}.")


def ask_password(validate):
    """Demande le mot de passe (sans l'afficher) jusqu'à ce qu'il soit valide et
    confirmé à l'identique."""
    while True:
        password = getpass("Mot de passe : ")
        try:
            validate(password)
        except ValidationError as error:
            show_error(error)
            continue
        if password == getpass("Confirmer le mot de passe : "):
            return password
        show_error("les mots de passe ne correspondent pas.")


def show_user_created(user):
    print(f"Collaborateur « {user.name} » créé (pole : {user.group.name}).")


def show_error(message):
    print(f"Erreur : {message}")
