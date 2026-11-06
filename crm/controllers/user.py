"""Logique métier des collaborateurs : relie la vue et les managers."""

import re

from crm.controllers.base import Controller
from crm.exceptions import ValidationError
from crm.managers.group import GroupManager
from crm.managers.user import UserManager
from crm.security import verify_password
from crm.views.user import UserView

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PASSWORD_MIN_LENGTH = 8


class UserController(Controller):
    """Création des collaborateurs."""

    def __init__(self, session, view=None):
        super().__init__()
        self.users = UserManager(session)
        self.groups = GroupManager(session)
        self.view = view or UserView()

    def create_user(self):
        """Demande les informations à la vue (champ par champ, avec vérification
        immédiate) puis crée le collaborateur."""
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

    def validate_name(self, name):
        """Lève ValidationError si le nom est vide."""
        if not name:
            raise ValidationError("le nom est obligatoire.")

    def validate_email(self, email):
        """Lève ValidationError si l'email est mal formé ou déjà utilisé."""
        if not EMAIL_PATTERN.match(email):
            raise ValidationError(f"« {email} » n'est pas un email valide.")
        if self.users.get_by_email(email):
            raise ValidationError(f"l'email « {email} » est déjà utilisé.")

    def validate_password(self, password):
        """Lève ValidationError si le mot de passe est trop court."""
        if len(password) < PASSWORD_MIN_LENGTH:
            raise ValidationError(
                f"le mot de passe doit faire au moins {PASSWORD_MIN_LENGTH} caractères."
            )

    def login(self):
        """Demande les identifiants à la vue, les vérifie puis crée le token."""
        email, password = self.view.login()
        user = self.users.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            self.view.show_error("email ou mot de passe incorrect.")
            return None

        token = self.create_token(user)
        self.tokens.save(token)
        self.view.show_logged_in(user)
        return token
