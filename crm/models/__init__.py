"""Modèles (M de MVC) : tables de la base, relations et contraintes.

Les classes sont ré-exportées ici pour pouvoir écrire `from crm.models import User`.
"""

from crm.models.models import (
    Base,
    Client,
    Contract,
    Event,
    Group,
    Permission,
    User,
    group_permissions,
)

__all__ = [
    "Base",
    "Client",
    "Contract",
    "Event",
    "Group",
    "Permission",
    "User",
    "group_permissions",
]
