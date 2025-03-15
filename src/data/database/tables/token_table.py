from sqlalchemy import Column, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import TEXT

from src.data.database.tables import BaseTable
from src.domain.entities import TokenType


class TokenTable(BaseTable):
    __tablename__ = "user_info"

    token = Column(
        "token",
        TEXT,
        nullable=False,
        doc="Access or refresh token value"
    )

    type = Column(
        "type",
        Enum(TokenType),
        nullable=False,
        default=TokenType.ACCESS,
        doc="Type of token"
    )

    user_id = Column(
        "user_id",
        ForeignKey("user.id"),
        nullable=False,
        doc="User for whom this token was created"
    )
