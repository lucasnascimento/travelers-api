import uuid
from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from database import db


class Institution(db.Model):
    table_name = "institution"
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    active_on_website: Mapped[str] = mapped_column(db.Boolean, default=False)
    name: Mapped[str] = mapped_column(db.String, nullable=False)
    document: Mapped[str] = mapped_column(db.String, nullable=False)
    has_banking_account: Mapped[bool] = mapped_column(db.Boolean, default=False)
    banking_account: Mapped[str] = mapped_column(db.JSON, nullable=True)
    password: Mapped[str] = mapped_column(db.String, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, default=False)
    inserted_at: Mapped[str] = mapped_column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[str] = mapped_column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {
            c.key: getattr(self, c.key) for c in db.inspect(self).mapper.column_attrs
        }
