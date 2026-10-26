from sqlalchemy import Column, Integer, String
from database.database import Base


class Notice(Base):
    __tablename__ = "notices"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)
    description = Column(String, nullable=False)

    notice_date = Column(String, nullable=False)

    notice_type = Column(String, nullable=False)