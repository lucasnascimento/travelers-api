from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from database import db
from datetime import datetime
import uuid


class TokenBlocklist(db.Model):
    table_name = "token_blocklist"
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    jti: Mapped[str] = mapped_column(
        UUID(as_uuid=True), nullable=True, default=uuid.uuid4, index=True
    )
    created_at: Mapped[str] = mapped_column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )
