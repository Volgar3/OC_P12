from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String, Table, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class User(DeclarativeBase):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"))
    group: Mapped["Group"] = relationship()


group_permissions = Table(
    "group_permissions",
    DeclarativeBase.metadata,
    Column("group_id", ForeignKey("groups.id"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.id"), primary_key=True),
)


class Group(DeclarativeBase):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    permissions: Mapped[list["Permission"]] = relationship(secondary=group_permissions)


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
    commercial_contact_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    commercial_contact: Mapped["User"] = relationship()


class Contract(DeclarativeBase):
    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    client: Mapped["Client"] = relationship()
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    remaining_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )
    contract_status: Mapped[bool] = mapped_column(default=False)


class Event(DeclarativeBase):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    contract_id: Mapped[int] = mapped_column(ForeignKey("contracts.id"))
    contract: Mapped["Contract"] = relationship()
    event_start_date: Mapped[datetime] = mapped_column(DateTime)
    event_end_date: Mapped[datetime] = mapped_column(DateTime)
    support_contact_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    support_contact: Mapped["User"] = relationship()
    location: Mapped[str] = mapped_column(String(255))
    attendees: Mapped[int] = mapped_column()
    notes: Mapped[str] = mapped_column(Text)


