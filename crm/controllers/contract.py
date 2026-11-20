"""Logique métier des contrats : relie la vue et les managers."""

from crm.controllers.base import Controller, require_permission
from crm.managers.contract import ContractManager
from crm.views.contract import ContractView


class ContractController(Controller):
    """Gestion des contrats."""

    def __init__(self, session, view=None):
        super().__init__(session)
        self.contracts = ContractManager(session)
        self.view = view or ContractView()

    @require_permission("read_contracts")
    def list_contracts(self):
        """Affiche tous les contrats."""
        contracts = self.contracts.get_all()
        self.view.show_contracts(contracts)
        return contracts

    @require_permission("read_contracts")
    def list_unsigned(self):
        """Affiche les contrats pas encore signés."""
        contracts = self.contracts.get_unsigned()
        self.view.show_contracts(contracts, "Contrats non signés")
        return contracts

    @require_permission("read_contracts")
    def list_not_fully_paid(self):
        """Affiche les contrats pas entièrement payés."""
        contracts = self.contracts.get_not_fully_paid()
        self.view.show_contracts(contracts, "Contrats pas entièrement payés")
        return contracts
