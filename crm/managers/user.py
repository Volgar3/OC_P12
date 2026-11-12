"""Accès aux collaborateurs (table `users`)."""

from sqlalchemy import select

from crm.managers.base import Manager
from crm.models import User
from crm.security import hash_password


class UserManager(Manager):
    """Lecture et écriture des collaborateurs."""

    def get_by_id(self, user_id):
        """Retourne le collaborateur ayant cet id, ou None."""
        return self.session.get(User, user_id)

    def get_by_email(self, email):
        """Retourne le collaborateur ayant cet email, ou None."""
        return self.session.scalars(select(User).where(User.email == email)).first()

    def has_any(self):
        """Retourne True s'il existe au moins un collaborateur."""
        return self.session.scalars(select(User.id).limit(1)).first() is not None

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

    def update(self, user, name, email, group, password=None):
        """Modifie un collaborateur ; le mot de passe n'est changé (et haché) que
        s'il est fourni."""
        user.name = name
        user.email = email
        user.group = group
        if password is not None:
            user.password_hash = hash_password(password)
        self.session.commit()
        return user

    def delete(self, user):
        """Supprime un collaborateur ; ses événements perdent leur support."""
        self.session.delete(user)
        self.session.commit()
