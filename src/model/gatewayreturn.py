import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from model.file import File

from database import db


class GatewayReturn(db.Model):
    __table_name__ = "gateway_return"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    method: Mapped[str] = mapped_column(db.String, default=False)
    path: Mapped[str] = mapped_column(db.String, nullable=False)
    body: Mapped[str] = mapped_column(db.JSON, nullable=True)
    headers: Mapped[str] = mapped_column(db.JSON, nullable=True)

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
