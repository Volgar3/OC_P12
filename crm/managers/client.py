"""Accès aux clients (table `clients`)."""

from sqlalchemy import select

from crm.managers.base import Manager
from crm.models import Client


class ClientManager(Manager):
    """Lecture et écriture des clients."""

    def get_all(self):
        """Retourne tous les clients, triés par nom."""
        return self.session.scalars(select(Client).order_by(Client.name)).all()
