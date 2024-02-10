import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


from database import db


class InvoiceEvent(db.Model):
    __tablename__ = "invoice_event"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    invoice_id: Mapped[Optional[str]] = mapped_column(ForeignKey("invoice.id"))
    gatewayreturn_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("gateway_return.id")
    )

    event: Mapped[str] = mapped_column(db.String, nullable=False)
    status: Mapped[str] = mapped_column(db.String, nullable=True)

    is_deleted: Mapped[bool] = mapped_column(db.Boolean, default=False)
    inserted_at: Mapped[str] = mapped_column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[str] = mapped_column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
