"""Accès aux départements (table `groups`)."""

from sqlalchemy import select

from crm.models import Group


class GroupRepository:
    """Lecture des départements."""

    def __init__(self, session):
        self.session = session

    def get_all(self):
        """Retourne tous les départements, triés par nom."""
        return self.session.scalars(select(Group).order_by(Group.name)).all()
