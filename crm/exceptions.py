"""Exceptions propres à l'application."""


class ValidationError(Exception):
    """Donnée saisie invalide ; le message est destiné à l'utilisateur."""


class AuthenticationError(Exception):
    """Aucun collaborateur connecté (token absent, expiré ou invalide)."""
