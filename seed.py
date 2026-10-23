"""Initialise la DB, à lancer en premier"""

from sqlalchemy import select, create_engine

from database import Session, build_url
from models import Base, Group, Permission

PERMISSIONS_BY_GROUP = {
    "gestion": [
        "read_clients",
        "read_contracts",
        "read_events",
        "create_contract",
        "update_contract",
        "update_event",
        "create_user",
        "update_user",
        "delete_user",
    ],
    "commercial": [
        "read_clients",
        "read_contracts",
        "read_events",
        "create_own_client",
        "update_own_client",
        "update_own_contract",
        "create_event",
    ],
    "support": [
        "read_clients",
        "read_contracts",
        "read_events",
        "update_own_event",
    ],
}


def get_or_create(session, model, name):

    obj = session.scalars(select(model).where(model.name == name)).first()
    if obj is None:
        obj = model(name=name)
        session.add(obj)
    return obj


def seed():
    engine = create_engine(build_url("OWNER"))
    Base.metadata.create_all(engine)
    engine.dispose()

    with Session() as session:
        for group_name, permission_names in PERMISSIONS_BY_GROUP.items():
            group = get_or_create(session, Group, group_name)
            for permission_name in permission_names:
                permission = get_or_create(session, Permission, permission_name)
                if permission not in group.permissions:
                    group.permissions.append(permission)
        session.commit()


if __name__ == "__main__":
    seed()
