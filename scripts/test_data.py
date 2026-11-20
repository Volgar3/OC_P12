"""Insère des données de test : collaborateurs, clients 1 à 5, contrats, events 1 à 5.

Chaque élément couvre un cas différent (contrat signé ou non, payé ou non, événement
avec ou sans support…). Toutes les données de test ont un email en @test.io.

    python -m scripts.test_data           insère les données (si elles n'existent pas)
    python -m scripts.test_data --reset   supprime puis réinsère les données de test

À n'utiliser que sur une base de développement : les comptes de test ont tous le
même mot de passe, TEST_PASSWORD.
"""

import sys
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select

from crm.database import Session
from crm.managers.group import GroupManager
from crm.managers.user import UserManager
from crm.models import Client, Contract, Event, User

TEST_DOMAIN = "@test.io"
TEST_PASSWORD = "Test1234"

# email -> (nom, département)
USERS = {
    "gestion@test.io": ("Test Gestion", "gestion"),
    "commercial1@test.io": ("Test Commercial 1", "commercial"),
    "commercial2@test.io": ("Test Commercial 2", "commercial"),
    "support1@test.io": ("Test Support 1", "support"),
    "support2@test.io": ("Test Support 2", "support"),
    "support3@test.io": ("Test Support 3", "support"),
}

# numéro -> (téléphone, email du commercial)
CLIENTS = {
    1: ("+678 123 456 78", "commercial1@test.io"),
    2: ("+1 234 567 8901", "commercial1@test.io"),
    3: ("+ 666 12345", "commercial2@test.io"),
    4: ("06 12 34 56 78", "commercial2@test.io"),
    5: ("+33 1 23 45 67 89", "commercial1@test.io"),
}

# numéro -> (client, total, reste à payer, signé)
CONTRACTS = {
    1: (1, "5000.00", "0.00", True),
    2: (2, "8000.00", "3000.00", True),
    3: (3, "2500.00", "2500.00", False),
    4: (4, "12000.00", "0.00", True),
    5: (1, "1500.00", "0.00", False),
}

# numéro -> (contrat, début, fin, lieu, participants, email du support, notes)
EVENTS = {
    1: (
        1,
        datetime(2027, 6, 4, 13, 0),
        datetime(2027, 6, 5, 2, 0),
        "53 Rue du Château, 41120 Candé-sur-Beuvron",
        75,
        "support1@test.io",
        "Mariage : DJ prévu, vérifier l'accès traiteur.",
    ),
    2: (
        1,
        datetime(2026, 3, 14, 18, 0),
        datetime(2026, 3, 14, 23, 30),
        "Paris",
        40,
        "support2@test.io",
        None,
    ),
    3: (
        2,
        datetime(2027, 9, 10, 9, 0),
        datetime(2027, 9, 12, 17, 0),
        "Lyon",
        300,
        "support1@test.io",
        None,
    ),
    4: (
        4,
        datetime(2027, 1, 20, 19, 0),
        datetime(2027, 1, 20, 23, 0),
        "Bordeaux",
        120,
        None,
        None,
    ),
    5: (
        2,
        datetime(2027, 2, 2, 10, 0),
        datetime(2027, 2, 2, 12, 0),
        "Visioconférence",
        0,
        None,
        "Réunion de préparation.\nAucun participant sur place.",
    ),
}


def has_test_data(session):
    """Retourne True si des données de test existent déjà."""
    query = select(User.id).where(User.email.endswith(TEST_DOMAIN)).limit(1)
    return session.scalars(query).first() is not None


def delete_test_data(session):
    """Supprime les événements, contrats, clients puis collaborateurs de test."""
    clients = session.scalars(
        select(Client).where(Client.email.endswith(TEST_DOMAIN))
    ).all()
    for client in clients:
        for contract in client.contracts:
            for event in contract.events:
                session.delete(event)
            session.delete(contract)
        session.delete(client)
    session.flush()
    users = session.scalars(select(User).where(User.email.endswith(TEST_DOMAIN)))
    for user in users:
        session.delete(user)
    session.commit()


def insert_test_data(session):
    """Insère les collaborateurs, clients, contrats et événements de test."""
    groups = {group.name: group for group in GroupManager(session).get_all()}
    user_manager = UserManager(session)
    users = {
        email: user_manager.add(name, email, TEST_PASSWORD, groups[group])
        for email, (name, group) in USERS.items()
    }

    clients = {}
    for number, (telephone, commercial) in CLIENTS.items():
        clients[number] = Client(
            name=f"Client {number}",
            email=f"client{number}{TEST_DOMAIN}",
            telephone=telephone,
            enterprise_name=f"Entreprise {number}",
            commercial_contact=users[commercial],
        )

    contracts = {}
    for number, (client, total, remaining, signed) in CONTRACTS.items():
        contracts[number] = Contract(
            client=clients[client],
            total_amount=Decimal(total),
            remaining_amount=Decimal(remaining),
            is_signed=signed,
        )

    events = []
    for number, event_data in EVENTS.items():
        contract, start, end, location, attendees, support, notes = event_data
        events.append(
            Event(
                name=f"Event {number}",
                contract=contracts[contract],
                event_start_date=start,
                event_end_date=end,
                location=location,
                attendees=attendees,
                support_contact=users[support] if support else None,
                notes=notes,
            )
        )

    session.add_all([*clients.values(), *contracts.values(), *events])
    session.commit()


def main():
    with Session() as session:
        if "--reset" in sys.argv:
            delete_test_data(session)
        elif has_test_data(session):
            print("Données de test déjà présentes (relancer avec --reset).")
            return
        insert_test_data(session)
    print(
        f"Données de test insérées : {len(USERS)} collaborateurs, "
        f"{len(CLIENTS)} clients, {len(CONTRACTS)} contrats, {len(EVENTS)} events."
    )
    print(f"Mot de passe de tous les comptes de test : {TEST_PASSWORD}")


if __name__ == "__main__":
    main()
