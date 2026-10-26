from sqlalchemy import Column, Integer, String
from database.database import Base


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(Integer, nullable=False)

    complaint_type = Column(String, nullable=False)
    description = Column(String, nullable=False)

    complaint_date = Column(String, nullable=False)

    status = Column(
        String,
        nullable=False,
        default="Pending"
    )