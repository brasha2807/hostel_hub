from sqlalchemy import Column, Integer, String
from database.database import Base


class Visitor(Base):
    __tablename__ = "visitors"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(Integer, nullable=False)

    visitor_name = Column(String, nullable=False)
    relation = Column(String, nullable=False)
    phone = Column(String, nullable=False)

    visit_date = Column(String, nullable=False)

    in_time = Column(String, nullable=False)
    out_time = Column(String, nullable=True)

    purpose = Column(String, nullable=True)