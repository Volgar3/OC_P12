"""Saisie et affichage liés aux clients (aucune logique métier ici)."""

from crm.views.base import View


class ClientView(View):
    """Écrans des clients."""

    def show_clients(self, clients):
        self.show_list("Liste des clients", clients, self.format_client)

    def format_client(self, client):
        """Retourne une ligne décrivant le client."""
        return (
            f"#{client.id} {client.name} ({client.enterprise_name}) | "
            f"{client.email} | {client.telephone} | "
            f"commercial : {client.commercial_contact.name}"
        )
