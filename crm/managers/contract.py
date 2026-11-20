"""Accès aux contrats (table `contracts`)."""

from sqlalchemy import select

from crm.managers.base import Manager
from crm.models import Contract


class ContractManager(Manager):
    """Lecture et écriture des contrats."""

    def get_all(self):
        """Retourne tous les contrats, du plus ancien au plus récent."""
        return self.session.scalars(select(Contract).order_by(Contract.id)).all()

    def get_unsigned(self):
        """Retourne les contrats qui ne sont pas encore signés."""
        query = select(Contract).where(Contract.is_signed.is_(False))
        return self.session.scalars(query.order_by(Contract.id)).all()

    def get_not_fully_paid(self):
        """Retourne les contrats dont il reste un montant à payer."""
        query = select(Contract).where(Contract.remaining_amount > 0)
        return self.session.scalars(query.order_by(Contract.id)).all()
