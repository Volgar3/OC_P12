"""Accès aux événements (table `events`)."""

from sqlalchemy import select

from crm.managers.base import Manager
from crm.models import Event


class EventManager(Manager):
    """Lecture et écriture des événements."""

    def get_all(self):
        """Retourne tous les événements, par date de début."""
        query = select(Event).order_by(Event.event_start_date)
        return self.session.scalars(query).all()

    def get_without_support(self):
        """Retourne les événements auxquels aucun support n'est associé."""
        query = select(Event).where(Event.support_contact_id.is_(None))
        return self.session.scalars(query.order_by(Event.event_start_date)).all()

    def get_by_support(self, user):
        """Retourne les événements dont `user` est le support."""
        query = select(Event).where(Event.support_contact_id == user.id)
        return self.session.scalars(query.order_by(Event.event_start_date)).all()
