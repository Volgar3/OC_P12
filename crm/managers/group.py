"""Accès aux départements (table `groups`)."""

from sqlalchemy import select

from crm.managers.base import Manager
from crm.models import Group


class GroupManager(Manager):
    """Lecture des départements."""

    def get_all(self):
        """Retourne tous les départements, triés par nom."""
        return self.session.scalars(select(Group).order_by(Group.name)).all()
