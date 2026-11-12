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

    def ask_user_changes(self, user, groups, validators):
        """Demande les nouvelles valeurs d'un collaborateur (Entrée seule garde la
        valeur actuelle) et les retourne ; `password` vaut None s'il ne change pas."""
        print(f"Modification de « {user.name} » (Entrée pour garder la valeur)")
        name = self.ask_optional("Nom complet", user.name, validators["name"])
        email = self.ask_optional("Email", user.email, validators["email"])
        group = self.ask_group(groups, current=user.group)
        password = None
        if self.ask_confirmation("Changer le mot de passe ?"):
            password = self.ask_password(validators["password"])
        return {"name": name, "email": email, "group": group, "password": password}

    def ask_until_valid(self, prompt, validate):
        """Redemande la saisie tant que `validate` la refuse, puis la retourne."""
        while True:
            value = input(prompt).strip()
            try:
                validate(value)
                return value
            except ValidationError as error:
                self.show_error(error)

    def ask_optional(self, label, current, validate):
        """Comme ask_until_valid, mais Entrée seule retourne la valeur actuelle."""
        while True:
            value = input(f"{label} [{current}] : ").strip()
            if not value:
                return current
            try:
                validate(value)
                return value
            except ValidationError as error:
                self.show_error(error)

    def ask_group(self, groups, current=None):
        """Affiche les départements numérotés et retourne celui choisi (Entrée seule
        garde `current` s'il est fourni)."""
        for number, group in enumerate(groups, start=1):
            print(f"  {number}. {group.name}")
        prompt = "Département (numéro)"
        if current:
            prompt += f" [{current.name}]"
        while True:
            choice = input(f"{prompt} : ").strip()
            if current and not choice:
                return current
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

    def ask_email(self):
        """Demande l'email du collaborateur à modifier ou supprimer."""
        return input("Email du collaborateur : ").strip()

    def ask_confirmation(self, question):
        """Pose une question oui/non ; seul « o » vaut oui."""
        return input(f"{question} (o/N) : ").strip().lower() == "o"

    def show_user_created(self, user):
        print(f"Collaborateur « {user.name} » créé (pole : {user.group.name}).")

    def show_user_updated(self, user):
        print(f"Collaborateur « {user.name} » modifié (pole : {user.group.name}).")

    def show_user_deleted(self, name):
        print(f"Collaborateur « {name} » supprimé.")

    def login(self):
        """Demande l'email et le mot de passe (sans l'afficher) et les retourne."""
        print("Connexion")
        email = input("Email : ").strip()
        password = getpass("Mot de passe : ")
        return email, password

    def show_logged_in(self, user):
        print(f"Bienvenue {user.name} (pole : {user.group.name}).")

    def show_logged_out(self):
        print("Vous êtes déconnecté.")
