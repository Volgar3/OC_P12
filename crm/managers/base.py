"""Classe mère des managers : l'accès à la base commun à tous."""


class Manager:
    """Garde la session SQLAlchemy utilisée pour lire et écrire en base."""

    def __init__(self, session):
        self.session = session
