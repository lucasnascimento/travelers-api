import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.file import File

from database import db


class Institution(db.Model):
    __table_name__ = "institution"

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
    file_id: Mapped[Optional[str]] = mapped_column(ForeignKey("file.id"))
    file: Mapped[Optional[File]] = relationship("File", uselist=False)
    ranking: Mapped[float] = mapped_column(
        db.Numeric, default="9999", server_default="9999"
    )

    def to_dict(self):
        result = {
            c.key: getattr(self, c.key) for c in db.inspect(self).mapper.column_attrs
        }

        del result["password"]  # Remove password from response

        if hasattr(self, "file") and self.file is not None:
            result["file"] = self.file.to_dict()
        return result
