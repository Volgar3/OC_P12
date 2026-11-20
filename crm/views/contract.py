"""Saisie et affichage liés aux contrats (aucune logique métier ici)."""

from crm.views.base import DATE_FORMAT, View


class ContractView(View):
    """Écrans des contrats."""

    def show_contracts(self, contracts, title="Liste des contrats"):
        self.show_list(title, contracts, self.format_contract)

    def format_contract(self, contract):
        """Retourne une ligne décrivant le contrat."""
        status = "signé" if contract.is_signed else "non signé"
        return (
            f"#{contract.id} client : {contract.client.name} "
            f"total : {contract.total_amount} € "
            f"reste : {contract.remaining_amount} € | {status} "
            f"créé le {contract.created_at:{DATE_FORMAT}} | "
            f"commercial : {contract.client.commercial_contact.name}"
        )
