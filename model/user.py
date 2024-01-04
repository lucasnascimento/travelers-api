import uuid
from datetime import datetime

import bcrypt
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from database import db


class User(db.Model):
    __table_name__ = "user"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(db.String, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(db.String, nullable=False)
    inserted_at: Mapped[str] = mapped_column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[str] = mapped_column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __init__(self, email, password) -> None:
        super().__init__()
        self.email = email
        self.hash_password(password)

    def hash_password(self, password):
        password_bytes = password.encode("utf-8")
        hashed_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        self.hashed_password = hashed_bytes.decode("utf-8")

    def check_password(self, password):
        password_bytes = password.encode("utf-8")
        hashed_bytes = self.hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_bytes)
