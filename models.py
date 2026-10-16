from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Table,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"))
    group: Mapped["Group"] = relationship(back_populates="users")
    clients: Mapped[list["Client"]] = relationship(back_populates="commercial_contact")
    supported_events: Mapped[list["Event"]] = relationship(
        back_populates="support_contact"
    )


group_permissions = Table(
    "group_permissions",
    Base.metadata,
    Column("group_id", ForeignKey("groups.id"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.id"), primary_key=True),
)


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    users: Mapped[list["User"]] = relationship(back_populates="group")
    permissions: Mapped[list["Permission"]] = relationship(
        secondary=group_permissions, back_populates="groups"
    )


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    groups: Mapped[list["Group"]] = relationship(
        secondary=group_permissions, back_populates="permissions"
    )


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    telephone: Mapped[str] = mapped_column(String(20))
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
    commercial_contact: Mapped["User"] = relationship(back_populates="clients")
    contracts: Mapped[list["Contract"]] = relationship(back_populates="client")


class Contract(Base):
    __tablename__ = "contracts"
    __table_args__ = (
        CheckConstraint(
            "remaining_amount >= 0 AND remaining_amount <= total_amount",
            name="ck_contract_amounts_valid",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    client: Mapped["Client"] = relationship(back_populates="contracts")
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    remaining_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )
    contract_is_signed: Mapped[bool] = mapped_column(default=False)
    events: Mapped[list["Event"]] = relationship(back_populates="contract")


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (
        CheckConstraint(
            "event_end_date >= event_start_date", name="ck_event_dates_order"
        ),
        CheckConstraint("attendees >= 0", name="ck_event_attendees_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    contract_id: Mapped[int] = mapped_column(ForeignKey("contracts.id"))
    contract: Mapped["Contract"] = relationship(back_populates="events")
    event_start_date: Mapped[datetime] = mapped_column(DateTime)
    event_end_date: Mapped[datetime] = mapped_column(DateTime)
    support_contact_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    support_contact: Mapped["User | None"] = relationship(
        back_populates="supported_events"
    )
    location: Mapped[str] = mapped_column(String(255))
    attendees: Mapped[int] = mapped_column()
    notes: Mapped[str | None] = mapped_column(Text)
