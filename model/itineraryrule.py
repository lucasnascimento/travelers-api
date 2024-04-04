import uuid
from datetime import datetime, date
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


from database import db


class Rule(db.Model):
    __tablename__ = "itinerary_rule"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    position: Mapped[int] = mapped_column(db.Integer, nullable=False)
    purchase_deadline: Mapped[str] = mapped_column(db.Date, nullable=False)
    installments: Mapped[str] = mapped_column(db.Integer, nullable=False)

    itinerary_id: Mapped[Optional[str]] = mapped_column(ForeignKey("itinerary.id"))

    pix_discount: Mapped[float] = mapped_column(
        db.Numeric, nullable=False, server_default="0"
    )
    seat_price: Mapped[float] = mapped_column(
        db.Numeric, nullable=False, server_default="0"
    )
    montly_interest: Mapped[float] = mapped_column(
        db.Numeric, nullable=False, server_default="0"
    )

    is_deleted: Mapped[bool] = mapped_column(db.Boolean, default=False)
    inserted_at: Mapped[str] = mapped_column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[str] = mapped_column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {
            c.key: format_if_date(getattr(self, c.key))
            for c in db.inspect(self).mapper.column_attrs
        }


def format_if_date(value):
    if isinstance(value, date):
        return value.isoformat()
    return value
