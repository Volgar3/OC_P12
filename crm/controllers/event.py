"""Logique métier des événements : relie la vue et les managers."""

from crm.controllers.base import Controller, require_permission
from crm.managers.event import EventManager
from crm.views.event import EventView


class EventController(Controller):
    """Gestion des événements."""

    def __init__(self, session, view=None):
        super().__init__(session)
        self.events = EventManager(session)
        self.view = view or EventView()

    @require_permission("read_events")
    def list_events(self):
        """Affiche tous les événements."""
        events = self.events.get_all()
        self.view.show_events(events)
        return events

    @require_permission("read_events")
    def list_without_support(self):
        """Affiche les événements sans support associé."""
        events = self.events.get_without_support()
        self.view.show_events(events, "Événements sans support")
        return events

    @require_permission("read_events")
    def list_mine(self):
        """Affiche les événements dont le collaborateur connecté est le support."""
        events = self.events.get_by_support(self.current_user)
        self.view.show_events(events, f"Événements de {self.current_user.name}")
        return events
