"""Accès aux collaborateurs (table `users`)."""

from sqlalchemy import select

from crm.models import User
from crm.security import hash_password


class UserRepository:
    """Lecture et écriture des collaborateurs."""

    def __init__(self, session):
        self.session = session

    def get_by_email(self, email):
        """Retourne le collaborateur ayant cet email, ou None."""
        return self.session.scalars(select(User).where(User.email == email)).first()

    def add(self, name, email, password, group):
        """Enregistre un collaborateur ; le mot de passe est toujours haché."""
        user = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            group=group,
        )
        self.session.add(user)
        self.session.commit()
        return user
