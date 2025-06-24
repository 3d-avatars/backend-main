from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import BIGINT
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

DeclarativeBase = declarative_base()


class BaseTable(DeclarativeBase):
    __abstract__ = True

    id = Column(
        BIGINT,
        primary_key=True,
        autoincrement=True,
        nullable=False,
        doc="Table id",
    )

    dt_created = Column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        nullable=False,
        doc="Date and time of create (type TIMESTAMP)",
    )

    dt_updated = Column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False,
        doc="Date and time of last update (type TIMESTAMP)",
    )

    def __repr__(self):
        columns = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        return f'<{self.__tablename__}: {", ".join(map(lambda x: f"{x[0]}={x[1]}", columns.items()))}>'
