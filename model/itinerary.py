import uuid
from datetime import datetime, date
from typing import Optional
import pytz

from sqlalchemy import ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.file import File
from model.institution import Institution
from model.itineraryrule import Rule
from model.group import Group

from database import db

from sqlalchemy import select, text
from sqlalchemy.orm import column_property


class Itinerary(db.Model):
    __tablename__ = "itinerary"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    status: Mapped[str] = mapped_column(db.String, nullable=False, default="draft")
    current_step: Mapped[str] = mapped_column(
        db.String, nullable=False, default="general"
    )
    title: Mapped[str] = mapped_column(db.String, nullable=False)
    boarding_date: Mapped[str] = mapped_column(db.Date, nullable=False)
    landing_date: Mapped[str] = mapped_column(db.Date, nullable=False)
    seats: Mapped[int] = mapped_column(db.Integer, nullable=False)

    details: Mapped[str] = mapped_column(db.String, nullable=False)
    summary: Mapped[str] = mapped_column(db.String, nullable=False)
    services: Mapped[str] = mapped_column(db.String, nullable=False)
    terms_and_conditions: Mapped[str] = mapped_column(db.String, nullable=False)

    institution_id: Mapped[Optional[str]] = mapped_column(ForeignKey("institution.id"))
    cover_id: Mapped[Optional[str]] = mapped_column(ForeignKey("file.id"))
    group_id: Mapped[Optional[str]] = mapped_column(ForeignKey("group.id"))

    institution: Mapped[Optional[Institution]] = relationship(
        "Institution", uselist=False
    )
    cover: Mapped[Optional[File]] = relationship(
        "File", uselist=False, foreign_keys=[cover_id]
    )
    group: Mapped[Optional[Group]] = relationship("Group", uselist=False)

    cover_small_id: Mapped[Optional[str]] = mapped_column(ForeignKey("file.id"))
    cover_small: Mapped[Optional[File]] = relationship(
        "File", uselist=False, foreign_keys=[cover_small_id]
    )

    purchase_deadline: Mapped[float] = column_property(
        select(Rule.purchase_deadline)
        .where(
            Rule.itinerary_id == id
            and Rule.is_deleted == False
            and Rule.purchase_deadline >= datetime.utcnow()
        )
        .order_by(Rule.purchase_deadline.asc())
        .limit(1)
        .scalar_subquery()
    )
    seat_price: Mapped[float] = column_property(
        select(Rule.seat_price)
        .where(
            Rule.itinerary_id == id
            and Rule.is_deleted == False
            and Rule.purchase_deadline >= datetime.utcnow()
        )
        .order_by(Rule.purchase_deadline.asc())
        .limit(1)
        .scalar_subquery()
    )
    installments: Mapped[float] = column_property(
        select(Rule.installments)
        .where(
            Rule.itinerary_id == id
            and Rule.is_deleted == False
            and Rule.purchase_deadline >= datetime.utcnow()
        )
        .order_by(Rule.purchase_deadline.asc())
        .limit(1)
        .scalar_subquery()
    )
    pix_discount: Mapped[float] = column_property(
        select(Rule.pix_discount)
        .where(
            Rule.itinerary_id == id
            and Rule.is_deleted == False
            and Rule.purchase_deadline >= datetime.utcnow()
        )
        .order_by(Rule.purchase_deadline.asc())
        .limit(1)
        .scalar_subquery()
    )

    cancelation_rules: Mapped[str] = mapped_column(
        db.String, nullable=False, server_default=""
    )

    is_deleted: Mapped[bool] = mapped_column(db.Boolean, default=False)
    inserted_at: Mapped[str] = mapped_column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[str] = mapped_column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        result = {
            c.key: format_if_date(getattr(self, c.key))
            for c in db.inspect(self).mapper.column_attrs
        }
        sold_seats = self.get_sold_seats()
        result["sold_seats"] = sold_seats
        if sold_seats >= self.seats:
            result["status"] = "sold_out"

        payment_rule = self.get_current_payment_rule()
        result["purchase_deadline"] = format_if_date(payment_rule.purchase_deadline)
        result["seat_price"] = payment_rule.seat_price
        result["installments"] = payment_rule.installments
        result["pix_discount"] = payment_rule.pix_discount

        brazil_tz = pytz.timezone("America/Sao_Paulo")
        now = datetime.now(brazil_tz).date()
        if now > payment_rule.purchase_deadline:
            result["status"] = "booking_closed"

        if hasattr(self, "cover") and self.cover is not None:
            result["cover"] = self.cover.to_dict()
        if hasattr(self, "cover_small") and self.cover_small is not None:
            result["cover_small"] = self.cover_small.to_dict()
        if hasattr(self, "institution") and self.institution is not None:
            result["institution"] = self.institution.to_dict()
        if hasattr(self, "group") and self.group is not None:
            result["group"] = self.group.to_dict()
        return result

    def get_sold_seats(self) -> int:
        from model.bookingtraveler import BookingTraveler
        from model.booking import Booking
        from model.invoice import Invoice

        query = (
            db.session.query(func.count(BookingTraveler.id).label("seats_sold"))
            .join(Booking, BookingTraveler.booking_id == Booking.id)
            .join(Invoice, Invoice.booking_id == Booking.id)
            .filter(Invoice.status == "PAID")
            .filter(Booking.itinerary_id == self.id)
        )

        return query.scalar()

    def get_current_payment_rule(self):
        from model.itineraryrule import Rule

        brazil_tz = pytz.timezone("America/Sao_Paulo")
        now = datetime.now(brazil_tz).date()
        query = (
            db.session.query(Rule)
            .filter(Rule.itinerary_id == self.id)
            .filter(Rule.is_deleted == False)
            .order_by(Rule.purchase_deadline.asc())
        )

        payment_rules = query.all()

        # future me, please find a better way to do this
        # we have to find the first rule that has a purchase_deadline greater than the current date
        # and return if all rules are in the past
        # then return the last rule
        payment_rule = payment_rules[-1]
        for rule in payment_rules:
            if now <= rule.purchase_deadline:
                payment_rule = rule
                break

        return payment_rule


def format_if_date(value):
    if isinstance(value, date):
        return value.isoformat()
    return value
