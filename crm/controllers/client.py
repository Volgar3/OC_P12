"""Logique métier des clients : relie la vue et les managers."""

from crm.controllers.base import Controller, require_permission
from crm.managers.client import ClientManager
from crm.views.client import ClientView


class ClientController(Controller):
    """Gestion des clients."""

    def __init__(self, session, view=None):
        super().__init__(session)
        self.clients = ClientManager(session)
        self.view = view or ClientView()

    @require_permission("read_clients")
    def list_clients(self):
        """Affiche tous les clients."""
        clients = self.clients.get_all()
        self.view.show_clients(clients)
        return clients
