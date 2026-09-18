from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Table, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class User(DeclarativeBase):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id : Mapped[int] = mapped_column(
        ForeignKey("groups.id")
    )
    group: Mapped["Group"] = relationship()

class Group(DeclarativeBase):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    permissions = Table(
        "group_permissions",
        DeclarativeBase.metadata,
        Column("group_id", ForeignKey("groups.id"), primary_key=True),
        Column("permission_id", ForeignKey("permissions.id"), primary_key=True),
    )

class Permission(DeclarativeBase):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True)

class Client(DeclarativeBase):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    telephone: Mapped[str] = mapped_column(String(15))
    enterprise_name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )
    commercial_contact_id : Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )
    commercial_contact: Mapped["User"] = relationship()

class Contract(DeclarativeBase):
    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(primary_key=True)

class Event(DeclarativeBase):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)