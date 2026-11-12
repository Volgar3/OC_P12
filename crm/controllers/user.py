"""Logique métier des collaborateurs : relie la vue et les managers."""

import re

from crm.controllers.base import Controller, require_permission
from crm.exceptions import ValidationError
from crm.managers.group import GroupManager
from crm.security import verify_password
from crm.views.user import UserView

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PASSWORD_MIN_LENGTH = 8
MAX_LOGIN_ATTEMPTS = 3


class UserController(Controller):
    """Comptes des collaborateurs : connexion, création, modification et
    suppression."""

    def __init__(self, session, view=None):
        super().__init__(session)
        self.groups = GroupManager(session)
        self.view = view or UserView()

    def create_user(self):
        """Demande les informations à la vue (champ par champ, avec vérification
        immédiate) puis crée le collaborateur.

        Réservé à la permission `create_user`, sauf pour le tout premier compte
        (sinon personne ne pourrait jamais se connecter)."""
        if self.users.has_any() and not self.authorize("create_user"):
            return None
        groups = self.groups.get_all()
        if not groups:
            self.view.show_error("aucun département : lancez d'abord scripts.init_db.")
            return None
        data = self.view.ask_new_user(
            groups,
            validators={
                "name": self.validate_name,
                "email": self.validate_email,
                "password": self.validate_password,
            },
        )
        try:
            user = self.register(**data)
        except ValidationError as error:
            self.view.show_error(error)
            return None
        self.view.show_user_created(user)
        return user

    def register(self, name, email, password, group):
        """Vérifie toutes les données puis enregistre le collaborateur."""
        self.validate_name(name)
        self.validate_email(email)
        self.validate_password(password)
        return self.users.add(name, email, password, group)

    @require_permission("update_user")
    def update_user(self):
        """Demande quel collaborateur modifier, puis ses nouvelles valeurs
        (département et mot de passe compris)."""
        user = self.find_user()
        if user is None:
            return None
        data = self.view.ask_user_changes(
            user,
            self.groups.get_all(),
            validators={
                "name": self.validate_name,
                "email": lambda email: self.validate_email(email, user),
                "password": self.validate_password,
            },
        )
        try:
            user = self.change(user, **data)
        except ValidationError as error:
            self.view.show_error(error)
            return None
        self.view.show_user_updated(user)
        return user

    def change(self, user, name, email, group, password=None):
        """Vérifie toutes les nouvelles données puis modifie le collaborateur."""
        self.validate_name(name)
        self.validate_email(email, user)
        if password is not None:
            self.validate_password(password)
        return self.users.update(user, name, email, group, password)

    @require_permission("delete_user")
    def delete_user(self):
        """Demande quel collaborateur supprimer et le supprime après confirmation."""
        user = self.find_user()
        if user is None:
            return None
        if user.id == self.current_user.id:
            self.view.show_error("vous ne pouvez pas supprimer votre propre compte.")
            return None
        if user.clients:
            self.view.show_error(
                f"{user.name} est le commercial de {len(user.clients)} client(s) : "
                "attribuez-les d'abord à un autre commercial."
            )
            return None
        question = f"Supprimer « {user.name} » ?"
        if user.supported_events:
            question = (
                f"{user.name} est le support de {len(user.supported_events)} "
                f"événement(s), qui n'auront plus de support. {question}"
            )
        if not self.view.ask_confirmation(question):
            return None
        name = user.name
        self.users.delete(user)
        self.view.show_user_deleted(name)
        return name

    def find_user(self):
        """Demande l'email d'un collaborateur à la vue et le retourne, ou None."""
        email = self.view.ask_email()
        user = self.users.get_by_email(email)
        if user is None:
            self.view.show_error(f"aucun collaborateur avec l'email « {email} ».")
        return user

    def validate_name(self, name):
        """Lève ValidationError si le nom est vide."""
        if not name:
            raise ValidationError("le nom est obligatoire.")

    def validate_email(self, email, user=None):
        """Lève ValidationError si l'email est mal formé ou déjà utilisé par un
        autre collaborateur que `user`."""
        if not EMAIL_PATTERN.match(email):
            raise ValidationError(f"« {email} » n'est pas un email valide.")
        owner = self.users.get_by_email(email)
        if owner and owner is not user:
            raise ValidationError(f"l'email « {email} » est déjà utilisé.")

    def validate_password(self, password):
        """Lève ValidationError si le mot de passe est trop court."""
        if len(password) < PASSWORD_MIN_LENGTH:
            raise ValidationError(
                f"le mot de passe doit faire au moins {PASSWORD_MIN_LENGTH} caractères."
            )

    def login(self):
        """Demande les identifiants à la vue (au plus MAX_LOGIN_ATTEMPTS fois), les
        vérifie puis crée le token."""
        for attempt in range(1, MAX_LOGIN_ATTEMPTS + 1):
            email, password = self.view.login()
            user = self.users.get_by_email(email)
            if user and verify_password(password, user.password_hash):
                break
            remaining = MAX_LOGIN_ATTEMPTS - attempt
            self.view.show_error(
                f"email ou mot de passe incorrect ({remaining} essai(s) restant(s))."
            )
        else:
            return None

        token = self.create_token(user)
        self.tokens.save(token)
        self.view.show_logged_in(user)
        return token

    def logout(self):
        """Supprime le token : il faudra se reconnecter."""
        self.tokens.delete()
        self.view.show_logged_out()
