"""Saisie et affichage liés aux événements (aucune logique métier ici)."""

from crm.views.base import DATE_FORMAT, View


class EventView(View):
    """Écrans des événements."""

    def show_events(self, events, title="Liste des événements"):
        self.show_list(title, events, self.format_event)

    def format_event(self, event):
        """Retourne une ligne décrivant l'événement."""
        support = event.support_contact.name if event.support_contact else "aucun"
        return (
            f"#{event.id} {event.name} | contrat #{event.contract.id} "
            f"(client : {event.contract.client.name}) | "
            f"du {event.event_start_date:{DATE_FORMAT}} "
            f"au {event.event_end_date:{DATE_FORMAT}} -> {event.location} "
            f"{event.attendees} participants / support : {support}"
        )
