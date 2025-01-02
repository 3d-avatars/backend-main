from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import TEXT

from src.data.database.tables import BaseTable


class UserTable(BaseTable):
    __tablename__ = "user"

    email = Column(
        "email",
        TEXT,
        nullable=False,
        unique=True,
        doc="User's email"
    )

    hashed_password = Column(
        "hashed_password",
        TEXT,
        nullable=False,
        unique=True,
        doc="User's hashed password"
    )
