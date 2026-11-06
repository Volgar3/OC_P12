from getpass import getpass

from crm.exceptions import ValidationError
from crm.views.base import View


class UserView(View):
    """Écrans des collaborateurs."""

    def ask_new_user(self, groups, validators):
        """Demande les informations d'un nouveau collaborateur et les retourne."""
        print("Création d'un collaborateur")
        name = self.ask_until_valid("Nom complet : ", validators["name"])
        email = self.ask_until_valid("Email : ", validators["email"])
        group = self.ask_group(groups)
        password = self.ask_password(validators["password"])
        return {"name": name, "email": email, "password": password, "group": group}

    def ask_until_valid(self, prompt, validate):
        """Redemande la saisie tant que `validate` la refuse, puis la retourne."""
        while True:
            value = input(prompt).strip()
            try:
                validate(value)
                return value
            except ValidationError as error:
                self.show_error(error)

    def ask_group(self, groups):
        """Affiche les départements numérotés et retourne celui choisi."""
        for number, group in enumerate(groups, start=1):
            print(f"  {number}. {group.name}")
        while True:
            choice = input("Département (numéro) : ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(groups):
                return groups[int(choice) - 1]
            self.show_error(f"entrez un numéro entre 1 et {len(groups)}.")

    def ask_password(self, validate):
        """Demande le mot de passe (sans l'afficher) jusqu'à ce qu'il soit valide et
        confirmé à l'identique."""
        while True:
            password = getpass("Mot de passe : ")
            try:
                validate(password)
            except ValidationError as error:
                self.show_error(error)
                continue
            if password == getpass("Confirmer le mot de passe : "):
                return password
            self.show_error("les mots de passe ne correspondent pas.")

    def show_user_created(self, user):
        print(f"Collaborateur « {user.name} » créé (pole : {user.group.name}).")

    def login(self):
        """Demande l'email et le mot de passe (sans l'afficher) et les retourne."""
        print("Connexion")
        email = input("Email : ").strip()
        password = getpass("Mot de passe : ")
        return email, password

    def show_logged_in(self, user):
        print(f"Bienvenue {user.name} (pole : {user.group.name}).")
